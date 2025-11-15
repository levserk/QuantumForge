#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from rag_bot import RAGBot

def test_bot():
    print("=" * 80)
    print("  ТЕСТИРОВАНИЕ RAG-БОТА")
    print("=" * 80)
    print()
    
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Ошибка: OPENAI_API_KEY не найден в .env файле")
        return
    
    try:
        bot = RAGBot(api_key)
    except Exception as e:
        print(f"❌ Ошибка при инициализации: {e}")
        return
    
    print()
    print("=" * 80)
    print("  ЗАПУСК ТЕСТОВЫХ ЗАПРОСОВ")
    print("=" * 80)
    
    test_queries = [
        "Кто такой Биир и что с ним случилось?",
        "Кто такой Гоан и чем он известен?",
        "Что случилось с Ву?",
        "Что такое Рыин Кэен и зачем он нужен?",
        "Расскажи про Доин Каин",
        "Где находится Мо и что там произошло?",
        "Что известно о хехах?",
        "Расскажи про Беин",
        "Кто такой Гарри Поттер?",
        "Какая погода в Москве?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'=' * 80}")
        print(f"ТЕСТ {i}/{len(test_queries)}")
        print(f"{'=' * 80}")
        print(f"\n👤 Запрос: {query}")
        print("\n🔍 Обработка...")
        
        try:
            answer = bot.generate_answer(query, debug=True)
            print(f"\n🤖 Ответ:\n{answer}")
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
    
    print(f"\n{'=' * 80}")
    print("  ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 80)

if __name__ == "__main__":
    test_bot()

