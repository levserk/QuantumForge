import requests
import time
import os
from urllib.parse import quote

def download_page(url, output_dir):
    try:
        page_name = url.split('/wiki/')[-1]
        filename = f"{page_name}.html"
        filepath = os.path.join(output_dir, filename)
        
        if os.path.exists(filepath):
            print(f"Пропуск (уже есть): {url}")
            return True
        
        print(f"Скачивание: {url}")
        
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"  ✓ Сохранено: {filename}")
        return True
        
    except Exception as e:
        print(f"  ✗ Ошибка: {e}")
        return False

def main():
    script_dir = os.path.dirname(__file__)
    links_file = os.path.join(script_dir, '..', 'links.txt')
    output_dir = os.path.join(script_dir, '..', 'raw_html')
    
    if not os.path.exists(links_file):
        print(f"Ошибка: файл {links_file} не найден")
        print("Сначала запустите 1_crawl_links.py")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    with open(links_file, 'r', encoding='utf-8') as f:
        links = [line.strip() for line in f if line.strip()]
    
    print(f"Найдено {len(links)} ссылок для скачивания")
    print("=" * 60)
    
    success_count = 0
    failed_count = 0
    
    for i, link in enumerate(links, 1):
        print(f"\n[{i}/{len(links)}]")
        
        if download_page(link, output_dir):
            success_count += 1
        else:
            failed_count += 1
        
        time.sleep(1.5)
    
    print("\n" + "=" * 60)
    print(f"Завершено!")
    print(f"  Успешно скачано: {success_count}")
    print(f"  Ошибок: {failed_count}")
    print(f"  Файлы сохранены в: {output_dir}")

if __name__ == "__main__":
    main()

