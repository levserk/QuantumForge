import os
from pathlib import Path

CHROMA_DB_PATH = Path(__file__).parent.parent / "task_3" / "chroma_db"
COLLECTION_NAME = "lotr_knowledge_base"
EMBEDDING_MODEL = "sentence-transformers/multi-qa-mpnet-base-dot-v1"

OPENAI_MODEL = "gpt-4o-mini"
OPENAI_TEMPERATURE = 0.3
OPENAI_MAX_TOKENS = 500

TOP_K_RESULTS = 3
SIMILARITY_THRESHOLD = 0.4

