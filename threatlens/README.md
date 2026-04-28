# ThreatLens

**IOC Enrichment & Triage Platform**

**Desenvolvido por Patrick Santos**

ThreatLens evoluiu para uma arquitetura incremental com três camadas:
- **legacy-streamlit/** (MVP atual preservado)
- **backend-go/** (API principal em Go)
- **frontend/** (Next.js + TypeScript + Tailwind)

> O ThreatLens apoia a decisão do analista e **não** executa bloqueio automático.

## Arquitetura
```text
threatlens/
├── legacy-streamlit/
├── backend-go/
│   ├── cmd/server
│   └── internal/{api,config,db,models,services}
├── frontend/
│   ├── app/
│   ├── components/
│   └── lib/
├── docs/
├── docker-compose.yml
└── README.md
```

## Legacy Streamlit (preservado)
```bash
cd threatlens
streamlit run app.py
```
Ou:
```bash
cd threatlens/legacy-streamlit
./run_legacy.sh
```

## Backend Go
```bash
cd threatlens/backend-go
go mod tidy
go run ./cmd/server
```
API base: `http://localhost:8080/api`

### Endpoints principais
- `GET /api/health`
- `GET /api/dashboard/stats`
- `POST /api/ioc/analyze`
- `GET /api/ioc/history`
- `GET /api/ioc/history/:id`
- `GET /api/ioc/search?q=`
- `GET /api/cases`
- `GET /api/cases/:id`
- `POST /api/cases`
- `PATCH /api/cases/:id`
- `GET /api/sources/health`
- `POST /api/ai/analyze`
- `GET /api/config/status`

## Frontend Next.js
```bash
cd threatlens/frontend
npm install
npm run dev
```
App: `http://localhost:3000`

## Docker
```bash
cd threatlens
docker compose up --build
```

## Variáveis de ambiente (`.env`)
```env
VIRUSTOTAL_API_KEY=
ABUSEIPDB_API_KEY=
URLHAUS_API_KEY=
IPINFO_API_KEY=
OPENAI_API_KEY=
PORT=8080
DB_PATH=./threatlens-go.db
FRONTEND_ORIGIN=http://localhost:3000
NEXT_PUBLIC_API_BASE=http://localhost:8080/api
```

## Funcionalidades atuais
- Dashboard SOC/SaaS dark com KPIs, gráficos observabilidade e saúde das fontes.
- Histórico investigativo e central de casos.
- Análise de IOC com score, risco, confiança, recomendação e KQL.
- Análise assistida por IA (opcional, segura por ausência de chave).
- Persistência local em SQLite.

## Roadmap
- Migração completa de fluxo para API Go + frontend Next.js.
- Camada de autenticação e RBAC.
- Evolução para PostgreSQL.
- Integrações SIEM/SOAR.

## Links de Patrick Santos
- LinkedIn: [INSERIR_LINK_LINKEDIN]
- GitHub: [INSERIR_LINK_GITHUB]
- Portfólio: [INSERIR_LINK_PORTFOLIO]
- E-mail: [INSERIR_EMAIL_PROFISSIONAL]
