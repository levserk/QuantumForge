import json
import random
from pathlib import Path
from collections import defaultdict

CONSONANTS = ['б', 'в', 'г', 'д', 'з', 'к', 'л', 'м', 'н', 'п', 'р', 'с', 'т', 'ф', 'х']
VOWELS = ['а', 'е', 'и', 'о', 'у', 'ы', 'э']
ENDINGS = ['ор', 'он', 'ир', 'ар', 'ан', 'ин', 'ен', 'эль', 'иль', 'ас', 'ос', 'ус']

def generate_fantasy_name(original_word):
    """Генерирует фэнтезийное имя на основе оригинального"""
    if not original_word or len(original_word) < 2:
        return ''.join(random.choice(CONSONANTS) + random.choice(VOWELS) for _ in range(2))
    
    is_capitalized = original_word[0].isupper()
    length_hint = len(original_word)
    
    first_char = original_word[0].lower()
    start_consonant = first_char if first_char in CONSONANTS else random.choice(CONSONANTS)
    
    syllables = max(1, (length_hint + 1) // 3)
    
    name_parts = [start_consonant + random.choice(VOWELS)]
    
    for i in range(syllables - 1):
        name_parts.append(random.choice(CONSONANTS) + random.choice(VOWELS))
    
    if length_hint > 4 and random.random() > 0.5:
        name_parts.append(random.choice(ENDINGS))
    
    name = ''.join(name_parts)
    
    return name.capitalize() if is_capitalized else name.lower()

def extract_terms_from_texts():
    """Извлекает все заглавные слова из текстов"""
    cleaned_dir = Path(__file__).parent.parent / 'cleaned_texts'
    
    terms = set()
    
    for file_path in cleaned_dir.glob('*.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        words = text.split()
        for word in words:
            clean_word = word.strip('.,;:!?()[]«»""\'')
            
            if len(clean_word) >= 3 and clean_word[0].isupper():
                terms.add(clean_word)
        
        from urllib.parse import unquote
        filename = file_path.stem
        decoded = unquote(filename)
        
        for part in decoded.replace('_', ' ').split():
            if len(part) >= 3 and part[0].isupper():
                terms.add(part)
    
    return sorted(terms)

def add_manual_races():
    """Добавляет вручную ключевые расы и их производные"""
    races = {
        'эльф': None,
        'гном': None,
        'орк': None,
        'хоббит': None,
        'энт': None
    }
    
    race_forms = {}
    
    for race in races:
        base_fantasy = generate_fantasy_name(race)
        
        race_forms[race] = base_fantasy
        race_forms[race + 'ы'] = base_fantasy + 'ы'
        race_forms[race + 'ов'] = base_fantasy + 'ов'
        race_forms[race + 'ом'] = base_fantasy + 'ом'
        race_forms[race + 'ами'] = base_fantasy + 'ами'
    
    return race_forms

def main():
    print("=" * 80)
    print("  ГЕНЕРАЦИЯ СЛОВАРЯ ФЭНТЕЗИЙНЫХ ЗАМЕН")
    print("=" * 80)
    
    print("\n🔍 Извлечение терминов из текстов...")
    terms = extract_terms_from_texts()
    print(f"✅ Извлечено: {len(terms)} уникальных терминов")
    
    print("\n🎲 Генерация фэнтезийных имён...")
    terms_map = {}
    used_names = set()
    
    for i, term in enumerate(terms, 1):
        if i % 100 == 0:
            print(f"  {i}/{len(terms)}")
        
        if ' ' in term:
            words = term.split()
            fake_words = []
            for word in words:
                fake_word = generate_fantasy_name(word)
                attempts = 0
                while fake_word in used_names and attempts < 10:
                    fake_word = generate_fantasy_name(word)
                    attempts += 1
                used_names.add(fake_word)
                fake_words.append(fake_word)
            fake_name = ' '.join(fake_words)
        else:
            fake_name = generate_fantasy_name(term)
            attempts = 0
            while fake_name in used_names and attempts < 10:
                fake_name = generate_fantasy_name(term)
                attempts += 1
            used_names.add(fake_name)
        
        terms_map[term] = fake_name
    
    print("\n🐉 Добавление рас и их производных...")
    race_forms = add_manual_races()
    terms_map.update(race_forms)
    
    if 'Нуменор' in terms_map:
        numenor_base = terms_map['Нуменор']
        terms_map['нуменорцы'] = numenor_base.lower() + 'цы'
        terms_map['нуменорец'] = numenor_base.lower() + 'ец'
        terms_map['нуменорский'] = numenor_base.lower() + 'ский'
        terms_map['Нуменорцы'] = numenor_base + 'цы'
        print(f"  + нуменорцы → {terms_map['нуменорцы']}")
    
    output_path = Path(__file__).parent.parent / 'terms_map.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(terms_map, f, ensure_ascii=False, indent=2, sort_keys=True)
    
    print(f"\n✅ Сохранено: {output_path}")
    print(f"📚 Всего: {len(terms_map)} замен")
    
    print("\n" + "=" * 80)
    print("  ПРИМЕРЫ ЗАМЕН")
    print("=" * 80)
    
    examples = [
        'Единое Кольцо', 'Нуменор', 'нуменорцы', 
        'эльф', 'эльфы', 'гном', 'гномы', 'орк', 'орки'
    ]
    
    for term in examples:
        if term in terms_map:
            print(f"  ✅ {term:20} → {terms_map[term]}")

if __name__ == "__main__":
    random.seed(42)
    main()

