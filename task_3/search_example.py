#!/usr/bin/env python3
"""
Примеры поиска по векторному индексу.
Демонстрирует работу семантического поиска с замененными терминами.
"""

import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path

# Конфигурация
CHROMA_DB_DIR = Path(__file__).parent / "chroma_db"
COLLECTION_NAME = "lotr_knowledge_base"
EMBEDDING_MODEL = "sentence-transformers/multi-qa-mpnet-base-dot-v1"

# Тестовые запросы с замененными именами
TEST_QUERIES = [
    {
        "query": "Кто такой Биир?",
        "description": "Поиск по персонажу (Балин → Биир)"
    },
    {
        "query": "Расскажи про Саена и его планы",
        "description": "Поиск по антагонисту (Саурон → Саен)"
    },
    {
        "query": "Что такое Рыин Кэен?",
        "description": "Поиск по артефакту (Единое Кольцо → Рыин Кэен)"
    },
    {
        "query": "Расскажи про хехов",
        "description": "Поиск по расе (эльфы → хехы)"
    },
    {
        "query": "Что известно о гызах?",
        "description": "Поиск по расе (гномы → гызы)"
    }
]

def search_query(collection, query: str, n_results: int = 3):
    """Выполняет семантический поиск по запросу."""
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results

def print_results(query_info: dict, results: dict):
    """Форматирует и выводит результаты поиска."""
    print(f"\n{'=' * 80}")
    print(f"🔍 Запрос: {query_info['query']}")
    print(f"   ({query_info['description']})")
    print(f"{'=' * 80}")
    
    if not results['documents'] or not results['documents'][0]:
        print("   Ничего не найдено")
        return
    
    documents = results['documents'][0]
    metadatas = results['metadatas'][0]
    distances = results['distances'][0]
    
    for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances), 1):
        # Расчет similarity score (ChromaDB возвращает L2 distance)
        # Меньше distance = выше релевантность
        similarity = 1 / (1 + dist)
        
        print(f"\n📄 Результат {i}:")
        print(f"   Релевантность: {similarity:.3f} (distance: {dist:.3f})")
        print(f"   Источник: {meta.get('source', 'unknown')}")
        print(f"   Чанк ID: {meta.get('chunk_id', 'unknown')}")
        print(f"\n   Текст:")
        
        # Выводим текст с отступом
        lines = doc.split('\n')
        for line in lines[:5]:  # Первые 5 строк
            if line.strip():
                print(f"   {line[:120]}{'...' if len(line) > 120 else ''}")
        
        if len(lines) > 5:
            print(f"   ... (еще {len(lines) - 5} строк)")

def main():
    """Основная функция."""
    print("=" * 80)
    print("  ПРИМЕРЫ СЕМАНТИЧЕСКОГО ПОИСКА")
    print("=" * 80)
    print()
    print(f"📁 Индекс: {CHROMA_DB_DIR}")
    print(f"🤖 Модель: {EMBEDDING_MODEL}")
    
    # Проверяем наличие индекса
    if not CHROMA_DB_DIR.exists():
        print(f"\n❌ Ошибка: индекс не найден в {CHROMA_DB_DIR}")
        print("   Сначала запустите build_index.py")
        return
    
    try:
        # Подключаемся к ChromaDB
        print(f"\n🔌 Подключение к индексу...")
        client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
        
        # Инициализируем embedding function
        embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )
        
        # Получаем коллекцию
        collection = client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_func
        )
        
        print(f"✅ Коллекция загружена")
        print(f"   Чанков в индексе: {collection.count()}")
        
        # Выполняем тестовые запросы
        for query_info in TEST_QUERIES:
            results = search_query(collection, query_info['query'], n_results=3)
            print_results(query_info, results)
        
        print(f"\n{'=' * 80}")
        print("✨ Все запросы выполнены!")
        print("=" * 80)
        print()
        print("💡 Попробуйте свои запросы:")
        print("   - Используйте замененные имена из knowledge_base")
        print("   - Семантический поиск найдет релевантные фрагменты")
        print("   - Чем меньше distance, тем выше релевантность")
        print()
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

