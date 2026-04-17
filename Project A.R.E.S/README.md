# A.R.E.S — Artificial Research and Engineering System

A.R.E.S (Artificial Research and Engineering System) is a local-first AI system designed to support research, engineering workflows, task execution, and persistent memory management.

It runs entirely on a single machine using Ollama, FastAPI, and SQLite, providing a private, self-contained AI environment with no external API dependencies.

This repository represents a GitHub-safe showcase build, demonstrating the system architecture, core functionality, and extensible design while allowing private logic to remain local.

---

## Core Capabilities

* Local browser-based chat interface
* FastAPI backend for structured execution
* SQLite persistence for tasks, notes, memory, and logs
* Retrieval-Augmented Generation (RAG) memory system
* Optimization-based routing with pairwise ranking (O(n²))
* Modular tool system (tasks, notes, memory operations)
* One-click Windows startup scripts
* Health monitoring endpoint (`/health`)

---

## System Overview

A.R.E.S is designed as a structured AI execution system:

User Input → Intent Routing → Optimizer → Tool Execution / Memory Retrieval → Local Model → Response

Key components:

* Agent Layer — builds prompts and controls execution flow
* Memory System (RAG) — retrieves relevant stored context
* Optimizer — selects execution strategy using pairwise comparison
* Tool System — performs deterministic actions (tasks, notes, memory)
* Local Model (Ollama) — generates responses

---

## Privacy and Design Philosophy

* Fully local execution
* No API keys required
* No external data transmission
* Designed for single-user ownership
* Supports private extensions without exposing logic publicly

---

## Public-Safe Repository Strategy

This repository is structured to allow public demonstration without exposing sensitive implementation details.

### Included in the public repository:

* Working application runtime
* User interface and backend architecture
* Database schema
* RAG memory system
* Baseline routing and optimizer
* Documentation and startup scripts

### Excluded from the public repository:

* Custom routing heuristics
* Private system prompts
* Internal optimization strategies
* Local databases and user data
* Experimental or proprietary logic

Sensitive logic can be placed in:

```
private_overrides/
```

This directory is ignored by Git and can be used for local extensions without exposing them publicly.

---

## Quick Start

1. Install Python 3.11 or higher
2. Install Ollama: https://ollama.com
3. Pull a local model (example):

   ```
   ollama pull phi3:mini
   ```
4. Create a virtual environment
5. Install dependencies:

   ```
   pip install -r requirements.txt
   ```
6. Start A.R.E.S:

   * Windows: double-click `BOOT_ARES_ONLINE.bat`
   * Manual:

     ```
     python -m uvicorn app.main:app --reload
     ```
7. Open:

   ```
   http://127.0.0.1:8000
   ```

---

## Project Structure

```
app/
  core/
    agent.py
    config.py
    llm_local.py
    memory.py
    optimizer.py
    private_loader.py
    router.py
    tools.py
  db/
    schema.py
  static/
  templates/
private_overrides/
scripts/
BOOT_ARES_ONLINE.bat
STOP_ARES.bat
```

---

## Showcase Positioning

A.R.E.S can be presented as:

* A local-first AI system for private use
* A FastAPI and Ollama-based assistant with persistent memory
* A modular architecture combining tools, memory, routing, and retrieval
* A foundation for building private AI infrastructure

---

## Notes

* No API keys are required
* The system is designed for single-user local operation
* `ares.db` is generated on first run and excluded from version control
* `private_overrides/` is excluded from version control to protect sensitive logic

---

## Summary

A.R.E.S is not a chatbot. It is a locally controlled AI system designed for structured execution, memory-aware responses, and extensible workflow support.

It provides a foundation for building private, self-hosted AI systems with full control over data, behavior, and system evolution.
