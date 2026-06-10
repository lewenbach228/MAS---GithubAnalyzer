# Project Meta — P8 Analyseur de Dépôts GitHub

> Document interne au portfolio. Non visible sur GitHub.
> Dernière mise à jour : 2026-06-10

---

## 1. Vue d'ensemble

**Type d'agent :** Utility-based / Tool Server (Agent outillé)
**Problème métier :** Auditer un dépôt GitHub sur la sécurité, la structure et le contenu, sans s'appuyer sur la documentation existante, via un protocole standardisé.
**Format :** Serveur MCP + API REST + Dashboard React

## 2. Walking Skeleton

Validé. Un client MCP CLI minimal testant la connexion stdio au serveur `server.py`, le clonage d'un repo, l'extraction de l'arborescence, l'analyse d'un fichier et le scan Semgrep en isolation.

## 3. Architecture Decisions

| Décision | Alternative | Raison |
|----------|------------|--------|
| **Python pour le core** | TypeScript / Node.js | Intégration native de l'AST (`tree-sitter-python`) et de Semgrep. SDK MCP Python mature. |
| **Bridge FastAPI** | Client MCP navigateur (WASM) | Simplifie le développement du front-end React, permet l'orchestration des appels parallèles et masque la complexité du protocole MCP. |
| **Tree-Sitter pour l'AST** | Expressions Régulières | Parsing robuste, déterministe et évolutif (supporte d'autres langages à l'avenir). |
| **OpenTelemetry (Trace fichier)** | Jaeger / Prometheus | MVP "zéro infra". Un `FileSpanExporter` permet de démontrer l'observabilité sans ajouter de complexité de déploiement. |
| **Explication Code via OpenAI** | Ollama local | Meilleure qualité et rapidité (GPT-4o-mini). Permet de combler l'absence de support AST pour les fichiers non Python. |

## 4. Limitations (internes)

- **AST limité à Python :** L'agent extrait les classes, fonctions et appels uniquement pour les fichiers `.py`. Les autres fichiers s'appuient uniquement sur l'explication LLM.
- **Scan Semgrep bloquant :** L'appel à Semgrep est synchrone. Sur de très gros dépôts, le scan peut timeout l'API.
- **Télémétrie simple :** Les traces sont simplement loggées dans `traces.jsonl` puis relues par l'API ; aucune agrégation complexe ni backend de tracing n'est implémenté.
- **Clone sans authentification :** Seuls les dépôts publics GitHub sont supportés (pas de gestion de tokens GitHub).

## 5. Couverture Coverage Matrix

- **Type agent :** Utility-based (Tool Server)
- **BDD :** Aucune (In-memory + fichiers JSONL)
- **Providers :** OpenAI (GPT-4o-mini)
- **Patterns :** Tool Use / Model Context Protocol (MCP), API-first, Observabilité (OpenTelemetry)
- **Compétences :** AST parsing, DevSecOps (Semgrep static analysis), Tracing.

## 6. Build

```bash
cd dashboard && npm run build  # tsc + vite → OK
python -m py_compile api_server.py scanner.py tracer.py # → OK
```

## 7. Structure des fichiers

```
agents/p8-github-analyzer/
├── server.py              # Serveur FastMCP natif (stdio)
├── api_server.py          # Bridge FastAPI (expose les tools en REST)
├── explainer.py           # LLM Explainer (OpenAI GPT-4o-mini)
├── analyzer.py            # Moteur AST (Tree-Sitter Python)
├── scanner.py             # Moteur de Scan (Semgrep)
├── cloner.py              # Git Wrapper
├── tracer.py              # Configuration OpenTelemetry (FileExporter)
├── client_test.py         # Test end-to-end MCP Client
├── dashboard/             # Front-end React + Vite
│   ├── src/components/    # Composants React (FileTree, Telemetry, etc.)
│   └── src/api.ts         # Client HTTP
└── project.meta.md        # Ce fichier
```