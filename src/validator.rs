use regex::Regex;

pub fn validate_content(text: &str, char_limit: usize) -> (bool, Option<String>) {
    if text.trim().is_empty() {
        return (false, Some("Generated content is empty".to_string()));
    }

    if text.len() > char_limit {
        return (false, Some(format!("Content exceeds character limit ({}/{})", text.len(), char_limit)));
    }

    let words: Vec<&str> = text.split_whitespace().collect();
    if words.len() > 5 {
        for i in 0..words.len() - 2 {
            let phrase = format!("{} {} {}", words[i], words[i+1], words[i+2]).to_lowercase();
            // Count occurrences of phrase in lowercase text
            let count = text.to_lowercase().matches(&phrase).count();
            if count > 2 {
                return (false, Some("Content contains repetitive patterns".to_string()));
            }
        }
    }

    let placeholders = [
        "lorem ipsum", "[placeholder]", "todo", "xxx", "test test",
        "sample text", "example post", "generated text"
    ];
    let text_lower = text.to_lowercase();
    for placeholder in placeholders {
        if text_lower.contains(placeholder) {
            return (false, Some(format!("Content contains placeholder text: {}", placeholder)));
        }
    }

    if text.chars().filter(|&c| c == '!').count() > 3 || text.chars().filter(|&c| c == '?').count() > 3 {
        return (false, Some("Content contains excessive punctuation".to_string()));
    }

    if text.len() > 20 && text.chars().all(|c| !c.is_alphabetic() || c.is_uppercase()) {
        return (false, Some("Content is all caps".to_string()));
    }

    let url_regex = Regex::new(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+").unwrap();
    if url_regex.find_iter(text).count() > 2 {
        return (false, Some("Content contains too many URLs".to_string()));
    }

    if text.trim().len() < 10 {
        return (false, Some("Content is too short (minimum 10 characters)".to_string()));
    }

    (true, None)
}
