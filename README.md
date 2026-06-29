# Bluesky Ollama Bot

Posts AI-generated content to Bluesky using Ollama. Combines the Bluesky API from [bluesky-markov](https://github.com/ewanc26/bluesky-markov) with Ollama LLM from [llm-analyser](https://github.com/ewanc26/llm-analyser).

> Also available on [Tangled](https://tangled.org/ewancroft.uk/bluesky-ollama)

## Requirements

- Python 3.x
- [Ollama](https://ollama.com/)
- `atproto`, `python-dotenv`, `ollama` (in `requirements.txt`)

## Install

```bash
git clone https://github.com/ewanc26/bluesky-ollama.git
cd bluesky-ollama
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
ollama pull llama3.2
```

Create `.env`:

```plaintext
SOURCE_HANDLE=your_source_handle.bsky.social
DESTINATION_HANDLE=your_destination_handle.bsky.social
CHAR_LIMIT=280
SRC_APP_PASS=your_source_app_password
DST_APP_PASS=your_destination_app_password
BSKY_HOST_URL=https://bsky.social
OLLAMA_MODEL=llama3.2
```

Use app passwords, not your main password.

## Usage

```bash
python src/main.py
```

Does this on a loop:

1. Logs into both accounts
2. Fetches recent posts from the source
3. Generates a new post with Ollama
4. Posts to the destination
5. Waits 30 min – 3 hours, repeats

### Options

```bash
python src/main.py [-m MODEL_NAME] [--dry-run]
```

- `-m` — Model to use (default: llama3.2)
- `--dry-run` — Generate without posting

## Project layout

```
├── log/general.log        # Logs
├── src/
│   ├── bsky_api.py        # Bluesky API
│   ├── clean.py           # Content cleaning
│   ├── ollama_gen.py      # Ollama generation
│   ├── time_utils.py      # Timing
│   └── main.py            # Entry point
├── .env
├── requirements.txt
└── README.md
```

## Troubleshooting

**Ollama not responding** — `ollama serve`, check `ollama list`

**Login failed** — Make sure you're using app passwords and full handles (e.g. `user.bsky.social`)

**No posts generated** — Check the source account has posts and look at `log/general.log`

## Licence

AGPLv3 — see [LICENCE](LICENCE)
