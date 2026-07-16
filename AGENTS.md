# AGENTS.md

Guidance for agents working on this dual Python/Rust Bluesky-to-Ollama posting bot.

## Two implementations

- The README and Nix shell describe the Python path: `python src/main.py`, dependencies in `requirements.txt`, helpers in `bsky_api.py`, `ollama_gen.py`, `clean.py`, and `time_utils.py`.
- `Cargo.toml` and the `.rs` siblings implement a separate Rust binary with similar behaviour. Changes are not shared automatically; state which implementation is in scope and keep common safety fixes aligned where practical.
- Python `main.py` defines its own validator and rate limiter; `content_validator.py` and `rate_limiter.py` are currently unused alternatives. Rust uses `validator.rs` and `rate_limiter.rs`.
- `example.env` contains the shared source/destination credentials, service, model, and limit contract. Paths such as `log/` are relative to the working directory.
- A large Rust `target/` tree was historically tracked. It is generated output, not source; do not restore or mix its cleanup with an unrelated change.

## Current behaviour and failure modes

- `--dry-run` suppresses destination login and posting, but still logs into the source account, resolves identity, fetches posts, sends their cleaned content to local Ollama, and writes logs. It is read-only toward Bluesky, not offline or privacy-neutral.
- Python paginates until the source collection ends; Rust fetches only the first 100 records. Neither filters replies or sensitive/private-context semantics beyond reading public post records.
- Python Ollama failures are converted into strings such as `Error generating post: ...`. The inline validator does not reliably reject error text, so a generation failure can become a real post. Rust returns generation errors, but its empty-corpus fallback (`No content available to generate from.`) can pass validation and be posted.
- Both generators log full cleaned/generated text. Treat source content as potentially sensitive and do not enable debug logs or publish captured prompts casually.
- Rust uses byte length for `CHAR_LIMIT` and calls `String::truncate`; Unicode crossing a byte boundary can panic. Python counts Unicode code points, while Bluesky rich-text limits/facets are protocol-specific. Make limit handling explicitly UTF-8 safe and test actual record acceptance.
- No implementation checks generated output against recent destination posts, provenance, factuality, impersonation risk, or repeated posts across restarts. The in-memory rate counters reset on every process start and are far looser than the 30-minute-to-3-hour scheduler needs.
- Ollama calls have no explicit timeout or cancellation. Fetch/generation failures still lead to the ordinary random sleep; process shutdown is only explicitly friendly in Python's `KeyboardInterrupt` path.
- Python `bsky_api.login` calls `quit(1)` on failure, bypassing ordinary exception handling, and DID resolution returns `None` on failure. Avoid this control flow in reusable helpers.
- Daily Rust log rolling has no retention; Python uses a single growing `log/general.log`. Never log credentials, tokens, authorization headers, or raw session objects.

## Validation

For Python, create a disposable virtual environment, install `requirements.txt`, and run syntax/import checks plus a real test suite if added; there is currently no checked-in `test_validation.py` or automated Python test. For Rust run `cargo fmt --check`, `cargo clippy --all-targets --all-features`, `cargo test`, and `cargo build --release`; there are currently no Rust tests. Add mocked tests for empty source data, Ollama timeout/error strings, Unicode boundaries, invalid `CHAR_LIMIT`, duplicate output, rate-counter reset, and shutdown. Never use a routine test to publish; even `--dry-run` requires explicit source-account and prompt-content authorization.
