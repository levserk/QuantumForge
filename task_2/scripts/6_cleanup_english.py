import re
from pathlib import Path

def clean_text(text):
    """Удаляет английские названия и упоминания LOTR из текста"""
    
    text = re.sub(r'\(\s*англ\.\s*[A-Za-z\s\-éúíóáàèòùìâêîôûäëïöüÿæœçñ]+\s*\)', '', text, flags=re.IGNORECASE)
    
    text = re.sub(r'\(\s*кв\.\s*[A-Za-z\s\-éúíóáàèòùìâêîôûäëïöüÿæœçñ]+\s*\|\s*рус\.\s*[^)]+\)', '', text, flags=re.IGNORECASE)
    
    text = re.sub(r'\(\s*синд\.\s*[A-Za-z\s\-éúíóáàèòùìâêîôûäëïöüÿæœçñ]+\s*\)', '', text, flags=re.IGNORECASE)
    
    text = re.sub(r'\(\s*[A-Za-z\s\-éúíóáàèòùìâêîôûäëïöüÿæœçñ]+\s*\)', '', text, flags=re.IGNORECASE)
    
    text = re.sub(r'[A-Za-zéúíóáàèòùìâêîôûäëïöüÿæœçñ]{3,}', '', text, flags=re.IGNORECASE)
    
    text = re.sub(r'  +', ' ', text)
    
    text = re.sub(r'\(\s*\)', '', text)
    
    text = re.sub(r'«\s*»', '', text)
    
    return text.strip()

def main():
    kb_dir = Path(__file__).parent.parent / 'knowledge_base'
    
    print("=" * 80)
    print("  ФИНАЛЬНАЯ ЧИСТКА ТЕКСТОВ")
    print("=" * 80)
    
    files = sorted(kb_dir.glob('*.txt'))
    print(f"\n📚 Найдено файлов: {len(files)}")
    
    for i, file_path in enumerate(files, 1):
        with open(file_path, 'r', encoding='utf-8') as f:
            original_text = f.read()
        
        cleaned_text = clean_text(original_text)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        
        if (i % 10 == 0) or (i == len(files)):
            print(f"  [{i}/{len(files)}] {file_path.name}")
    
    print("\n✅ Завершено")
    
    print("\n" + "=" * 80)
    print("ПРИМЕР ФИНАЛЬНОГО ТЕКСТА")
    print("=" * 80)
    
    sample_file = list(kb_dir.glob('*.txt'))[0]
    with open(sample_file, 'r', encoding='utf-8') as f:
        content = f.read()[:600]
    print(f"\nПервые 600 символов из {sample_file.name}:")
    print(content)

if __name__ == "__main__":
    main()

