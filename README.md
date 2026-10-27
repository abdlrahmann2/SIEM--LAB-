# Lookout

**A security event console that watches a log stream, correlates it into alerts, and lets you rehearse real attack chains against it.**

Lookout ingests log events, normalizes and scores them, runs correlation rules over the live stream, and surfaces the result as alerts you can triage. A built-in drill engine replays scripted, MITRE ATT&CK-mapped attack scenarios so you can see your rules fire without waiting for a real incident.

```
   ╭───────╮
  ╱  ╭───╮  ╲     L O O K O U T
 │   │ ● │   │
  ╲  ╰───╯  ╱
   ╰───────╯
```

## What it does

- **Ingest and correlate in real time.** Events are normalized, given a severity, written to MongoDB and published to a Redis Stream. A consumer group evaluates correlation rules against that stream.
- **Three rule types.** Threshold (N events in a window), Sequence (ordered events) and Aggregation (grouped counts).
- **Triage workflow.** Alerts move through acknowledge, investigate, resolve or false positive.
- **Live views.** Server-Sent Events feed the alert list and log viewer, which supports pagination and filtering.
- **Drills.** Four YAML playbooks generate multi-stage event sequences: *Brute Force with Lateral Movement*, *Data Exfiltration via DNS Tunneling*, *Phishing to C2 Beaconing* and *Privilege Escalation and Persistence*. Playback speed is adjustable.
- **Accounts and roles.** JWT auth with Argon2 password hashing, `analyst` and `admin` roles, and rate limiting.

## Quick start

```bash
cp .env.example .env      # set SECRET_KEY first
docker compose up -d
```

Open `http://localhost:8600`. Create the first admin from the backend container:

```bash
docker exec -it lookout-backend flask admin create
```

Against the dev stack, `just create-admin` does the same.

For development with hot reload, use `docker compose -f dev.compose.yml up`. Common tasks are wrapped in a [`just`](https://github.com/casey/just) file; run `just` to list them.

## Stack

- **Backend:** Flask, MongoEngine, Redis Streams, Pydantic, Argon2, PyJWT, structlog, Gunicorn (Python 3.14)
- **Frontend:** React 19, TypeScript, Vite, TanStack Query, Zustand, visx, SCSS Modules
- **Data:** MongoDB 7, Redis 7
- **Edge:** nginx

## Layout

```
backend/
  lookout/
    controllers/   request handling and business logic
    routes/        blueprints, mounted under /v1
    models/        MongoEngine documents (alert, log_event, correlation_rule, ...)
    engine/        normalizer, severity classifier, correlation engine
    scenarios/     drill runner and YAML playbooks
    core/          auth, streaming (SSE + Redis), rate limiting, error handling
    schemas/       Pydantic request/response models
  wsgi.py          production entry point
frontend/          React console
conf/              Dockerfiles and nginx configs
learn/             background and walkthroughs
```

## Configuration

Compose reads `.env` (see `.env.example`):

| Variable | Purpose |
|----------|---------|
| `APP_NAME` | Prefix for container and project names (default `lookout`) |
| `SECRET_KEY` | JWT signing secret. Change it |
| `MONGO_DB` | Database name |
| `REDIS_PASSWORD` | Optional Redis password |
| `NGINX_HOST_PORT` | Public port (default `8600`) |
| `MONGO_HOST_PORT`, `REDIS_HOST_PORT`, `BACKEND_HOST_PORT`, `FRONTEND_HOST_PORT` | Host ports published by the dev stack |
| `LOG_LEVEL`, `DEBUG` | Backend logging |

Redis streams are `lookout:logs` and `lookout:alerts`; the consumer group is `lookout-correlation`.

## Learn

| Module | Topic |
|--------|-------|
| [00 Overview](learn/00-OVERVIEW.md) | Prerequisites and quick start |
| [01 Concepts](learn/01-CONCEPTS.md) | Log correlation, severity, ATT&CK, real breaches |
| [02 Architecture](learn/02-ARCHITECTURE.md) | System design and data flow |
| [03 Implementation](learn/03-IMPLEMENTATION.md) | Code walkthrough |
| [04 Challenges](learn/04-CHALLENGES.md) | Extension ideas and exercises |

## Provenance and license

Lookout is a derivative of the AGPL-3.0 project `siem-dashboard` by AngelaMos, restructured and rebranded. See [NOTICE](NOTICE) for what changed. Original copyright headers are kept in the source files, as the license requires.

Licensed under the [GNU Affero General Public License v3.0](LICENSE). If you run a modified version as a network service, you must offer its source to its users.
