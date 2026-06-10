# P8: GitHub Analyzer

## Strategy Alignment
- **Agent Type**: Utility-based / Tool Server
- **Primary Goal**: Prouver la maîtrise du protocole MCP, de l'analyse statique (AST/Semgrep) et de l'observabilité (OpenTelemetry) pour un agent Architecte.
- **Competencies Tracked**: MCP Protocol, OpenTelemetry, DevSecOps (Semgrep), AST parsing (tree-sitter).
- **Target Audience**: CTO / VP Engineering (prouve l'intégration d'outils standards au sein d'une architecture).

## Implementation Details
- **Stack**: Python 3.14, FastAPI, MCP SDK, tree-sitter, Semgrep, OpenTelemetry, React + Vite.
- **Provider**: OpenAI (GPT-4o-mini) pour l'explication du code multi-langage.
- **Integration**: FastAPI Bridge + React Dashboard.

## Notes (Not for README)
- Le `__main__.py` de Semgrep bloque son exécution via `python -m semgrep`. Un contournement a été utilisé via `subprocess` dans `scanner.py`.
- Le serveur FastMCP est disponible via `server.py` mais `api_server.py` est utilisé pour la démonstration web.
- Les données OpenTelemetry sont sauvées dans `traces.jsonl` pour simplifier l'UI sans nécessiter Jaeger/Zipkin.
