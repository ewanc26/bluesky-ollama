# AGENTS.md

Guidance for agents working on the Rust bot that generates Bluesky posts with a local Ollama model.

## Structure and contracts

- `src/` owns CLI/config validation, source-content collection, prompt construction, Ollama calls, output cleanup, Bluesky publication, and scheduling.
- `example.env` documents configuration; real `.env` files are secrets.
- `test_validation.py` covers configuration/input validation alongside Rust code. `target/` is generated build output even if present locally.

## Invariants

- Treat model output as untrusted: strip unwanted wrappers, enforce character limits, reject empty/duplicate output, and never execute generated content.
- Keep Ollama endpoints local/configurable and apply timeouts. A model outage must not cause a rapid retry or a fabricated post success.
- Preserve separation between prompt source data and destination credentials.
- Validate delay ranges and schedule exactly one next attempt.
- Never log app passwords, tokens, authorization headers, or sensitive source material.
- Do not include `target/`, logs, `.env`, or model artifacts in commits.

## Validation

Run `cargo fmt --check`, `cargo clippy --all-targets --all-features`, `cargo test`, `python -m unittest test_validation.py` (or its documented runner), and `cargo build --release`. Mock Ollama, AT Protocol, randomness, and time for invalid config, model timeout, overlong output, empty output, post failure, retry bounds, and shutdown. Use a dedicated account for any intentional live post.
