# Multi-Agent Data Analyst

An interview-ready **Agentic AI** project that turns natural-language business questions into data-driven answers using a **LangGraph multi-agent workflow**, executable SQL tools, validation, analytics and response synthesis.

## Business scenario

A business user asks questions such as:

- What is our total revenue?
- Show revenue by region.
- What are the top products by revenue?
- Show monthly sales trends.
- Which customers generate the most revenue?

The system routes the request through specialized agents instead of relying on one monolithic prompt.

## Architecture

```text
User
  |
  v
Orchestrator Agent
  |
  +--> Unsupported --> Response Agent
  |
  +--> Data/SQL Agent
          |
          v
      SQL Execution Agent ---> SQLite
          |
          v
      Validation Agent
          |
          v
      Analytics Agent
          |
          v
      Response Agent
          |
          v
        Answer
```

See [`docs/architecture.md`](docs/architecture.md) for the Mermaid diagram and Azure production mapping.

## Multi-agent responsibilities

| Agent | Role |
|---|---|
| Orchestrator | Understands intent and chooses the workflow path |
| Data/SQL Agent | Generates SQL with optional LLM assistance |
| SQL Execution Agent | Executes SQL through a controlled tool |
| Validation Agent | Validates result quality and safety |
| Analytics Agent | Interprets returned data |
| Response Agent | Produces the final response |

## Technology stack

- Python 3.10+
- LangGraph
- LangChain Core
- OpenAI-compatible LLM / Azure OpenAI option
- SQLite
- Pandas-compatible CSV data
- Pydantic
- Pytest
- GitHub Actions

## Sample data

`data/sales.csv` contains 20 synthetic sales orders and `data/customers.csv` contains customer master data. No real customer information is used.

## Project structure

```text
multi-agent-data-analyst/
├── data/
│   ├── sales.csv
│   └── customers.csv
├── src/
│   ├── agents.py
│   ├── main.py
│   └── tools.py
├── tests/
│   └── test_agents.py
├── docs/
│   ├── architecture.md
│   └── interview_questions.md
├── .github/workflows/tests.yml
├── .env.example
├── requirements.txt
└── README.md
```

## How to run

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m src.main
```

The project works without an API key using deterministic SQL templates. To enable LLM-based SQL generation, copy `.env.example` to `.env` and provide an OpenAI-compatible key/model. Never commit secrets.

## Example flow

**Question:** `Show revenue by region`

1. Orchestrator classifies it as a data-analysis request.
2. Data/SQL Agent creates a SQL query.
3. SQL Agent executes the query against SQLite.
4. Validation Agent checks the result.
5. Analytics Agent identifies the highest-ranked region and result set.
6. Response Agent returns the analysis and SQL used.

## Agentic AI concepts demonstrated

- Orchestration
- Specialized agents
- Shared state
- Conditional routing
- Tool use
- SQL generation and execution
- Guardrails
- Validation agent
- Sequential agent workflow
- LLM + deterministic fallback

## Why this is better than a single LLM call

A single prompt may generate an answer without a reliable execution boundary. This design separates planning, data access, validation and response generation. Each node can be tested, observed and replaced independently.

## Production Azure architecture

For an enterprise implementation, replace the local components with:

- Azure OpenAI for reasoning and SQL generation
- Microsoft Fabric Warehouse / Azure SQL / Synapse for governed data
- Azure Data Lake Storage for raw data
- Azure AI Foundry for agent lifecycle and evaluation
- Microsoft Purview for governance and lineage
- Azure Key Vault + Managed Identity for secrets/authentication
- Azure Monitor / Application Insights for observability

## Future enhancements

- Add SQL query repair agent
- Add human approval for expensive/high-risk queries
- Add semantic layer and business glossary
- Add parallel agents for independent analysis dimensions
- Add LangSmith tracing and evaluation datasets
- Add role-based access and row-level security
- Add RAG over business definitions and KPI documentation
- Add support for SQL Server, Oracle and Fabric

## Interview explanation

> "I designed a stateful multi-agent analytics system using LangGraph. An orchestrator first classifies the user request. A specialized data agent converts the request to SQL, an execution agent calls a controlled database tool, a validation agent checks the result, and an analytics agent interprets it before a response agent returns the answer. The key advantage is separation of concerns, explicit routing, tool boundaries and testability. In Azure, the LLM can be Azure OpenAI, the data layer can be Fabric or Azure SQL, and Purview and Azure Monitor provide governance and observability."

## Disclaimer

All data is synthetic and created only for demonstration, learning and interview purposes.
