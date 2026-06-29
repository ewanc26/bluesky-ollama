mod bsky;
mod clean;
mod ollama_gen;
mod rate_limiter;
mod time;
mod validator;

use anyhow::{Context, Result};
use atrium_api::app::bsky::feed::post::RecordData;
use atrium_api::types::string::Datetime;
use clap::Parser;
use chrono::Local;
use dotenvy::dotenv;
use std::env;
use std::path::Path;
use tracing::{debug, info, error, warn};
use tracing_subscriber::{fmt, prelude::*, EnvFilter};

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Ollama model to use
    #[arg(short, long)]
    model: Option<String>,

    /// Generate posts without actually posting them
    #[arg(long)]
    dry_run: bool,
}

#[tokio::main]
async fn main() -> Result<()> {
    let args = Args::parse();

    // Ensure the log directory exists
    let log_directory = "log";
    if !Path::new(log_directory).exists() {
        std::fs::create_dir_all(log_directory)?;
    }

    // Set up tracing
    let file_appender = tracing_appender::rolling::daily(log_directory, "general.log");
    let (non_blocking, _guard) = tracing_appender::non_blocking(file_appender);

    let filter = EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| EnvFilter::new("info"));

    tracing_subscriber::registry()
        .with(filter)
        .with(fmt::layer().with_writer(std::io::stdout))
        .with(fmt::layer().with_writer(non_blocking).with_ansi(false))
        .init();

    info!("NEW EXECUTION OF BLUESKY-OLLAMA BOT");
    if args.dry_run {
        info!("RUNNING IN DRY-RUN MODE (no posts will be published)");
    }
    println!("\n🤖 Bluesky Ollama Bot started.\n");

    // Load environment variables
    dotenv().ok();

    let source_handle = env::var("SOURCE_HANDLE").context("SOURCE_HANDLE not set")?;
    let destination_handle = env::var("DESTINATION_HANDLE").context("DESTINATION_HANDLE not set")?;
    let char_limit = env::var("CHAR_LIMIT")
        .unwrap_or_else(|_| "280".to_string())
        .parse::<usize>()
        .unwrap_or(280);
    let model_name = args.model.or_else(|| env::var("OLLAMA_MODEL").ok()).unwrap_or_else(|| "llama3.2".to_string());

    debug!(
        "Loaded environment variables: SOURCE_HANDLE={}, DESTINATION_HANDLE={}, CHAR_LIMIT={}, MODEL={}",
        source_handle, destination_handle, char_limit, model_name
    );

    let mut rate_limiter = rate_limiter::RateLimiter::new();

    // Login
    let source_agent = bsky::login("SOURCE_HANDLE", "SRC_APP_PASS").await?;
    let source_did = bsky::resolve_did(&source_agent, &source_handle).await?;
    info!("Resolved source DID: {}", source_did.as_str());

    let destination_agent = if !args.dry_run {
        let agent = bsky::login("DESTINATION_HANDLE", "DST_APP_PASS").await?;
        Some(agent)
    } else {
        None
    };

    let mut iteration = 0;
    loop {
        iteration += 1;
        println!("Iteration {}", iteration);

        let current_time = Local::now();
        let refresh_interval = time::calculate_refresh_interval();
        let next_refresh = time::calculate_next_refresh(current_time, refresh_interval);

        // Fetch and process
        match bsky::retrieve_posts(&source_agent, source_did.clone(), 100).await {
            Ok(posts) => {
                let cleaned_posts: Vec<String> = posts.iter().map(clean::get_post_text).map(|t| clean::clean_content(&t)).filter(|t| !t.is_empty()).collect();
                
                match ollama_gen::generate_post(cleaned_posts, model_name.clone(), char_limit).await {
                    Ok(generated_text) => {
                        let (is_valid, error_msg) = validator::validate_content(&generated_text, char_limit);
                        if is_valid {
                            if let Some(ref agent) = destination_agent {
                                let (can_post, limit_type) = rate_limiter.can_post();
                                if can_post {
                                    match agent.create_record(RecordData {
                                        text: generated_text.clone(),
                                        created_at: Datetime::now(),
                                        embed: None,
                                        entities: None,
                                        facets: None,
                                        labels: None,
                                        langs: Some(vec!["en".parse().unwrap()]),
                                        reply: None,
                                        tags: None,
                                    }).await {
                                        Ok(response) => {
                                            rate_limiter.record_post();
                                            info!("Posted successfully: {}", response.data.uri.as_str());
                                            println!("✅ Posted successfully: {}", response.data.uri.as_str());
                                        }
                                        Err(e) => error!("Failed to post: {:?}", e),
                                    }
                                } else {
                                    let wait_until = rate_limiter.get_wait_time(limit_type.unwrap()).unwrap();
                                    warn!("Rate limit reached. Waiting until {}", wait_until);
                                }
                            } else {
                                info!("DRY-RUN: Post would be: {}", generated_text);
                            }
                        } else {
                            warn!("Validation failed: {}", error_msg.unwrap());
                        }
                    }
                    Err(e) => error!("Ollama generation failed: {:?}", e),
                }
            }
            Err(e) => error!("Failed to retrieve posts: {:?}", e),
        }

        time::sleep_until_next_refresh(next_refresh).await;
    }
}
