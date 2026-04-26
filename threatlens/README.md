# ThreatLens

![ThreatLens Banner](assets/dashboard_banner.svg)

## IOC Enrichment & Triage Platform

**Desenvolvido por Patrick Santos**

ThreatLens é uma plataforma de enriquecimento, triagem e documentação de indicadores de ameaça para Blue Team/SOC, com foco em análise rápida, padronizada e rastreável.

> O ThreatLens apoia a decisão do analista, mas não executa bloqueios automáticos.

## Funcionalidades
- Painel SOC com KPIs, saúde das fontes e quick actions.
- Análise de IOC com score, risco, confiança, breakdown, veredito por fonte, recomendação e KQL.
- Histórico investigativo clicável com timeline.
- Central de Casos com atualização de status/decisão/notas.
- Análise em lote (CSV/TXT) com preview, progresso e exportação CSV/JSON.
- Detalhe da análise com reanálise e exportação.
- Trilha de auditoria em SQLite.
- Modo demo com dados realistas para validação sem API key.
- Launcher desktop (Tkinter) + script `abrir_threatlens.bat`.

- Cards do painel são clicáveis e aplicam filtros/navegação contextual.
- Análise assistida por IA via OpenAI (opcional).

## Screenshots sugeridos
- Dashboard (Painel)
- Analisar IOC
- Histórico timeline
- Casos
- Detalhe da análise
- Launcher

## Instalação
```bash
cd threatlens
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Configuração de chaves
`.streamlit/secrets.toml`
```toml
VIRUSTOTAL_API_KEY = ""
ABUSEIPDB_API_KEY = ""
URLHAUS_API_KEY = ""
IPINFO_API_KEY = ""
OPENAI_API_KEY = ""
```

## Execução
```bash
streamlit run app.py
```

## Launcher
```bash
python launcher.py
```

## Fluxo de uso
1. Acesse **Analisar IOC**.
2. Gere análise e salve como caso.
3. Reabra em **Histórico** ou **Casos**.
4. Abra **Detalhe da Análise**.
5. Exporte relatório/KQL.

## Estrutura
```text
threatlens/
├── app.py
├── launcher.py
├── abrir_threatlens.bat
├── assets/
├── core/
├── services/
├── database/
├── utils/
├── views/
└── docs/
```

## Roadmap
- Integração SIEM/SOAR.
- RBAC e gestão multi-analista.
- Exportação PDF executiva/técnica.

## Limitações
- Dependência de disponibilidade/rate limit das APIs OSINT.
- Contexto interno de logs continua essencial.

## Uso responsável
- Não executar bloqueio automático sem validação humana.
- Não enviar dados internos sensíveis para APIs externas sem política formal.

## Links de Patrick Santos
- LinkedIn: [INSERIR_LINK_LINKEDIN]
- GitHub: [INSERIR_LINK_GITHUB]
- Portfólio: [INSERIR_LINK_PORTFOLIO]
- E-mail: [INSERIR_EMAIL_PROFISSIONAL]

## Docs
- [installation](docs/installation.md)
- [usage](docs/usage.md)
- [architecture](docs/architecture.md)
- [security](docs/security.md)
- [roadmap](docs/roadmap.md)
- [screenshots](docs/screenshots.md)


## IA e privacidade
- A análise IA envia apenas IOC + resultados de enriquecimento (sem secrets).
- Não envie logs internos sensíveis, credenciais ou dados pessoais.
- A resposta IA é auxiliar e exige validação humana.
