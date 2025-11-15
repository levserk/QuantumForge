import os
from bs4 import BeautifulSoup
import re
from urllib.parse import unquote

def clean_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
        tag.decompose()
    
    for tag in soup.find_all(class_=re.compile(r'(navigation|sidebar|footer|header|menu|ad|advertisement|infobox|navbox|toc|reference|gallery)')):
        tag.decompose()
    
    for tag in soup.find_all(id=re.compile(r'(navigation|sidebar|footer|header|menu|ad|toc)')):
        tag.decompose()
    
    main_content = soup.find('div', class_='mw-parser-output')
    if not main_content:
        main_content = soup.find('article')
    if not main_content:
        main_content = soup.find('main')
    if not main_content:
        main_content = soup.find('body')
    
    if main_content:
        for tag in main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
            tag.append('\n')
        
        text = main_content.get_text(separator=' ', strip=True)
    else:
        text = soup.get_text(separator=' ', strip=True)
    
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r' ([,.:;!?])', r'\1', text)
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\[править.*?\]', '', text)
    text = text.replace('[править]', '').replace('[edit]', '')
    
    paragraphs = [p.strip() for p in text.split('\n') if p.strip() and len(p.strip()) > 20]
    text = '\n\n'.join(paragraphs)
    
    return text

def main():
    script_dir = os.path.dirname(__file__)
    input_dir = os.path.join(script_dir, '..', 'raw_html')
    output_dir = os.path.join(script_dir, '..', 'cleaned_texts')
    
    if not os.path.exists(input_dir):
        print(f"Ошибка: папка {input_dir} не найдена")
        print("Сначала запустите 2_download_pages.py")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    html_files = [f for f in os.listdir(input_dir) if f.endswith('.html')]
    
    if not html_files:
        print(f"В папке {input_dir} не найдено HTML файлов")
        return
    
    print(f"Найдено {len(html_files)} HTML файлов для обработки")
    print("=" * 60)
    
    success_count = 0
    
    for i, filename in enumerate(html_files, 1):
        decoded_name = unquote(filename)
        print(f"[{i}/{len(html_files)}] Обработка: {decoded_name}")
        
        try:
            input_path = os.path.join(input_dir, filename)
            
            with open(input_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            cleaned_text = clean_html(html_content)
            
            txt_filename = unquote(filename).replace('.html', '.txt')
            output_path = os.path.join(output_dir, txt_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
            
            print(f"  ✓ Сохранено: {txt_filename} ({len(cleaned_text)} символов)")
            success_count += 1
            
        except Exception as e:
            print(f"  ✗ Ошибка: {e}")
    
    print("\n" + "=" * 60)
    print(f"Завершено!")
    print(f"  Обработано файлов: {success_count}/{len(html_files)}")
    print(f"  Файлы сохранены в: {output_dir}")

if __name__ == "__main__":
    main()

