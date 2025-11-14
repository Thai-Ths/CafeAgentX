# CafeAgentX ☕
*LangGraph-powered café chatbot with RAG, SQLite, and extensible agents*

[**🌐 Try CafeAgentX on Hugging Face Spaces**](https://huggingface.co/spaces/LKTs/CafeAgentX)

<img width="1278" height="854" alt="CafeAgentX UI" src="https://github.com/user-attachments/assets/c215c19d-da07-4b50-b961-14a1eed8c607" />

---

## Overview

**CafeAgentX** is a ready-to-run café assistant built with LangChain and LangGraph. The assistant blends Retrieval-Augmented Generation (RAG), a structured SQLite database, and multiple specialized agents to deliver accurate answers about menus, promotions, and reservations.

---

## ✨ What CafeAgentX Delivers

- **RAG for café knowledge** – Answers grounded in curated documents stored in ChromaDB.
- **SQLite order data** – Structured lookups for menu items, pricing, and availability.
- **Plug-in agents** – Intake, cafe knowledge, and database experts collaborate via LangGraph; register new agents in minutes.
- **Polished UI** – A Gradio chat interface with logs, sample prompts, and Gemini API key input.
- **Production-minded flow** – Clear separation between workflow orchestration, agents, and data assets.

---

## 🏗️ Architecture Snapshot

The orchestration lives in `workflows/`. `main.py` wires together the agents, builds the LangGraph workflow, and launches the Gradio UI.

- `agents/` – Individual agent logic (intake, café knowledge, database, aggregators, etc.).
- `rag/` – Document loaders, embeddings, and vector store helpers.
- `database/` – SQLite schema plus scripts to refresh café data.
- `config/` – Shared settings and agent registry.
- `ui/` – Front-end theme, assets, and layout code.

Add or swap agents by registering them in `config/agent_registry.py` and updating the router in `workflows/router.py`.

> **Tip:** Because the workflow is described as a LangGraph state machine, you can observe every intermediate step (state, logs, assigned agents) while you iterate on new capabilities.

---

## 📁 Project Structure

```
agents/      - Agent logic and wrappers
assets/      - Knowledge base and raw data for RAG
config/      - Configuration files and agent registry
database/    - SQLite DB and scripts
rag/         - RAG system and embeddings
ui/          - Gradio UI and static assets
workflows/   - Workflow graph, router, and shared state
main.py      - Application entry point
```

> **Note:** The Git repository is published as `SupportFlowX`, but the application itself is CafeAgentX. After cloning you are already in the correct project root.

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/Thai-Ths/SupportFlowX.git
cd SupportFlowX  # CafeAgentX project root
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
# or, for faster installs:
uv pip install -r requirements.txt
```

### 3. Prepare data & API key

- Place your café documents for RAG under `assets/knowledge_base/`.
- Ensure `database/database.db` exists (or edit the path in `config/settings.py`).
- Create a [Gemini API Key](https://makersuite.google.com/app/apikey) and keep it handy for runtime.

### 4. Rebuild knowledge base and database (optional)

```bash
python rag/rag_system.py       # embed docs into ChromaDB
python database/create_db.py  # create/update database.db
```

Run these whenever you update documents or menu data.

### 5. Launch CafeAgentX

```bash
python main.py
```

Open the local Gradio URL to chat with your café assistant.

---

## 🔧 Customizing CafeAgentX

### Add another specialist agent

1. **Create the agent logic** in `agents/your_agent.py`.
   ```python
   from agents.base import BaseAgent

   class LoyaltyAgent(BaseAgent):
       def __init__(self, crm_client):
           self.crm_client = crm_client

       def process(self, state):
           # Inspect state["user_message"] or structured assignments
           # Return a dict containing updates for the workflow state
           return {"logs": ["Loyalty agent responded"], "final_response": "…"}
   ```
2. **Register the agent** in `config/agent_registry.py` so the workflow can instantiate it.
3. **Route traffic** by editing `workflows/router.py` to let the intake agent select the new specialist when relevant.
4. **Chain the node** inside `workflows/graph.py` (pass the callable to `build_workflow`) so it feeds its output to the aggregator.

### Retarget the bot to a different venue

- Swap the café PDFs/notes in `assets/knowledge_base/` for your domain.
- Replace `database/database.db` (or point `config/settings.py` to a new SQLite file) with your structured menu/inventory data.
- Update the copy and imagery in `config/ui_config.py` and `ui/theme.css`.
- Adjust prompts in the agent classes to reflect your terminology.

### Integrate external systems

- Call POS, loyalty, or reservation APIs from the aggregator or specialist agents.
- Publish usage metrics or alerts by appending to the `logs` field in the workflow state.
- Wrap the Gradio blocks in FastAPI/ASGI and serve with `uvicorn` for production.

---

## 🖥️ Demo Flow

CafeAgentX coordinates multiple roles:

1. **Intake Agent** interprets the user request and decides which specialists are needed.
2. **Cafe Knowledge Agent (`landscape_cafe_bot`)** performs RAG lookups over curated café documents.
3. **Coffee DB Agent** queries SQLite for structured menu and availability data.
4. **Aggregator** merges responses and returns a single, polished answer.

You can append new agents to this sequence without disturbing the existing collaboration.

---

## 📦 Requirements

- Python 3.8+
- [gradio](https://gradio.app/)
- [langgraph](https://github.com/langchain-ai/langgraph)
- [typing-extensions](https://pypi.org/project/typing-extensions/)
- [langchain-google-genai](https://github.com/langchain-ai/langchain)
- [pillow](https://python-pillow.org/)
- [chromadb](https://www.trychroma.com/)
- [sentence-transformers](https://www.sbert.net/)
- [PyPDF2](https://pypdf2.readthedocs.io/)
- [pymupdf](https://pymupdf.readthedocs.io/)
- [langchain-text-splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/text_splitters/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [pandas](https://pandas.pydata.org/)

(Everything is listed in `requirements.txt`.)

---

## 🔒 License

Copyright (c) 2024 Thai

CafeAgentX is released for **educational, research, or internal evaluation purposes only**.

- **No commercial use.**
- **No redistribution, sublicensing, or inclusion in proprietary software.**
- You may modify the project for private or learning purposes.
- For public deployment or commercial use, please contact the author for written permission.

All rights reserved.

---

## ⭐ Credits

Built with:

- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [LangChain](https://python.langchain.com/)
- [Gradio](https://gradio.app/)
- [Google Generative AI](https://makersuite.google.com/)
