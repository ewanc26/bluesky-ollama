# Contributing to the Bluesky Ollama bot

A bot that posts AI-generated content to Bluesky using Ollama, combining the Bluesky API from bluesky-markov with Ollama generation from llm-analyser. Thanks for wanting to help!

## Getting started

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
ollama pull llama3.2
python src/main.py --dry-run   # generate without posting
```

Credentials live in `.env` (never committed): handles, app passwords, host URL, model name.

## Notes for this project

- **App passwords only, never main passwords** — keep it that way in docs and code.
- `--dry-run` is the safe way to test generation changes; use it in your PR description.
- `log/general.log` is the diagnostic surface: if you add a failure mode, make sure it logs something findable.
- The loop (log in → fetch source posts → generate → post → wait 30 min–3 h) is the whole program; keep the modules in `src/` small and single-purpose.

## Before opening a PR

- The documented build and tests pass, and you ran them yourself.
- Conventional commits; one focused PR per change.
- AI-assisted PRs are welcome; stand behind every line.

## Licence

AGPL v3 (see [LICENCE](LICENCE)). Contributions are accepted under the same terms. Contributions are accepted under the same terms.