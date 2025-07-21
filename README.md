# SupportFlowX 🚀  
*Multi-Agent Orchestration Framework for Scalable Chatbots*

[**🌐 Try CafeAgentX on Hugging Face Spaces**](https://huggingface.co/spaces/LKTs/CafeAgentX)

> **Example Project:** CafeAgentX ☕ – Café Assistant Demo

<img width="1278" height="854" alt="image" src="https://github.com/user-attachments/assets/c215c19d-da07-4b50-b961-14a1eed8c607" />


---

## Overview

**SupportFlowX** is a flexible, agentic orchestration framework—built on LangGraph—designed to build scalable, multi-agent AI assistants.  
The core design enables easy integration, scaling, and replacement of domain-specific AI agents for any business scenario.  
By orchestrating tasks between specialized agents, SupportFlowX minimizes bottlenecks and maximizes both reliability and maintainability.

**CafeAgentX** is provided as a working demo — a café chatbot that showcases agent collaboration for customer Q&A, menu, promotions, and database support.

---

## ✨ Key Features

- **Orchestration-First:** True agentic routing; intake agent delegates tasks to skill-specific agents.
- **Highly Scalable:** Add or swap agents and domains with minimal code changes.
- **Reduce LLM Bottlenecks:** Parallel and specialized task handling for better throughput.
- **Production-Ready Demo:** Café Assistant (CafeAgentX) demonstrates end-to-end deployment.
- **Gradio UI:** Easy, ready-to-use chat interface for fast prototyping or real-world service.

---

## 💡 Use Cases

SupportFlowX is not limited to cafés!
- Customer support (retail, banking, IT helpdesk, etc.)
- Booking & reservations
- HR or internal knowledge bots
- Medical, law, or domain-specific assistants
- … any scenario where orchestrated, scalable agents make sense.

**Just swap out the agent modules and data!**

---

## 🏗️ Architecture

The main entry point is `main.py`, which builds the workflow and launches the chat UI.
- Configuration lives in `config/`.
- Database files are stored under `database/` and the knowledge base lives in `assets/knowledge_base/`.
- Each agent is modular and extensible (see the files in `agents/`).

## Project Structure

```

agents/      - Agent logic and wrappers
assets/      - Knowledge base and raw data
config/      - Configuration files and agent registry
database/    - SQLite DB and scripts
rag/         - RAG system and embeddings
ui/          - Gradio UI and static assets
workflows/   - Workflow graph and state router
main.py      - Application entry point

```

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/your-username/supportflowx.git
cd supportflowx
````

### 2. Install dependencies

#### With pip

```bash
pip install -r requirements.txt
```

#### Or with uv (faster installs/locking)

```bash
uv pip install -r requirements.txt
```

### 3. Prepare data & API key

* Place your knowledge base (RAG documents) in `assets/knowledge_base`
* Place your sample DB as `database/database.db` (or as configured)
* **Get a Gemini API Key**: [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey) (for Google Generative AI access)

### 4. Run the Demo App

```bash
python main.py
```

Then open the local Gradio UI in your browser!

---

## 🛠️ Customization & Scaling

* **Add new skills:** Create new agent modules in `agents/` and register them in `config/agent_registry.py`.
* **Change business logic:** Tweak agent routing and orchestration logic as needed.
* **Swap domains:** Replace Café agents and data with your own (e.g. legal, retail, travel, etc.)
* **Production Deployment:** Wrap in FastAPI/ASGI and run with `uvicorn` for robust serving.

---

## 🖥️ Example: CafeAgentX

CafeAgentX is a demo café assistant built with SupportFlowX, featuring:

* Menu, promotions, and table info via RAG & database queries
* Natural language chat with easy UI
* Realistic, extensible agent collaboration (IntakeAgent → CafeBot & DBAgent → Aggregator → Response)

> **Workflow Diagram:**
> <img width="446" height="456" alt="image" src="https://github.com/user-attachments/assets/cb515f28-4cbd-4c50-8914-ea4855324050" />

---

## 📦 Requirements

* Python 3.8+
* [gradio](https://gradio.app/)
* [langgraph](https://github.com/langchain-ai/langgraph)
* [typing-extensions](https://pypi.org/project/typing-extensions/)
* [operator](https://docs.python.org/3/library/operator.html)
* [langchain-google-genai](https://github.com/langchain-ai/langchain)
* [pillow](https://python-pillow.org/)
* [chromadb](https://www.trychroma.com/)
* [sentence-transformers](https://www.sbert.net/)
* [PyPDF2](https://pypdf2.readthedocs.io/)
* [pymupdf](https://pymupdf.readthedocs.io/)
* [langchain-text-splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/text_splitters/)
* [python-dotenv](https://pypi.org/project/python-dotenv/)
* [pandas](https://pandas.pydata.org/)
* [sqlite3](https://docs.python.org/3/library/sqlite3.html)

> All listed in `requirements.txt`

---

## 🔒 License

Copyright (c) 2024 Thai

This project ("SupportFlowX" and all included examples such as "CafeAgentX") is released for **educational, research, or internal evaluation purposes only**.

- **No commercial use.**
- **No redistribution, sublicensing, or use in proprietary software.**
- Modification for private/learning purposes is allowed.
- For any public deployment, commercial use, or redistribution, please contact the author for explicit written permission.

All rights reserved.

## ⭐ Credits

Built with:

* [LangGraph](https://langchain-ai.github.io/langgraph/)
* [Gradio](https://gradio.app/)
* [Google Generative AI](https://makersuite.google.com/)

---

**Ready to orchestrate your own AI support workflows?
Fork SupportFlowX, swap the agents, and build the next smart support system — with no single-agent bottleneck!**

---
