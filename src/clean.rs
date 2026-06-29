use regex::Regex;
use html_escape::decode_html_entities;
use tracing::debug;

pub fn clean_content(content: &str) -> String {
    debug!("Original content: {}", content);

    // Remove HTML tags
    let re_html = Regex::new(r"<[^<]+?>").unwrap();
    let cleaned = re_html.replace_all(content, "");

    // Decode HTML entities
    let cleaned = decode_html_entities(&cleaned);

    // Remove usernames based on domain patterns
    let domain_regex = Regex::new(r"@\w+\.([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?").unwrap();
    let cleaned = domain_regex.replace_all(&cleaned, "");

    // Remove special characters
    let re_special = Regex::new(r"[^\w\s.,!?;:]").unwrap();
    let cleaned = re_special.replace_all(&cleaned, "");

    // Remove words enclosed with colons
    let re_colons = Regex::new(r":\w+:").unwrap();
    let cleaned = re_colons.replace_all(&cleaned, "");

    cleaned.to_string().trim().to_string()
}

pub fn get_post_text(record: &atrium_api::app::bsky::feed::post::Record) -> String {
    record.text.clone()
}
