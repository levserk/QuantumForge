#!/usr/bin/env python3
"""
Скрипт создания векторного индекса из базы знаний.
Использует all-mpnet-base-v2 для эмбеддингов и ChromaDB для хранения.
"""

import os
import time
from pathlib import Path
from typing import List, Dict
import chromadb
from chromadb.utils import embedding_functions
from langchain.text_splitter import RecursiveCharacterTextSplitter

print("=" * 60)
print("  СОЗДАНИЕ ВЕКТОРНОГО ИНДЕКСА")
print("=" * 60)
print()

# Конфигурация
KNOWLEDGE_BASE_DIR = Path(__file__).parent.parent / "task_2" / "knowledge_base"
CHROMA_DB_DIR = Path(__file__).parent / "chroma_db"
CHUNK_SIZE = 600
CHUNK_OVERLAP = 200
COLLECTION_NAME = "lotr_knowledge_base"
EMBEDDING_MODEL = "sentence-transformers/multi-qa-mpnet-base-dot-v1"

print(f"📁 База знаний: {KNOWLEDGE_BASE_DIR}")
print(f"💾 Индекс будет сохранен в: {CHROMA_DB_DIR}")
print(f"🤖 Модель эмбеддингов: {EMBEDDING_MODEL}")
print(f"📏 Размер чанка: {CHUNK_SIZE} символов (overlap: {CHUNK_OVERLAP})")
print()

def load_documents() -> List[Dict[str, str]]:
    """Загружает все текстовые документы из базы знаний."""
    documents = []
    txt_files = list(KNOWLEDGE_BASE_DIR.glob("*.txt"))
    
    print(f"🔍 Загрузка документов из {KNOWLEDGE_BASE_DIR.name}...")
    
    for i, filepath in enumerate(txt_files, 1):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if content.strip():
                documents.append({
                    "content": content,
                    "source": filepath.name,
                    "path": str(filepath)
                })
                
                if i % 10 == 0:
                    print(f"  [{i}/{len(txt_files)}] Загружено...")
        except Exception as e:
            print(f"  ⚠️  Ошибка при загрузке {filepath.name}: {e}")
    
    print(f"✅ Загружено {len(documents)} документов")
    return documents

def split_into_chunks(documents: List[Dict[str, str]]) -> List[Dict[str, any]]:
    """Разбивает документы на чанки."""
    print(f"\n✂️  Разбиение на чанки...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = []
    chunk_id = 0
    
    for doc_idx, doc in enumerate(documents, 1):
        doc_chunks = text_splitter.split_text(doc["content"])
        
        doc_title = doc["source"].replace('.txt', '').replace('_', ' ')
        
        for local_chunk_id, chunk_text in enumerate(doc_chunks):
            chunk_with_title = f"{doc_title}. {chunk_text}"
            
            chunks.append({
                "id": f"chunk_{chunk_id}",
                "text": chunk_with_title,
                "metadata": {
                    "source": doc["source"],
                    "chunk_id": local_chunk_id,
                    "doc_index": doc_idx - 1
                }
            })
            chunk_id += 1
        
        if doc_idx % 10 == 0:
            print(f"  [{doc_idx}/{len(documents)}] Обработано, чанков: {len(chunks)}")
    
    print(f"✅ Создано {len(chunks)} чанков из {len(documents)} документов")
    return chunks

def create_index(chunks: List[Dict[str, any]]):
    """Создает векторный индекс в ChromaDB."""
    print(f"\n🔨 Создание индекса ChromaDB...")
    
    # Инициализация ChromaDB клиента
    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    
    # Удаляем существующую коллекцию если есть
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print(f"  🗑️  Удалена старая коллекция")
    except:
        pass
    
    # Создаем embedding function
    print(f"  📥 Загрузка модели {EMBEDDING_MODEL}...")
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL,
        device='mps'
    )
    
    # Создаем коллекцию
    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_func,
        metadata={"hnsw:space": "cosine"}
    )
    
    print(f"  ✅ Коллекция '{COLLECTION_NAME}' создана")
    
    # Добавляем чанки батчами
    batch_size = 500
    total_batches = (len(chunks) + batch_size - 1) // batch_size
    
    print(f"\n  📊 Добавление {len(chunks)} чанков (батчи по {batch_size})...")
    
    start_time = time.time()
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        batch_num = i // batch_size + 1
        
        ids = [chunk["id"] for chunk in batch]
        documents = [chunk["text"] for chunk in batch]
        metadatas = [chunk["metadata"] for chunk in batch]
        
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
        if batch_num % 5 == 0 or batch_num == total_batches:
            elapsed = time.time() - start_time
            print(f"    [{batch_num}/{total_batches}] батчей добавлено ({elapsed:.1f}s)")
    
    elapsed_total = time.time() - start_time
    
    print(f"\n✅ Индекс успешно создан!")
    print(f"  ⏱️  Время генерации: {elapsed_total:.2f} секунд")
    print(f"  📦 Чанков в индексе: {collection.count()}")
    
    return collection, elapsed_total

def main():
    """Основная функция."""
    overall_start = time.time()
    
    try:
        # Шаг 1: Загрузка документов
        documents = load_documents()
        
        if not documents:
            print("❌ Нет документов для индексации!")
            return
        
        # Шаг 2: Разбиение на чанки
        chunks = split_into_chunks(documents)
        
        # Шаг 3: Создание индекса
        collection, gen_time = create_index(chunks)
        
        # Статистика
        overall_time = time.time() - overall_start
        
        print("\n" + "=" * 60)
        print("📊 ИТОГОВАЯ СТАТИСТИКА")
        print("=" * 60)
        print(f"  Модель: {EMBEDDING_MODEL}")
        print(f"  Размерность эмбеддингов: 768")
        print(f"  Документов обработано: {len(documents)}")
        print(f"  Чанков создано: {len(chunks)}")
        print(f"  Время генерации индекса: {gen_time:.2f}s")
        print(f"  Общее время: {overall_time:.2f}s")
        print(f"  Индекс сохранен в: {CHROMA_DB_DIR}")
        print("=" * 60)
        print()
        print("✨ Готово! Теперь можно запустить search_example.py")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

