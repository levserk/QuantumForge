#!/usr/bin/env python3

import json
import time
import shutil
from pathlib import Path
from typing import List, Dict, Tuple
import chromadb
from chromadb.utils import embedding_functions
from langchain.text_splitter import RecursiveCharacterTextSplitter

KNOWLEDGE_BASE_DIR = Path(__file__).parent.parent / "task_2" / "knowledge_base"
CHROMA_DB_BASE_DIR = Path(__file__).parent / "chroma_db_benchmark"
TEST_QUERIES_FILE = Path(__file__).parent / "test_queries.json"

MODELS = [
    "sentence-transformers/all-mpnet-base-v2",
    "sentence-transformers/multi-qa-mpnet-base-dot-v1",
    "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
]

CHUNK_CONFIGS = [
    {"size": 1000, "overlap": 200, "name": "Baseline"},
    {"size": 1000, "overlap": 400, "name": "High overlap"},
    {"size": 600, "overlap": 200, "name": "Small chunks"},
    {"size": 600, "overlap": 300, "name": "Small + high"}
]

def load_test_queries() -> List[Dict]:
    with open(TEST_QUERIES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_documents() -> List[Dict[str, str]]:
    documents = []
    txt_files = list(KNOWLEDGE_BASE_DIR.glob("*.txt"))
    
    for filepath in txt_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            if content.strip():
                documents.append({
                    "content": content,
                    "source": filepath.name,
                })
        except Exception as e:
            pass
    
    return documents

def split_into_chunks(documents: List[Dict[str, str]], chunk_size: int, chunk_overlap: int) -> List[Dict]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = []
    chunk_id = 0
    
    for doc_idx, doc in enumerate(documents):
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
                    "doc_index": doc_idx
                }
            })
            chunk_id += 1
    
    return chunks

def create_index(chunks: List[Dict], model_name: str, config_id: int) -> chromadb.Collection:
    chroma_db_dir = CHROMA_DB_BASE_DIR / f"test_{config_id}"
    
    if chroma_db_dir.exists():
        shutil.rmtree(chroma_db_dir)
    chroma_db_dir.mkdir(parents=True, exist_ok=True)
    
    client = chromadb.PersistentClient(path=str(chroma_db_dir))
    
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=model_name,
        device='mps'
    )
    
    collection_name = f"kb_test_{config_id}"
    
    collection = client.create_collection(
        name=collection_name,
        embedding_function=embedding_func,
        metadata={"hnsw:space": "cosine"}
    )
    
    batch_size = 500
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        
        ids = [chunk["id"] for chunk in batch]
        documents = [chunk["text"] for chunk in batch]
        metadatas = [chunk["metadata"] for chunk in batch]
        
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
    
    return collection

def search_query(collection: chromadb.Collection, query: str, top_k: int = 3) -> List[Dict]:
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    
    search_results = []
    if results['documents'] and results['documents'][0]:
        for i in range(len(results['documents'][0])):
            search_results.append({
                "text": results['documents'][0][i],
                "source": results['metadatas'][0][i]['source'],
                "similarity": 1 - results['distances'][0][i]
            })
    
    return search_results

def evaluate_configuration(model_name: str, chunk_size: int, chunk_overlap: int, config_name: str, config_id: int, test_queries: List[Dict]) -> Dict:
    print(f"\n{'='*80}")
    print(f"ТЕСТ: {model_name}")
    print(f"Chunk size: {chunk_size}, overlap: {chunk_overlap} ({config_name})")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    documents = load_documents()
    print(f"Загружено документов: {len(documents)}")
    
    chunks = split_into_chunks(documents, chunk_size, chunk_overlap)
    print(f"Создано чанков: {len(chunks)}")
    
    print("Создание индекса...")
    collection = create_index(chunks, model_name, config_id)
    index_time = time.time() - start_time
    print(f"Индекс создан за {index_time:.2f}s")
    
    recall_at_1 = 0
    recall_at_3 = 0
    similarities = []
    
    print("\nТестирование запросов:")
    for i, test in enumerate(test_queries, 1):
        query = test["query"]
        expected = test["expected_file"]
        
        results = search_query(collection, query, top_k=3)
        
        found_at_1 = False
        found_at_3 = False
        
        if results:
            top1_source = results[0]["source"]
            top1_sim = results[0]["similarity"]
            similarities.append(top1_sim)
            
            if top1_source == expected:
                recall_at_1 += 1
                found_at_1 = True
                found_at_3 = True
            else:
                for r in results:
                    if r["source"] == expected:
                        found_at_3 = True
                        break
            
            if found_at_3:
                recall_at_3 += 1
            
            status = "✓" if found_at_1 else ("~" if found_at_3 else "✗")
            print(f"  [{i}] {status} '{query}' → {top1_source} (sim: {top1_sim:.3f})")
    
    recall_1_pct = (recall_at_1 / len(test_queries)) * 100
    recall_3_pct = (recall_at_3 / len(test_queries)) * 100
    avg_sim = sum(similarities) / len(similarities) if similarities else 0
    
    results = {
        "model": model_name,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "recall_at_1": recall_1_pct,
        "recall_at_3": recall_3_pct,
        "avg_similarity": avg_sim,
        "index_time": index_time,
        "num_chunks": len(chunks)
    }
    
    print(f"\nРезультаты:")
    print(f"  Recall@1: {recall_1_pct:.1f}%")
    print(f"  Recall@3: {recall_3_pct:.1f}%")
    print(f"  Avg similarity: {avg_sim:.3f}")
    
    return results

def main():
    print("="*80)
    print("БЕНЧМАРК ВЕКТОРНОГО ПОИСКА")
    print("="*80)
    
    test_queries = load_test_queries()
    print(f"\nЗагружено тестовых запросов: {len(test_queries)}")
    
    all_results = []
    config_id = 0
    
    for model in MODELS:
        for config in CHUNK_CONFIGS:
            try:
                result = evaluate_configuration(
                    model_name=model,
                    chunk_size=config["size"],
                    chunk_overlap=config["overlap"],
                    config_name=config["name"],
                    config_id=config_id,
                    test_queries=test_queries
                )
                result["config_name"] = config["name"]
                all_results.append(result)
                config_id += 1
            except Exception as e:
                print(f"\n❌ Ошибка: {e}")
                import traceback
                traceback.print_exc()
                config_id += 1
    
    print("\n" + "="*80)
    print("ИТОГОВАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ")
    print("="*80)
    print()
    
    all_results.sort(key=lambda x: (x["recall_at_3"], x["recall_at_1"], x["avg_similarity"]), reverse=True)
    
    print(f"{'Модель':<50} {'Config':<15} {'R@1':<8} {'R@3':<8} {'Sim':<8} {'Time':<8}")
    print("-"*100)
    
    for r in all_results:
        model_short = r["model"].split("/")[-1][:48]
        print(f"{model_short:<50} {r['config_name']:<15} {r['recall_at_1']:>6.1f}% {r['recall_at_3']:>6.1f}% {r['avg_similarity']:>6.3f} {r['index_time']:>6.1f}s")
    
    print()
    print("="*80)
    best = all_results[0]
    print("ЛУЧШАЯ КОНФИГУРАЦИЯ:")
    print(f"  Модель: {best['model']}")
    print(f"  Chunk size: {best['chunk_size']}, overlap: {best['chunk_overlap']}")
    print(f"  Recall@1: {best['recall_at_1']:.1f}%")
    print(f"  Recall@3: {best['recall_at_3']:.1f}%")
    print(f"  Avg similarity: {best['avg_similarity']:.3f}")
    print("="*80)
    
    with open(Path(__file__).parent / "benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Результаты сохранены в benchmark_results.json")

if __name__ == "__main__":
    main()

