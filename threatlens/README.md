# ThreatLens - IOC Enrichment & Triage Platform

Aplicativo Streamlit para Blue Team/SOC que detecta tipo de IOC, realiza enriquecimento com fontes públicas de Threat Intelligence, calcula score de risco, gera recomendação operacional, persiste histórico em SQLite e permite exportação em CSV.

## Funcionalidades

- Detecção automática de IOC:
  - IPv4
  - Domínio (incluindo `dominio[.]com`)
  - URL
  - Hash MD5, SHA1 e SHA256
- Enriquecimento de IOC:
  - VirusTotal (IP, domínio, URL e hash)
  - AbuseIPDB (IP)
  - URLhaus (URL e domínio)
  - IPinfo (opcional para IP)
- Tratamento resiliente de erros por fonte:
  - `Consultado`, `Não aplicável`, `Sem API key`, `Erro`, `Sem resultado`
- Cálculo de score de risco (0-100) e classificação:
  - Baixo, Médio, Alto, Crítico
- Recomendação operacional por faixa de risco
- Geração automática de query KQL para Microsoft Defender Advanced Hunting
- Histórico local com SQLite
- Análise em lote por CSV/TXT
- Dashboard com métricas e gráficos
- Exportação de resultados/histórico para CSV

## Estrutura

```text
threatlens/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
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
├── pages/
│   ├── dashboard.py
│   ├── analyze.py
│   ├── batch.py
│   ├── history.py
│   ├── settings.py
│   └── about.py
└── utils/
    ├── export.py
    └── ui.py
```

## Requisitos

- Python 3.11+

## Instalação

```bash
cd threatlens
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## Configuração de API keys

Use **um** dos formatos:

### Opção A: Streamlit secrets (recomendado)

1. Crie o arquivo `.streamlit/secrets.toml`
2. Copie o conteúdo de `.streamlit/secrets.toml.example`
3. Preencha as chaves:

```toml
VIRUSTOTAL_API_KEY = "..."
ABUSEIPDB_API_KEY = "..."
IPINFO_API_KEY = "..."
```

### Opção B: .env

1. Copie `.env.example` para `.env`
2. Preencha os valores.

> O app funciona parcialmente mesmo sem todas as chaves.

## Execução

```bash
streamlit run app.py
```

## Uso

### Tela Dashboard
Visualize total de análises, distribuição por risco/tipo e últimas análises.

### Tela Analisar IOC
1. Cole um IOC
2. Clique em **Analisar IOC**
3. Veja score, risco, recomendação, fontes e evidências
4. Exporte o resultado em CSV
5. Copie a KQL gerada

### Tela Análise em lote
- Suba CSV com coluna `ioc` ou TXT com um IOC por linha
- Execute análise e exporte o consolidado

### Tela Histórico
- Filtre por tipo/risco
- Busque por IOC
- Exporte para CSV
- Limpe histórico com confirmação

## Segurança

- Não há hardcode de API keys
- Chaves não são exibidas na interface
- Chaves não são salvas em banco
- `secrets.toml` é ignorado no Git
- Chamadas HTTP com timeout
- Tratamento de exceções sem stack trace para usuário
- Não executa bloqueio automático em firewall/EDR

## Limitações

- Dependência de disponibilidade/rate limit das APIs externas
- Cobertura e contexto variam por fonte
- Não substitui investigação com telemetria interna

## Exemplo rápido de IOC

- IP: `8.8.8.8`
- Domínio: `example[.]com`
- URL: `https://example.com/path`
- MD5: `44d88612fea8a8f36de82e1278abb02f`

