# Gemma3 Local Chat

A minimal local AI chat setup using [Gemma 3](https://ollama.com/library/gemma3) models via [Ollama](https://ollama.com/), containerized with Docker and accessed through a simple Python CLI client.

---

## Overview

- **`docker-compose.yml`** — Spins up Ollama in Docker and auto-pulls the `gemma3:1b` model on first run.
- **`client.py`** — A terminal chat client that maintains conversation history and talks to Ollama via its OpenAI-compatible API.

---

## Requirements

- [Docker](https://docs.docker.com/get-docker/) with the Compose plugin
- Python 3.8+
- `openai` Python package

Install the Python dependency:

```bash
pip install openai
```

---

## Setup

### 1. Start Ollama

```bash
docker compose up -d
```

This will:
1. Pull the `ollama/ollama` Docker image.
2. Start the Ollama server on port `11434`.
3. Run an init container that waits for Ollama to be ready and then pulls the `gemma3:1b` model automatically.

The model download happens only once — it is stored in a named Docker volume (`gemma4_ollama_data`) and persists across restarts.

### 2. Wait for the model to be ready

You can follow the init container logs to confirm the model has been pulled:

```bash
docker logs -f gemma4-init
```

You should eventually see:

```
Model ready.
```

### 3. Run the chat client

```bash
python client.py
```

Type your messages and press Enter. Type `salir` to exit.

---

## Daily usage

Once the initial setup is done, day-to-day use is just three commands:

```bash
docker compose up -d   # start Ollama in the background
python client.py       # start chatting
docker compose down    # stop everything when done
```

---

## Configuration

### Changing the model

Edit `client.py` and update the `MODEL` variable:

```python
MODEL = "gemma3:4b"   # or gemma3:12b, gemma3:27b
```

Then update `docker-compose.yml` so the init container pulls the right model:

```yaml
ollama pull gemma3:4b
```

Available Gemma 3 variants:

| Model | Size on disk | Notes |
|---|---|---|
| `gemma3:1b` | ~0.8 GB | Fastest, lowest resource usage |
| `gemma3:4b` | ~3 GB | Good balance of speed and quality |
| `gemma3:12b` | ~8 GB | Higher quality, needs more RAM/VRAM |
| `gemma3:27b` | ~17 GB | Best quality, requires a capable GPU |

### Changing the port

By default Ollama is exposed on `11434`. To change it, edit the `ports` section in `docker-compose.yml` and update the `base_url` in `client.py` accordingly.

---

## Architecture

```
┌─────────────────────────────────┐
│  client.py (Python)             │
│  OpenAI-compatible HTTP client  │
│  localhost:11434/v1             │
└────────────────┬────────────────┘
                 │ HTTP
┌────────────────▼────────────────┐
│  Docker: ollama/ollama          │
│  container: gemma4-ollama       │
│  port: 11434                    │
│  volume: gemma4_ollama_data     │
└─────────────────────────────────┘
```

- The Ollama container is on an **internal network** (`no-internet`) with no outbound internet access after the model is pulled.
- It is also on a **bridge network** (`host-access`) so the Python client on the host can reach it via `localhost:11434`.
- Conversation **history is kept in memory** for the duration of the session, giving the model full context of the current conversation.

---

## Stopping

```bash
docker compose down
```

To also remove the downloaded model and free up disk space:

```bash
docker compose down -v
```

> **Warning:** `-v` deletes the `gemma4_ollama_data` volume. The model will be re-downloaded on next `docker compose up`.
