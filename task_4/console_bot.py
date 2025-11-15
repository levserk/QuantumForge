#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from rag_bot import RAGBot

def main():
    print("=" * 80)
    print("  RAG-БОТ: ПОМОЩНИК ПО БАЗЕ ЗНАНИЙ")
    print("=" * 80)
    print()
    
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Ошибка: OPENAI_API_KEY не найден в .env файле")
        print()
        print("Создайте файл .env в папке task_4/ со следующим содержимым:")
        print("OPENAI_API_KEY=your-api-key-here")
        print()
        print("Получить API ключ: https://platform.openai.com/api-keys")
        return
    
    try:
        bot = RAGBot(api_key)
    except Exception as e:
        print(f"❌ Ошибка при инициализации бота: {e}")
        return
    
    print()
    print("🤖 RAG-бот готов к работе!")
    print()
    print("Команды:")
    print("  - Введите ваш вопрос")
    print("  - 'debug' - включить/выключить отладочную информацию")
    print("  - 'exit' или 'quit' - выход")
    print()
    print("=" * 80)
    
    debug = False
    
    while True:
        try:
            query = input("\n👤 Вы: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['exit', 'quit', 'выход']:
                print("\n👋 До свидания!")
                break
            
            if query.lower() == 'debug':
                debug = not debug
                print(f"🔧 Debug режим: {'включен' if debug else 'выключен'}")
                continue
            
            if debug:
                print("\n🔍 Поиск релевантных документов...")
            else:
                print("\n🔍 Думаю...")
            
            answer = bot.generate_answer(query, debug=debug)
            
            print(f"\n🤖 Бот:\n{answer}")
            
        except KeyboardInterrupt:
            print("\n\n👋 До свидания!")
            break
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

if __name__ == "__main__":
    main()

