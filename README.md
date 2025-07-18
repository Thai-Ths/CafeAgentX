# SupportFlowX 🚀  
*Agent Orchestration Framework for Scalable, Modular Chatbots*

> **Example Project:** CafeAgentX ☕ – Café Assistant Demo

---

## Overview

**SupportFlowX** is a flexible, agentic orchestration framework designed to build scalable, multi-agent AI assistants.  
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

![Workflow](https://github.com/user-attachments/assets/9cb92dc7-0b54-4447-8fcc-0b29aaccc323)
</details>

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

The core logic is in `core.py`, which handles orchestration and routing between specialized agents.
- All main configuration is in `config.py`.
- Database files for both structured data and RAG are inside `data/` and `knowledge-base/`.
- Each agent is modular and extensible (see `AG00_*`, `AG01_*`, ...).

<details>
<summary><b>Click to view directory structure</b></summary>

```
.
├── data/                      # Contains database.db, and setup scripts
├── image/                     # Images for Gradio UI
├── knowledge-base/            # RAG source documents, and setup scripts
├── landscape\_cafe/           # RAG database
├── AG00\_intake\_agent.py
├── AG01\_cafe\_bot.py
├── AG02\_database\_agent.py
├── AG03\_aggregator\_agent.py
├── core.py                    # Main orchestration entrypoint
├── config.py                  # Central configuration
├── cafe\_theme.css            # Custom Gradio theme
├── requirements.txt
├── README.md
├── demo.ipynb

```

</details>

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

* Place your knowledge base (RAG documents) in `/knowledge-base`
* Place your sample DB as `/data/database.db` (or as configured)
* Place images in `/image/`
* **Get a Gemini API Key**: [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey) (for Google Generative AI access)

### 4. Run the Demo App

```bash
python core.py
```

Then open the local Gradio UI in your browser!

---

## 🛠️ Customization & Scaling

* **Add new skills:** Create new agent modules (see AGXX\_\*.py), import and register in `core.py`.
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
> *(See attached diagram / image in repo for orchestration flow)*

---

## 📦 Requirements

* Python 3.8+
* [gradio](https://gradio.app/)
* [langgraph](https://github.com/langchain-ai/langgraph)
* [langchain](https://github.com/langchain-ai/langchain)
* [langchain-google-genai](https://github.com/langchain-ai/langchain)
* [pillow](https://python-pillow.org/)
* [sqlite3](https://docs.python.org/3/library/sqlite3.html)
* [typing-extensions](https://pypi.org/project/typing-extensions/)

> All listed in `requirements.txt`

---

## 📁 Files Required for Deployment

* `core.py`
* `config.py`
* `requirements.txt`
* `/data/database.db`
* `/knowledge-base/`
* `/image/landscape_icon.jpg`
* `/image/landscape_cover.jpg`
* `cafe_theme.css`
* All `AG*.py` agent files

---

## 🔒 License

```
Copyright (c) 2024 [Your Name or Organization]

This project ("SupportFlowX" and all included examples such as "CafeAgentX") is released for **educational, research, or internal evaluation purposes only**.

- **No commercial use.**
- **No redistribution, sublicensing, or use in proprietary software.**
- Modification for private/learning purposes is allowed.
- For any public deployment, commercial use, or redistribution, please contact the author for explicit written permission.

All rights reserved.
```

## ⭐ Credits

Built with:

* [LangGraph](https://langchain-ai.github.io/langgraph/)
* [Gradio](https://gradio.app/)
* [Google Generative AI](https://makersuite.google.com/)

---

**Ready to orchestrate your own AI support workflows?
Fork SupportFlowX, swap the agents, and build the next smart support system — with no single-agent bottleneck!**

---
