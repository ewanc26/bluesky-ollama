# Bluesky Ollama Bot

An AI-powered Bluesky bot that uses Ollama to generate posts based on content from a source account. This project combines the Bluesky API integration from [bluesky-markov](https://github.com/ewanc26/bluesky-markov) with the Ollama LLM capabilities from [llm-analyser](https://github.com/ewanc26/llm-analyser).

## Features

- Fetches posts from a specified source Bluesky account
- Uses Ollama (local LLM) to generate new posts in a similar style
- Automatically posts generated content to a destination account
- Configurable posting intervals with randomization
- Comprehensive logging for debugging and monitoring
- Content cleaning and preprocessing
- **Rate limiting** to comply with Bluesky API limits (1666 posts/hour, 11666 posts/day)
- **Content validation** to prevent spam, placeholder text, and low-quality posts
- **Dry-run mode** for testing without publishing posts

## Requirements

- Python 3.x
- Ollama (installed locally)
- Required Python libraries:
  - `atproto` - Bluesky API client
  - `python-dotenv` - Environment variable management
  - `ollama` - Ollama Python client

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ewanc26/bluesky-ollama.git
   cd bluesky-ollama
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install and set up Ollama:**

   - Download and install Ollama from [ollama.com](https://ollama.com/)
   - Pull a model (default is llama3.2):
     ```bash
     ollama pull llama3.2
     ```

5. **Configure environment variables:**

   Create a `.env` file in the root directory:

   ```plaintext
   SOURCE_HANDLE=your_source_handle.bsky.social
   DESTINATION_HANDLE=your_destination_handle.bsky.social
   CHAR_LIMIT=280
   SRC_APP_PASS=your_source_app_password
   DST_APP_PASS=your_destination_app_password
   BSKY_HOST_URL=https://bsky.social
   OLLAMA_MODEL=llama3.2
   ```

   **Important:** Use app-specific passwords from your Bluesky account settings, not your main password.

## Usage

Run the bot with:

```bash
python src/main.py
```

The bot will:
1. Log into both source and destination accounts
2. Fetch recent posts from the source account
3. Generate a new post using Ollama based on the source content
4. Post the generated content to the destination account
5. Wait a random interval (30 minutes to 3 hours) before repeating

### Command Line Options

```bash
python src/main.py [-m MODEL_NAME] [--dry-run]
```

- `-m, --model`: Specify the Ollama model to use (default: llama3.2)
- `--dry-run`: Generate posts without actually posting them (useful for testing)

#### Examples

```bash
# Run normally
python src/main.py

# Test with dry-run mode (no posts will be published)
python src/main.py --dry-run

# Use a different model
python src/main.py -m llama3.3

# Combine options
python src/main.py --dry-run -m mistral
```

## Configuration

### Environment Variables

- `SOURCE_HANDLE`: The Bluesky handle to fetch posts from
- `DESTINATION_HANDLE`: The Bluesky handle to post generated content to
- `SRC_APP_PASS`: App password for source account
- `DST_APP_PASS`: App password for destination account
- `CHAR_LIMIT`: Maximum character limit for generated posts (default: 280)
- `BSKY_HOST_URL`: Bluesky host URL (default: https://bsky.social)
- `OLLAMA_MODEL`: The Ollama model to use (default: llama3.2)

### Customizing the System Prompt

Edit the `generate_post()` function in `src/ollama_gen.py` to customize how the AI generates posts.

## Project Structure

```
bluesky-ollama/
├── log/
│   └── general.log           # Application logs
├── src/
│   ├── bsky_api.py          # Bluesky API interactions
│   ├── clean.py             # Content cleaning utilities
│   ├── ollama_gen.py        # Ollama-based post generation
│   ├── time_utils.py        # Timing and scheduling utilities
│   └── main.py              # Main application logic
├── .env                      # Environment variables (create this)
├── .gitignore               # Git ignore rules
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Logging

All logs are stored in `log/general.log` with detailed information about:
- Login attempts and successes
- Post fetching and generation
- API interactions
- Errors and exceptions

## How It Works

1. **Authentication**: The bot logs into both source and destination Bluesky accounts
2. **Content Retrieval**: Fetches recent posts from the source account using pagination
3. **Content Cleaning**: Removes HTML tags, mentions, special characters, and emojis
4. **AI Generation**: Uses Ollama to analyze the source posts and generate new content that mimics the style and topics
5. **Content Validation**: Checks generated content for:
   - Empty or too short posts
   - Character limit compliance
   - Repetitive patterns
   - Placeholder text
   - Excessive punctuation or URLs
   - Spam indicators
6. **Rate Limit Check**: Ensures posting complies with Bluesky's rate limits
7. **Posting**: Posts the generated content to the destination account (skipped in dry-run mode)
8. **Scheduling**: Waits a random interval before generating and posting again

## Safety and Ethics

- This bot is for educational and creative purposes
- Always respect Bluesky's terms of service and API guidelines
- Be transparent about automated accounts
- Consider adding a note in your destination account bio that it's an AI-powered bot
- Monitor the generated content to ensure it remains appropriate

### Rate Limiting

The bot automatically complies with Bluesky's rate limits:
- **5,000 points per hour** (creating a post = 3 points)
- **35,000 points per day**
- Maximum ~1,666 posts per hour
- Maximum ~11,666 posts per day

The bot tracks posting history and will automatically wait if limits are approached. A safety buffer is built in to prevent hitting the hard limits.

### Content Safety

The bot includes multiple layers of content validation:
- Rejects empty or placeholder content
- Prevents repetitive or spam-like posts
- Enforces minimum and maximum length requirements
- Filters excessive punctuation and URLs
- Ensures content meets Bluesky Community Guidelines

## Troubleshooting

### "Ollama not responding"
- Ensure Ollama is running: `ollama serve`
- Check if the model is pulled: `ollama list`

### "Login failed"
- Verify you're using app-specific passwords, not your main password
- Check that handles include the full domain (e.g., `user.bsky.social`)

### "No posts generated"
- Ensure the source account has posts to analyze
- Check the logs in `log/general.log` for detailed error information

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Credits

This project combines ideas from:
- [bluesky-markov](https://github.com/ewanc26/bluesky-markov) - Bluesky API integration
- [llm-analyser](https://github.com/ewanc26/llm-analyser) - Ollama integration

## Disclaimer

This bot generates content using AI. While efforts are made to keep content appropriate, the generated posts may not always be perfect. Monitor the bot's output regularly.
