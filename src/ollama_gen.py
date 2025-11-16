import logging
import os
import ollama
from clean import clean_content, get_post_text
from bsky_api import retrieve_posts

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

def get_account_posts(client, client_did, limit=100):
    """Fetch and clean posts from a Bluesky account."""
    posts = retrieve_posts(client, client_did, limit)

    # Debugging: Print structure of the first post
    if posts:
        logging.debug("First post structure: %s", posts[0])

    # Ensure we are accessing the text correctly
    cleaned_posts = []
    for post in posts:
        text = get_post_text(post)
        if text:
            cleaned_text = clean_content(text)
            if cleaned_text.strip():  # Only add non-empty posts
                cleaned_posts.append(cleaned_text)

    logging.info(f"Retrieved and cleaned {len(cleaned_posts)} posts from account.")
    return cleaned_posts

def generate_post(posts, model_name, char_limit):
    """
    Generate a new post using Ollama based on the provided posts.
    
    Args:
        posts: List of cleaned post texts to use as context
        model_name: Name of the Ollama model to use
        char_limit: Maximum character limit for the generated post
    
    Returns:
        Generated post text
    """
    try:
        client = ollama.Client()

        # Prepare context from posts
        if not posts:
            logging.warning("No posts provided for generation")
            return "No content available to generate from."

        # Sample posts to include in context (limit to avoid token limits)
        sample_size = min(20, len(posts))
        sample_posts = posts[:sample_size]
        posts_context = "\n\n".join([f"- {post}" for post in sample_posts])

        # Create prompt for Ollama
        prompt = f"""You are a creative social media post generator. Based on the following posts from a Bluesky account, generate a single new post that matches the style, tone, and topics of the original content.

Example posts from the account:
{posts_context}

Guidelines:
- Match the writing style, tone, and personality of the original posts
- Keep it concise and engaging
- Do not exceed {char_limit} characters
- Do not include hashtags unless they were common in the examples
- Make it feel natural and authentic to the account's voice
- Focus on similar topics or themes
- DO NOT use quotation marks or indicate this is a generated post

Generate only the post text, nothing else:"""

        logging.debug(f"Generating post with model: {model_name}")
        
        # Generate using Ollama
        response = client.generate(model=model_name, prompt=prompt)
        generated_text = response['response'].strip()

        # Remove any quotation marks that might have been added
        generated_text = generated_text.strip('"').strip("'")

        # Ensure we don't exceed character limit
        if len(generated_text) > char_limit:
            # Try to cut at a sentence or word boundary
            generated_text = generated_text[:char_limit]
            last_period = generated_text.rfind('.')
            last_space = generated_text.rfind(' ')
            
            if last_period > char_limit * 0.7:  # If we can cut at a sentence
                generated_text = generated_text[:last_period + 1]
            elif last_space > char_limit * 0.8:  # If we can cut at a word
                generated_text = generated_text[:last_space]
            # Otherwise just hard cut

        logging.info(f"Generated post ({len(generated_text)} chars): {generated_text}")
        return generated_text

    except Exception as e:
        logging.error(f"Error generating post with Ollama: {e}")
        return f"Error generating post: {str(e)}"
