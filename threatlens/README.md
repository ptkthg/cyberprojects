# ThreatLens - IOC Enrichment & Triage Platform

![ThreatLens Banner](assets/blue_team_banner.svg)

**Desenvolvido por Patrick Santos**

Plataforma de enriquecimento e triagem de IOCs para Blue Team/SOC, com interface Streamlit profissional, histórico local em SQLite, análise individual/lote, score explicável e integração com fontes OSINT.

## Principais funcionalidades

- Detecção e normalização de IOC:
  - IPv4, domínio, URL, MD5, SHA1 e SHA256.
  - Suporte a formato ofuscado como `dominio[.]com`.
- Enriquecimento de IOC em múltiplas fontes:
  - VirusTotal v3
  - AbuseIPDB
  - URLhaus
  - IPinfo (opcional)
- Score de risco explicável:
  - score final + breakdown dos motivos da pontuação
  - classificação Baixo/Médio/Alto/Crítico
- Recomendação operacional para SOC N1/N2.
- KQL generator para Microsoft Defender Advanced Hunting.
- Histórico com filtros e decisão do analista (Pendente, Monitorar, Investigar, Bloquear, Falso positivo, Escalado para incidente).
- Análise em lote (CSV/TXT) com barra de progresso e tolerância a falhas por IOC.
- Exportação CSV e relatório HTML.
- Launcher desktop (Tkinter) para iniciar/parar o ThreatLens sem terminal.

## Prints sugeridos

- Dashboard SOC com métricas e gráficos.
- Tela de triagem IOC com score breakdown.
- Histórico com decisão do analista.
- Launcher desktop em execução.

## Instalação

```bash
cd threatlens
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## Configuração de API keys

Crie `.streamlit/secrets.toml` com:

```toml
VIRUSTOTAL_API_KEY = ""
ABUSEIPDB_API_KEY = ""
URLHAUS_API_KEY = ""
IPINFO_API_KEY = ""
```

Também é possível usar `.env` com base em `.env.example`.

> O app funciona parcialmente mesmo sem todas as chaves.

## Executar via Streamlit

```bash
streamlit run app.py
```

## Executar via launcher.py (desktop)

```bash
python launcher.py
```

Funcionalidades do launcher:
- Iniciar ThreatLens
- Abrir no navegador
- Parar ThreatLens
- Sair
- Status de execução

## Executar via arquivo BAT (Windows)

Duplo clique em `abrir_threatlens.bat`.

Fluxo:
- ativa `.venv` se existir
- executa `python launcher.py`
- mantém terminal para visualizar erro

## Gerar executável (PyInstaller)

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name ThreatLens launcher.py
```

Saída em `dist/ThreatLens.exe`.

## Estrutura do projeto

```text
threatlens/
├── app.py
├── launcher.py
├── abrir_threatlens.bat
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
├── assets/
│   ├── logo.svg
│   ├── shield.svg
│   ├── radar.svg
│   ├── network.svg
│   ├── threat.svg
│   └── blue_team_banner.svg
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
├── database/
│   └── db.py
├── services/
│   ├── virustotal.py
│   ├── abuseipdb.py
│   ├── urlhaus.py
│   └── ipinfo.py
├── core/
│   ├── analyzer.py
│   ├── ioc_detector.py
│   ├── scoring.py
│   ├── recommendations.py
│   ├── kql_generator.py
│   └── normalizer.py
├── views/
│   ├── dashboard.py
│   ├── analyze.py
│   ├── batch.py
│   ├── history.py
│   ├── settings.py
│   └── about.py
└── utils/
    ├── export.py
    ├── styles.py
    └── ui.py
```

## Limitações

- Dependência de disponibilidade e rate limit das APIs externas.
- IOC enrichment não substitui correlação em logs internos.
- Resultado deve ser usado como apoio à decisão.

## Uso responsável

ThreatLens **não realiza bloqueio automático** em firewall/EDR/endpoint. A decisão final é sempre do analista.

---

Desenvolvido por Patrick Santos.
