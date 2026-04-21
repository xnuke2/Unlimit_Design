import os
import re
from pathlib import Path

def process_file(filepath):
    content = filepath.read_text(encoding='utf-8')
    original = content
    
    # 1. Remove alt="?"
    content = content.replace('alt="?"', 'alt=""')
    content = content.replace('alt=?', 'alt=""')

    # 2. Remove redundant title="..." from labels
    content = re.sub(r'(<label[^>]*?)\s+title="[^"]*"([^>]*>)', r'\1\2', content)

    # 3. Remove redundant title="..." and aria-label="..." from menuLinks
    content = re.sub(r'<a([^>]*?)aria-label="Главная"([^>]*?)>', r'<a\1\2>', content)
    content = re.sub(r'<a([^>]*?)title="Гранты и меры поддержки"\s+href="grant\.html"\s+aria-label="Гранты и меры поддержки"([^>]*?)>', r'<a\1href="grant.html"\2>', content)
    content = re.sub(r'<a([^>]*?)aria-label="Популяризация науки \(в разработке\)"([^>]*?)>', r'<a\1\2>', content)
    content = re.sub(r'<a([^>]*?)aria-label="Комиссия НТР \(в разработке\)"([^>]*?)>', r'<a\1\2>', content)
    content = re.sub(r'<a([^>]*?)aria-label="Отраслевые и специальные сегменты \(в разработке\)"([^>]*?)>', r'<a\1\2>', content)
    content = re.sub(r'<a([^>]*?)aria-label="База знаний \(в разработке\)"([^>]*?)>', r'<a\1\2>', content)
    content = re.sub(r'<a([^>]*?)aria-label="Аналитика \(в разработке\)"([^>]*?)>', r'<a\1\2>', content)

    # 4. Remove redundant titles from buttons/spans that duplicate text
    content = content.replace('title="Сбросить" ', '')
    content = content.replace('title="Сформировать" ', '')
    content = content.replace('title="Подать заявку" ', '')
    content = content.replace('title="Вернуться к навигатору"', '')
    content = content.replace('title="Нажмите, чтобы скопировать прямую ссылку/электронную почту" ', '')

    # 5. Remove aria-label from <article> in grant.html (since the h2 inside provides the accessible name)
    content = re.sub(r'(<article[^>]*?)\s+aria-label="[^"]*"([^>]*>)', r'\1\2', content)

    # 6. Clean up ant-btn role="button" if it's an <a>, we can keep it, but if it's on a button it's bad.
    # Actually, the "Подробнее" is an <a> tag, so role="button" is acceptable. Let's leave it.

    if content != original:
        filepath.write_text(content, encoding='utf-8')
        print(f"Cleaned {filepath.name}")

for p in Path('.').rglob('*.html'):
    if 'node_modules' not in p.parts:
        process_file(p)
