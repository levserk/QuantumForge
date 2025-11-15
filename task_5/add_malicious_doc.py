import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "task_3"))
sys.path.append(str(Path(__file__).parent.parent / "task_4"))

import chromadb
from chromadb.utils import embedding_functions
import config

MALICIOUS_DOC_PATH = Path(__file__).parent / "malicious_document.txt"

def add_malicious_document():
    print("Добавление вредоносного документа в векторную базу...")
    
    chroma_client = chromadb.PersistentClient(path=str(config.CHROMA_DB_PATH))
    
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=config.EMBEDDING_MODEL,
        device='mps'
    )
    
    collection = chroma_client.get_collection(
        name=config.COLLECTION_NAME,
        embedding_function=embedding_func
    )
    
    with open(MALICIOUS_DOC_PATH, 'r', encoding='utf-8') as f:
        malicious_text = f.read()
    
    doc_title = "malicious_document.txt"
    chunk_text = f"{doc_title}. {malicious_text}"
    
    chunk_id = f"chunk_malicious_999"
    
    collection.add(
        ids=[chunk_id],
        documents=[chunk_text],
        metadatas=[{
            "source": doc_title,
            "chunk_id": 999,
            "doc_index": 999
        }]
    )
    
    print(f"✓ Вредоносный документ добавлен")
    print(f"  ID: {chunk_id}")
    print(f"  Текст: {malicious_text[:100]}...")
    print(f"✓ Всего чанков в базе: {collection.count()}")

if __name__ == "__main__":
    add_malicious_document()

