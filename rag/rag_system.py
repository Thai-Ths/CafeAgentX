import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from sentence_transformers import SentenceTransformer
import PyPDF2
import fitz  # PyMuPDF
from langchain_text_splitters import CharacterTextSplitter
from config import settings

class RAGSystem:
    """
    Robust RAG (Retrieval-Augmented Generation) System.
    All paths, collection, and model names are configurable via config.settings.
    Emoji are used in logs for user feedback.
    """
    def __init__(
        self,
        knowledge_base_path: str = None,
        collection_name: str = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        db_path: str = None,
        embedding_model_name: str = None
    ):
        # Use config if not provided
        self.knowledge_base_path = Path(knowledge_base_path or settings.KNOWLEDGE_BASE_PATH)
        self.collection_name = collection_name or settings.COLLECTION_NAME
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.db_path = str(db_path or settings.EMBEDDING_PATH)
        self.embedding_model_name = embedding_model_name or settings.EMBEDDING_MODEL_NAME

        print(f"🔄 Loading embedding model: {self.embedding_model_name}")
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        self.embedding_dimension = len(self.embedding_model.encode(["test"], convert_to_tensor=False)[0])
        print(f"📏 Model dimension: {self.embedding_dimension}")

        print("🔄 Initializing ChromaDB...")
        self.chroma_client = chromadb.PersistentClient(path=self.db_path)
        self.collection = self._get_or_create_collection()
        print(f"✅ Robust RAG System initialized!")

    def _get_or_create_collection(self):
        """Check if collection exists and is compatible, otherwise recreate."""
        try:
            colls = self.chroma_client.list_collections()
            col_exists = any(c.name == self.collection_name for c in colls)
            if col_exists:
                col = self.chroma_client.get_collection(self.collection_name)
                if col.count() > 0:
                    try:
                        test_vec = self.embedding_model.encode(["test"], convert_to_tensor=False)[0].tolist()
                        col.query(query_embeddings=[test_vec], n_results=1)
                        print("✅ Existing collection is compatible.")
                        return col
                    except Exception as e:
                        if "dimension" in str(e).lower():
                            print(f"⚠️ Dimension mismatch: {e}")
                print("🗑️ Recreating collection...")
                self.chroma_client.delete_collection(self.collection_name)
            # Create new collection
            print("🆕 Creating new collection...")
            return self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={
                    "hnsw:space": "cosine",
                    "model_name": self.embedding_model_name,
                    "dimension": self.embedding_dimension
                }
            )
        except Exception as e:
            print(f"❌ Error managing collection: {e}")
            raise

    def build_knowledge_base(self) -> None:
        """Create knowledge base from source files."""
        print("🚀 Building knowledge base...")
        start = time.time()
        self.clear_database()
        chunks = self._process_documents()
        if not chunks:
            print("❌ No documents processed!")
            return
        self._create_and_save_embeddings(chunks)
        print(f"🎉 Knowledge base built in {time.time() - start:.2f}s!")
        self.show_database_stats()

    def _process_documents(self) -> List[Dict[str, Any]]:
        if not self.knowledge_base_path.exists():
            print(f"❌ Knowledge base not found: {self.knowledge_base_path}")
            return []
        chunks = []
        exts = ['.md', '.txt', '.pdf']
        for root, _, files in os.walk(self.knowledge_base_path):
            root_path = Path(root)
            category = root_path.relative_to(self.knowledge_base_path).parts[0] if root_path != self.knowledge_base_path else "root"
            for file in files:
                file_path = root_path / file
                if file_path.suffix.lower() in exts:
                    content = self._read_file_content(file_path)
                    if content:
                        chunks += self._create_chunks_from_text(content, str(file_path), category, file_path.name)
                        print(f"✅ Processed {file_path.name}: {len(chunks)} chunks (running total)")
        print(f"📊 Total chunks created: {len(chunks)}")
        return chunks

    def _create_and_save_embeddings(self, chunks: List[Dict[str, Any]]) -> None:
        texts = [c['text'] for c in chunks]
        ids = [c['id'] for c in chunks]
        metas = [c['metadata'] for c in chunks]
        print(f"🔮 Generating embeddings for {len(texts)} chunks...")
        embeddings = self.embedding_model.encode(texts, batch_size=16, show_progress_bar=True, convert_to_tensor=False)
        assert len(embeddings[0]) == self.embedding_dimension, "Embedding dimension mismatch"
        print("💾 Saving to ChromaDB...")
        self.collection.add(
            embeddings=[e.tolist() if hasattr(e, "tolist") else list(e) for e in embeddings],
            documents=texts,
            metadatas=metas,
            ids=ids
        )
        print("✅ Saved to ChromaDB!")

    def _read_file_content(self, file_path: Path) -> str:
        try:
            if file_path.suffix.lower() == '.pdf':
                try:
                    with fitz.open(str(file_path)) as doc:
                        return "".join(page.get_text() for page in doc)
                except Exception:
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        return "".join(page.extract_text() for page in reader.pages)
            else:
                for enc in ['utf-8', 'utf-8-sig', 'cp874', 'latin-1']:
                    try:
                        with open(file_path, 'r', encoding=enc) as f:
                            return f.read()
                    except Exception:
                        continue
        except Exception as e:
            print(f"❌ Error reading {file_path.name}: {e}")
        return ""

    def _create_chunks_from_text(self, text: str, source: str, category: str, filename: str) -> List[Dict[str, Any]]:
        splitter = CharacterTextSplitter(
            separator="---",
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
        chunks_text = splitter.split_text(text)
        return [
            {
                'id': f"{category}_{Path(filename).stem}_{i}",
                'text': chunk.strip(),
                'metadata': {
                    'source': source,
                    'category': category,
                    'chunk_id': f"{category}_{Path(filename).stem}_{i}",
                    'chunk_number': i,
                    'filename': filename
                }
            }
            for i, chunk in enumerate(chunks_text)
        ]

    def query(self, query_text: str, top_k: int = 5, category_filter: Optional[str] = None) -> str:
        print(f"🔍 Querying: '{query_text[:50]}...'")
        query_embedding = self.embedding_model.encode([query_text], convert_to_tensor=False)[0]
        where_clause = {"category": category_filter} if category_filter else None
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist() if hasattr(query_embedding, "tolist") else list(query_embedding)],
            n_results=top_k,
            where=where_clause
        )
        if not results['documents'][0]:
            return "No relevant information found."
        return "\n---\n".join(
            f"[Context {i+1}]\nSource: {m['filename']} (Category: {m['category']})\nContent: {doc.strip()}\n"
            for i, (doc, m) in enumerate(zip(results['documents'][0], results['metadatas'][0]))
        )

    def show_database_stats(self) -> None:
        try:
            count = self.collection.count()
            meta = self.collection.metadata
            print(f"\n📊 Database Stats:")
            print(f"   Total chunks: {count}")
            print(f"   Model: {meta.get('model_name', 'Unknown')}")
            print(f"   Dimension: {meta.get('dimension', 'Unknown')}")
            if count > 0:
                all_results = self.collection.get()
                categories = {}
                for m in all_results['metadatas']:
                    categories[m['category']] = categories.get(m['category'], 0) + 1
                print(f"   Categories: {len(categories)}")
        except Exception as e:
            print(f"❌ Error getting stats: {e}")

    def clear_database(self) -> None:
        print("🗑️ Clearing database...")
        try:
            self.chroma_client.delete_collection(self.collection_name)
            self.collection = self._get_or_create_collection()
            print("✅ Database cleared!")
        except Exception as e:
            print(f"❌ Error clearing database: {e}")

if __name__ == "__main__":
    rag = RAGSystem()  # Uses config.settings by default
    rag.build_knowledge_base()