# Security

- API keys are loaded from `st.secrets` or `.env`.
- Keys are never persisted in SQLite.
- `.streamlit/secrets.toml` must never be committed.
- ThreatLens does not perform automatic blocking actions.
- Avoid sending sensitive internal context to external OSINT APIs.
