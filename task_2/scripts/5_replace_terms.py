import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import unquote

def normalize_text(text):
    """Убирает диакритические знаки (ударения) из текста"""
    return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')

def load_terms_map():
    terms_map_path = Path(__file__).parent.parent / 'terms_map.json'
    with open(terms_map_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def sort_terms_by_priority(terms_map):
    """Сортирует термины для правильного порядка замены:
    1. Сначала составные (длинные последовательности)
    2. Потом одиночные (от длинных к коротким)
    """
    compound_terms = []
    single_terms = []
    
    for term in terms_map.keys():
        if ' ' in term:
            compound_terms.append(term)
        else:
            single_terms.append(term)
    
    compound_terms.sort(key=lambda x: (len(x.split()), len(x)), reverse=True)
    single_terms.sort(key=len, reverse=True)
    
    return compound_terms + single_terms

def create_replacement_pattern(term):
    """Создаёт regex-паттерн для замены с границами слов"""
    escaped = re.escape(term)
    return r'\b' + escaped + r'\b'

def smart_replace(text, terms_map, sorted_terms):
    """Умная замена с учётом приоритета и границ слов"""
    
    for term in sorted_terms:
        if term not in terms_map:
            continue
        
        replacement = terms_map[term]
        
        pattern = create_replacement_pattern(term)
        text = re.sub(pattern, replacement, text)
        
        term_with_accent = term
        for char in term:
            if char in 'аеиоуыэяюАЕИОУЫЭЯЮ':
                term_with_accent = term.replace(char, char + '\u0301', 1)
                pattern_with_accent = create_replacement_pattern(term_with_accent)
                text = re.sub(pattern_with_accent, replacement, text)
                break
    
    return text

def extract_name_from_filename(filename):
    """Извлекает оригинальное имя из названия файла"""
    name = filename.replace('.txt', '').replace('_', ' ')
    name = unquote(name)
    return name

def generate_new_filename(original_name, terms_map, sorted_terms):
    """Генерирует новое имя файла на основе замен"""
    new_name = smart_replace(original_name, terms_map, sorted_terms)
    new_name = new_name.replace(' ', '_')
    return new_name + '.txt'

def main():
    print("=" * 80)
    print("  УМНАЯ ЗАМЕНА ТЕРМИНОВ")
    print("=" * 80)
    
    terms_map = load_terms_map()
    print(f"\n✓ Загружен словарь: {len(terms_map)} терминов")
    
    sorted_terms = sort_terms_by_priority(terms_map)
    
    compound_count = len([t for t in sorted_terms if ' ' in t])
    single_count = len(sorted_terms) - compound_count
    
    print(f"  📋 Составные термины: {compound_count}")
    print(f"  📋 Одиночные термины: {single_count}")
    
    cleaned_dir = Path(__file__).parent.parent / 'cleaned_texts'
    knowledge_base_dir = Path(__file__).parent.parent / 'knowledge_base'
    knowledge_base_dir.mkdir(exist_ok=True)
    
    existing_files = list(knowledge_base_dir.glob('*.txt'))
    for f in existing_files:
        f.unlink()
    print(f"\n🗑️  Очищена папка knowledge_base")
    
    files = sorted(cleaned_dir.glob('*.txt'))
    print(f"\n📚 Найдено файлов: {len(files)}")
    
    print("\n" + "=" * 80)
    print("ОБРАБОТКА ФАЙЛОВ")
    print("=" * 80)
    
    for i, file_path in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}]")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            original_text = f.read()
        
        replaced_text = smart_replace(original_text, terms_map, sorted_terms)
        
        original_filename = file_path.name
        original_name = extract_name_from_filename(original_filename)
        new_filename = generate_new_filename(original_name, terms_map, sorted_terms)
        
        output_path = knowledge_base_dir / new_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(replaced_text)
        
        print(f"  Было: {original_filename}")
        print(f"  Стало: {new_filename}")
        print(f"  ✓ ({len(replaced_text)} символов)")
    
    print("\n" + "=" * 80)
    print("ЗАВЕРШЕНО")
    print("=" * 80)
    print(f"✅ Обработано: {len(files)}/{len(files)} файлов")
    print(f"📁 База знаний: {knowledge_base_dir}")
    
    print("\n" + "=" * 80)
    print("ПРИМЕРЫ ЗАМЕН В ТЕКСТЕ")
    print("=" * 80)
    
    sample_file = knowledge_base_dir / new_filename
    if sample_file.exists():
        with open(sample_file, 'r', encoding='utf-8') as f:
            content = f.read()[:500]
        print(f"\nПервые 500 символов из {new_filename}:")
        print(content)

if __name__ == "__main__":
    main()

