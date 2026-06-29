use bsky_sdk::BskyAgent;
use bsky_sdk::agent::config::Config;
use atrium_api::types::string::Did;
use anyhow::{Result, anyhow, Context};
use std::env;
use tracing::{info, debug};

pub async fn login(handle_env_var: &str, app_pass_env_var: &str) -> Result<BskyAgent> {
    let handle = env::var(handle_env_var).with_context(|| format!("Missing env var {}", handle_env_var))?;
    let app_pass = env::var(app_pass_env_var).with_context(|| format!("Missing env var {}", app_pass_env_var))?;
    let host_url = env::var("BSKY_HOST_URL").unwrap_or_else(|_| "https://bsky.social".to_string());

    debug!("Attempting to log in with handle: {}", handle);
    
    let agent = BskyAgent::builder()
        .config(Config {
            endpoint: host_url,
            ..Default::default()
        })
        .build()
        .await?;

    agent.login(handle.clone(), app_pass).await?;

    info!("Login successful for handle: {}", handle);
    Ok(agent)
}

pub async fn resolve_did(agent: &BskyAgent, handle: &str) -> Result<Did> {
    debug!("Resolving DID for handle: {}", handle);
    let output = agent.api.com.atproto.identity.resolve_handle(
        atrium_api::com::atproto::identity::resolve_handle::ParametersData {
            handle: handle.parse().map_err(|e| anyhow!("{:?}", e))?,
        }.into()
    ).await?;
    
    let did = output.data.did;
    debug!("Resolved DID: {}", did.as_str());
    Ok(did)
}

pub async fn retrieve_posts(agent: &BskyAgent, did: Did, limit: u8) -> Result<Vec<atrium_api::app::bsky::feed::post::Record>> {
    let mut post_list = Vec::new();
    
    let output = agent.api.com.atproto.repo.list_records(
        atrium_api::com::atproto::repo::list_records::ParametersData {
            collection: "app.bsky.feed.post".parse().map_err(|e| anyhow!("{:?}", e))?,
            repo: did.as_str().parse().map_err(|e| anyhow!("{:?}", e))?,
            cursor: None,
            limit: Some(limit.try_into().map_err(|e| anyhow!("{:?}", e))?),
            reverse: None,
        }.into()
    ).await?;

    for record in output.data.records {
        if let Ok(post_record) = serde_json::from_value::<atrium_api::app::bsky::feed::post::Record>(serde_json::to_value(&record.value)?) {
            post_list.push(post_record);
        }
    }

    Ok(post_list)
}
