# Project A.R.E.S.

A.R.E.S. stands for Artificial Research and Engineering System. It is a local FastAPI application that connects to Ollama, stores chat and task data in SQLite, retrieves relevant memories with TF-IDF scoring, and routes each request to an installed local model.

## Current capabilities

- Browser-based chat interface
- Local Ollama model discovery and generation
- SQLite storage for chats, tasks, notes, memories, and routing outcomes
- TF-IDF memory retrieval with cosine similarity
- Rule-based tool commands for tasks, notes, and memory
- Model selection based on request traits and recorded outcomes
- Health endpoint for the application and Ollama connection
- Optional local override modules, disabled by default

## Architecture

```text
browser -> FastAPI -> command router -> tools or model optimizer
                                      -> memory retrieval -> Ollama
                                      -> SQLite persistence
```

## Requirements

- Python 3.11 or newer
- [Ollama](https://ollama.com) running locally
- At least one supported model, such as `phi3:mini`

## Run it

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
ollama pull phi3:mini
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`.

Windows users can run `BOOT_ARES_ONLINE.bat` after installing the requirements and Ollama model.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | Ollama API address |
| `ARES_DB_PATH` | `ares.db` | SQLite database path |
| `ARES_DEFAULT_MODEL` | `phi3:mini` | Preferred fallback model |
| `ARES_ENABLE_PRIVATE_OVERRIDES` | `false` | Load local Python overrides when explicitly enabled |

Keep the service bound to localhost unless you add authentication and network controls. Chat history and saved memories are stored in the configured SQLite database.

## Test it

```bash
python -m pip install -r requirements-dev.txt
pytest -q
```

The test suite does not require a running Ollama instance.

## Author

Khyri Williams, preferred name Kai

## License

MIT
