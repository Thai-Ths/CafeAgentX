# SupportFlowX CafeAgentX

A modular, agent-based support system for cafes, featuring RAG (Retrieval-Augmented Generation), Gemini LLM integration, and workflow orchestration. Built with Gradio for the UI.

## Features
- Multi-agent workflow (intake, cafe bot, database, aggregator)
- RAG system for knowledge retrieval
- Gemini LLM (Google Generative AI) integration
- Gradio-based chat UI
- Modular, extensible architecture

## Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your Gemini API key (starts with `AI...`).
4. (Optional) Sync the database from CSVs if needed.

## Usage
Run the main app:
```bash
python main.py
```

Open the Gradio UI in your browser and enter your Gemini API key to start chatting.

## Project Structure
- `agents/`         — Agent logic and wrappers
- `assets/`         — Images, knowledge base, raw data
- `config/`         — Configuration and agent registry
- `database/`       — SQLite DB and scripts
- `rag/`            — RAG system and embeddings
- `ui/`             — Gradio UI and themes
- `workflows/`      — Workflow graph and routing

## License
MIT
