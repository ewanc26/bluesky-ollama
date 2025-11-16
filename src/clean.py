from html import unescape
import re
import logging
import os

# Ensure the log directory exists
log_directory = 'log'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Set up logging to a file in the log directory
logging.basicConfig(
    filename=os.path.join(log_directory, 'general.log'), 
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def clean_content(content):
    """Clean and preprocess content from Bluesky posts."""
    logging.debug("Original content: %s", content)

    # Remove HTML tags
    cleaned_content = re.sub('<[^<]+?>', '', content)
    logging.debug("After removing HTML tags: %s", cleaned_content)

    # Decode HTML entities
    cleaned_content = unescape(cleaned_content)
    logging.debug("After decoding HTML entities: %s", cleaned_content)

    # Remove usernames based on domain patterns
    domain_regex = r'@\w+\.([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?'
    cleaned_content = re.sub(domain_regex, '', cleaned_content)
    logging.debug("After removing usernames: %s", cleaned_content)

    # Remove special characters but keep basic punctuation
    cleaned_content = re.sub(r'[^\w\s.,!?;:]', '', cleaned_content)
    logging.debug("After removing special characters: %s", cleaned_content)

    # Remove words enclosed with colons (emoji shortcodes)
    cleaned_content = re.sub(r':\w+:', '', cleaned_content)
    logging.debug("After removing words enclosed with colons: %s", cleaned_content)

    # Remove extra whitespace
    cleaned_content = ' '.join(cleaned_content.split())
    logging.debug("Final cleaned content: %s", cleaned_content)

    return cleaned_content

def get_post_text(post):
    """Extract text from a post object."""
    if hasattr(post, 'value') and hasattr(post.value, 'text'):
        return post.value.text
    elif hasattr(post, 'text'):
        return post.text
    else:
        logging.warning("Post does not have 'value' or 'text' attribute: %s", post)
        return ""
