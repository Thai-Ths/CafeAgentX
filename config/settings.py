import os
from pathlib import Path

# Debug mode
DEBUG = True

# Base directory
BASE_DIR = Path(__file__).parent.parent.resolve()

# Path settings
ASSETS_DIR = BASE_DIR / "assets"
DATABASE_DIR = BASE_DIR / "database"
RAG_DIR = BASE_DIR / "rag"
UI_DIR = BASE_DIR / "ui"

# Database
DATABASE_PATH = DATABASE_DIR / "database.db"

# RAG/Embedding
KNOWLEDGE_BASE_PATH = ASSETS_DIR / "knowledge_base"
EMBEDDING_PATH = RAG_DIR / "embedding"
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
COLLECTION_NAME = "landscape_cafe"

# Gradio UI
APP_TITLE = "Landscape Cafe & Eatery Chatbot"

# API/LLM
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash-preview-05-20"

# Other settings can be added here 