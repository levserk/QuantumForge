import requests
from bs4 import BeautifulSoup
import time
import os

BASE_URL = "https://lotr.fandom.com"
CATEGORIES = [
    "/ru/wiki/Категория:Персонажи",
    "/ru/wiki/Категория:Артефакты",
    "/ru/wiki/Категория:Места",
    "/ru/wiki/Категория:Эльфы",
    "/ru/wiki/Категория:Гномы",
    "/ru/wiki/Категория:Хоббиты",
    "/ru/wiki/Категория:Люди",
    "/ru/wiki/Категория:Орки",
    "/ru/wiki/Категория:Народы",
    "/ru/wiki/Категория:Королевства",
    "/ru/wiki/Категория:Битвы",
    "/ru/wiki/Категория:Оружие",
]

def get_links_from_category(category_url, max_links=25):
    links = []
    try:
        print(f"Парсинг категории: {category_url}")
        response = requests.get(BASE_URL + category_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        category_content = soup.find('div', class_='category-page__members')
        if not category_content:
            category_content = soup.find('div', class_='mw-category')
        
        if category_content:
            link_elements = category_content.find_all('a', href=True)
            
            for link in link_elements:
                href = link.get('href')
                if href and href.startswith('/ru/wiki/') and ':' not in href:
                    full_url = BASE_URL + href
                    if full_url not in links:
                        links.append(full_url)
                        print(f"  Найдена ссылка: {link.get_text(strip=True)}")
                        
                        if len(links) >= max_links:
                            break
        
        time.sleep(1)
        
    except Exception as e:
        print(f"Ошибка при парсинге {category_url}: {e}")
    
    return links

def main():
    all_links = []
    target_count = 50
    links_per_category = target_count // len(CATEGORIES) + 5
    
    print(f"Начинаю сбор ссылок. Цель: {target_count}+ статей")
    print("=" * 60)
    
    for category in CATEGORIES:
        links = get_links_from_category(category, max_links=links_per_category)
        all_links.extend(links)
        print(f"Собрано из категории: {len(links)} ссылок")
        print("-" * 60)
    
    all_links = list(set(all_links))
    
    print(f"\nВсего собрано уникальных ссылок: {len(all_links)}")
    
    output_file = os.path.join(os.path.dirname(__file__), '..', 'links.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        for link in all_links:
            f.write(link + '\n')
    
    print(f"Ссылки сохранены в: {output_file}")
    
    if len(all_links) < target_count:
        print(f"\nВНИМАНИЕ: Собрано только {len(all_links)} ссылок из {target_count}")
        print("Возможно, нужно добавить больше категорий или увеличить лимит")
    else:
        print(f"\n✓ Успешно собрано {len(all_links)} ссылок!")

if __name__ == "__main__":
    main()

