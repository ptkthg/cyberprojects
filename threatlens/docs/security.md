# Security

- API keys are loaded from `st.secrets` or `.env`.
- Keys are never persisted in SQLite.
- `.streamlit/secrets.toml` must never be committed.
- ThreatLens does not perform automatic blocking actions.
- Avoid sending sensitive internal context to external OSINT APIs.

- OPENAI_API_KEY é lida de secrets/.env e nunca exibida.
- O payload enviado à OpenAI é sanitizado e limitado.
- O app não executa bloqueio automático.
