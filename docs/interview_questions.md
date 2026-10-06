# Interview Questions

1. **Why use multiple agents?** Separate responsibilities so planning, data access, validation and response generation can evolve independently.
2. **Why LangGraph?** It models stateful workflows with nodes, conditional edges and explicit execution paths.
3. **What does the orchestrator do?** It classifies the user request and routes it to the appropriate capability.
4. **Why use SQLite?** It is lightweight for a portfolio demo while preserving a real SQL execution boundary.
5. **How is SQL generation handled?** Azure/OpenAI-compatible LLM generation is optional; deterministic SQL templates provide a no-key fallback.
6. **How do you prevent destructive SQL?** The SQL tool accepts only SELECT/WITH and rejects write/DDL keywords.
7. **Where is validation performed?** After execution, before analytics and response synthesis.
8. **How would you scale this?** Replace SQLite with Azure SQL/Fabric/Synapse, add async execution, caching, connection pooling and governed semantic models.
9. **How would you add human-in-the-loop?** Pause before high-impact actions or expensive queries and request approval.
10. **How would you evaluate it?** Measure routing accuracy, SQL execution accuracy, answer correctness, latency, cost and safety violations.
11. **How would you add observability?** Trace every agent node, prompt, tool call, latency, token usage and validation outcome with LangSmith/Azure Monitor.
12. **What is the key architecture pattern?** User → Orchestrator → Specialized Agents → Tools/Data → Validation → Analytics → Response.
