use ollama_rs::Ollama;
use ollama_rs::generation::completion::request::GenerationRequest;
use tracing::{info, debug, warn};
use anyhow::Result;

pub async fn generate_post(posts: Vec<String>, model_name: String, char_limit: usize) -> Result<String> {
    let ollama = Ollama::default();

    if posts.is_empty() {
        warn!("No posts provided for generation");
        return Ok("No content available to generate from.".to_string());
    }

    let sample_size = std::cmp::min(20, posts.len());
    let sample_posts = &posts[..sample_size];
    let posts_context = sample_posts.iter().map(|p| format!("- {}", p)).collect::<Vec<_>>().join("\n\n");

    let prompt = format!(
        "You are a creative social media post generator. Based on the following posts from a Bluesky account, generate a single new post that matches the style, tone, and topics of the original content.\n\nExample posts from the account:\n{}\n\nGuidelines:\n- Match the writing style, tone, and personality of the original posts\n- Keep it concise and engaging\n- Do not exceed {} characters\n- Do not include hashtags unless they were common in the examples\n- Make it feel natural and authentic to the account's voice\n- Focus on similar topics or themes\n- DO NOT use quotation marks or indicate this is a generated post\n\nGenerate only the post text, nothing else:",
        posts_context, char_limit
    );

    debug!("Generating post with model: {}", model_name);

    let res = ollama.generate(GenerationRequest::new(model_name, prompt)).await?;
    let mut generated_text = res.response.trim().to_string();

    // Remove any quotation marks
    generated_text = generated_text.trim_matches(|c| c == '"' || c == '\'').to_string();

    // Ensure we don't exceed character limit
    if generated_text.len() > char_limit {
        generated_text.truncate(char_limit);
        if let Some(last_period) = generated_text.rfind('.') {
            if last_period > (char_limit as f32 * 0.7) as usize {
                generated_text.truncate(last_period + 1);
            }
        } else if let Some(last_space) = generated_text.rfind(' ') {
            if last_space > (char_limit as f32 * 0.8) as usize {
                generated_text.truncate(last_space);
            }
        }
    }

    info!("Generated post ({} chars): {}", generated_text.len(), generated_text);
    Ok(generated_text)
}
