# Mini-projet RSI2 – Atelier POO et DevOps1
## Gestionnaire de tâches partagé (client–serveur en Python + Git + Docker)

**Language:** Python 3.11+  
**Author:** repo template for school mini-project  

---

## Project overview
This repository provides a small client-server task manager:

- `serveur/` contains task model (`Tache`), manager (`GestionnaireTaches`) and TCP server (`ServeurTaches`).
- `client/` contains a simple interactive CLI (`ClientTaches`) with menu in French.
- Communication: JSON line-delimited protocol over TCP (`\n` delimited).
- Concurrency: server handles multiple clients using `ThreadPoolExecutor`.
- Persistence: optional JSON persistence configurable via CLI flags or environment variables.

---

## Features
- Add, list, delete, update task status.
- Optional filtering by `auteur` and `statut`, search by substring in title.
- Simple, robust protocol that always returns JSON including `status` and `error` when appropriate.
- Unit tests for manager and persistence.
- Dockerfile for server and optional client, `docker-compose.yml`.

---

## Quick run (no Docker)

### Start server (no persistence)
```bash

python -m serveur.main

```

## Quick run (Docker)

```bash

docker compose up --build
docker compose run sample-client

```
