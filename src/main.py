import os
import argparse
from datetime import datetime, timedelta
import logging
import re
from dotenv import load_dotenv
from bsky_api import login, DID_resolve
from ollama_gen import generate_post, get_account_posts
from time_utils import calculate_refresh_interval, calculate_next_refresh, sleep_until_next_refresh

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

# Set up console logging
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

# Rate limiting tracking
class RateLimiter:
    """Track posting rate to comply with Bluesky API limits."""
    def __init__(self):
        # Bluesky limits: 5000 points/hour, 35000 points/day
        # Creating a post = 3 points
        # We can create max 1666 records/hour and 11666 records/day
        self.hourly_posts = []
        self.daily_posts = []
        self.max_hourly_posts = 1600  # Keep some buffer
        self.max_daily_posts = 11000   # Keep some buffer
    
    def can_post(self):
        """Check if we can post without exceeding rate limits."""
        now = datetime.now()
        
        # Clean up old timestamps
        one_hour_ago = now - timedelta(hours=1)
        one_day_ago = now - timedelta(days=1)
        
        self.hourly_posts = [ts for ts in self.hourly_posts if ts > one_hour_ago]
        self.daily_posts = [ts for ts in self.daily_posts if ts > one_day_ago]
        
        # Check limits
        if len(self.hourly_posts) >= self.max_hourly_posts:
            logging.warning(f"Hourly rate limit reached: {len(self.hourly_posts)}/{self.max_hourly_posts}")
            return False, "hourly"
        
        if len(self.daily_posts) >= self.max_daily_posts:
            logging.warning(f"Daily rate limit reached: {len(self.daily_posts)}/{self.max_daily_posts}")
            return False, "daily"
        
        return True, None
    
    def record_post(self):
        """Record a successful post."""
        now = datetime.now()
        self.hourly_posts.append(now)
        self.daily_posts.append(now)
        logging.info(f"Rate limit status: {len(self.hourly_posts)} posts this hour, {len(self.daily_posts)} posts today")
    
    def get_wait_time(self, limit_type):
        """Calculate how long to wait before posting again."""
        if limit_type == "hourly" and self.hourly_posts:
            oldest_post = min(self.hourly_posts)
            wait_until = oldest_post + timedelta(hours=1)
            return wait_until
        elif limit_type == "daily" and self.daily_posts:
            oldest_post = min(self.daily_posts)
            wait_until = oldest_post + timedelta(days=1)
            return wait_until
        return None

def validate_content(text, char_limit=300):
    """
    Validate generated content before posting.
    
    Args:
        text: The generated text to validate
        char_limit: Maximum character limit
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not text or not text.strip():
        return False, "Generated content is empty"
    
    if len(text) > char_limit:
        return False, f"Content exceeds character limit ({len(text)}/{char_limit})"
    
    # Check for repetitive content (same phrase repeated multiple times)
    words = text.lower().split()
    if len(words) > 5:
        # Check for repeated sequences
        for i in range(len(words) - 2):
            phrase = ' '.join(words[i:i+3])
            if text.lower().count(phrase) > 2:
                return False, "Content contains repetitive patterns"
    
    # Check for placeholder text
    placeholders = [
        'lorem ipsum', '[placeholder]', 'todo', 'xxx', 'test test',
        'sample text', 'example post', 'generated text'
    ]
    text_lower = text.lower()
    for placeholder in placeholders:
        if placeholder in text_lower:
            return False, f"Content contains placeholder text: {placeholder}"
    
    # Check for excessive punctuation
    if text.count('!') > 3 or text.count('?') > 3:
        return False, "Content contains excessive punctuation"
    
    # Check for all caps (excluding short posts)
    if len(text) > 20 and text.isupper():
        return False, "Content is all caps"
    
    # Check for URLs that might be spam
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)
    if len(urls) > 2:
        return False, "Content contains too many URLs"
    
    # Check minimum length (avoid too short posts)
    if len(text.strip()) < 10:
        return False, "Content is too short (minimum 10 characters)"
    
    return True, None

def main():
    parser = argparse.ArgumentParser(description="Generate and post Bluesky content using Ollama")
    parser.add_argument("-m", "--model", help="Ollama model to use", default=None)
    parser.add_argument("--dry-run", action="store_true", 
                       help="Generate posts without actually posting them")
    args = parser.parse_args()

    logging.info("=" * 80)
    logging.info("NEW EXECUTION OF BLUESKY-OLLAMA BOT")
    if args.dry_run:
        logging.info("RUNNING IN DRY-RUN MODE (no posts will be published)")
    logging.info("=" * 80)
    
    print("\n🤖 Bluesky Ollama Bot started.\n")
    if args.dry_run:
        print("⚠️  DRY-RUN MODE: Posts will be generated but NOT published\n")

    # Load environment variables
    load_dotenv()

    source_handle = os.getenv("SOURCE_HANDLE")
    destination_handle = os.getenv("DESTINATION_HANDLE")
    char_limit = int(os.getenv("CHAR_LIMIT", 280))
    model_name = args.model or os.getenv("OLLAMA_MODEL", "llama3.2")

    # Log environment variable loading
    logging.debug(
        "Loaded environment variables: SOURCE_HANDLE=%s, DESTINATION_HANDLE=%s, CHAR_LIMIT=%d, MODEL=%s",
        source_handle, destination_handle, char_limit, model_name
    )

    # Validate required environment variables
    if not source_handle or not destination_handle:
        logging.error("SOURCE_HANDLE and DESTINATION_HANDLE must be set in .env file")
        print("❌ Error: SOURCE_HANDLE and DESTINATION_HANDLE must be set in .env file")
        return 1

    # Initialize rate limiter
    rate_limiter = RateLimiter()

    # Login to source client and resolve DID
    try:
        print("🔐 Logging into source account...")
        source_client = login("SOURCE_HANDLE", "SRC_APP_PASS")
        logging.info("Successfully logged in to source account.")
        print("✅ Successfully logged in to source account.")
        
        source_did_package = DID_resolve(source_handle)
        source_did = source_did_package['did']
        logging.info("Resolved source DID: %s", source_did)

        if not args.dry_run:
            print("🔐 Logging into destination account...")
            destination_client = login("DESTINATION_HANDLE", "DST_APP_PASS")
            logging.info("Successfully logged in to destination account.")
            print("✅ Successfully logged in to destination account.\n")
        else:
            destination_client = None
            print("⏭️  Skipping destination account login (dry-run mode)\n")

    except Exception as e:
        logging.exception("An error occurred during setup: %s", e)
        print(f"❌ Setup error: {e}")
        return 1

    def generate_and_post():
        """Generate a post using Ollama and post it to Bluesky."""
        try:
            print("📥 Fetching posts from source account...")
            source_posts = get_account_posts(source_client, source_did)
            logging.info(f"Fetched {len(source_posts)} posts from source account.")
            print(f"✅ Fetched {len(source_posts)} posts from source account.")

            if not source_posts:
                logging.warning("No posts retrieved from source account. Skipping generation.")
                print("⚠️  No posts available. Skipping this cycle.")
                return

            print(f"🤖 Generating post using {model_name}...")
            generated_text = generate_post(source_posts, model_name, char_limit)
            logging.info(f"Generated text: {generated_text}")
            print(f"\n📝 Generated post:\n{'-' * 40}\n{generated_text}\n{'-' * 40}\n")

            # Validate content
            print("🔍 Validating generated content...")
            is_valid, error_message = validate_content(generated_text, char_limit)
            
            if not is_valid:
                logging.warning(f"Content validation failed: {error_message}")
                print(f"⚠️  Content validation failed: {error_message}")
                print("⏭️  Skipping this post. Will try again next cycle.\n")
                return
            
            print("✅ Content validation passed")

            # Skip posting in dry-run mode
            if args.dry_run:
                print("💭 DRY-RUN MODE: Post would be published here (but wasn't)\n")
                return

            # Check rate limits
            can_post, limit_type = rate_limiter.can_post()
            if not can_post:
                wait_until = rate_limiter.get_wait_time(limit_type)
                print(f"⏳ {limit_type.capitalize()} rate limit reached. Next post available at: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
                logging.warning(f"Rate limit reached: {limit_type}. Waiting until {wait_until}")
                return

            print("📤 Posting to destination account...")
            response = destination_client.send_post(
                text=generated_text,
                langs=['en']
            )
            post_link = response['uri']
            
            # Record the post for rate limiting
            rate_limiter.record_post()
            
            logging.info("Posted to destination Bluesky account successfully: %s", post_link)
            print(f"✅ Posted successfully: {post_link}\n")

        except Exception as e:
            logging.error("Error in generate_and_post: %s", e)
            print(f"❌ Error: {e}")

    # Main loop
    try:
        iteration = 0
        while True:
            iteration += 1
            print(f"{'=' * 60}")
            print(f"Iteration {iteration}")
            print(f"{'=' * 60}")
            
            current_time = datetime.now()
            refresh_interval = calculate_refresh_interval()
            next_refresh = calculate_next_refresh(current_time, refresh_interval)

            logging.debug(
                "Current time: %s, Refresh interval: %s seconds, Next refresh: %s",
                current_time, refresh_interval, next_refresh
            )

            # Generate and post
            generate_and_post()

            # Sleep until next iteration
            print(f"⏰ Next post scheduled for {next_refresh.strftime('%Y-%m-%d %H:%M:%S')}")
            sleep_until_next_refresh(next_refresh)
            print()

    except KeyboardInterrupt:
        logging.info("Exiting on user interrupt.")
        print("\n\n👋 Exiting on user interrupt. Goodbye!")
        return 0
    except Exception as e:
        logging.exception("Unexpected error in main loop: %s", e)
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
