#!/usr/bin/env python3

from pathlib import Path
import re

html_path = Path('grant.html')
html = html_path.read_text(encoding='utf-8')

# Replace the entire pagination block
start_marker = '<nav aria-label="Пагинация по результатам поиска">'
end_marker = '</nav>'
start_idx = html.find(start_marker)

if start_idx != -1:
    end_idx = html.find(end_marker, start_idx) + len(end_marker)
    
    new_pagination = '''<nav aria-label="Пагинация по результатам поиска">
    <ul class="ant-pagination" style="display: flex; list-style: none; padding: 0; margin: 16px 0; gap: 8px; align-items: center;">
        <li><span aria-disabled="true" aria-label="Предыдущая страница недоступна" style="color: #ccc; cursor: not-allowed; padding: 4px 8px;">Назад</span></li>
        <li><a href="?page=1" aria-current="page" aria-label="Текущая страница 1" style="background: #0067ad; color: #fff; padding: 4px 8px; border-radius: 4px; text-decoration: none;">1</a></li>
        <li><a href="?page=2" aria-label="Перейти на страницу 2" style="padding: 4px 8px; text-decoration: none; color: #0067ad;">2</a></li>
        <li><a href="?page=3" aria-label="Перейти на страницу 3" style="padding: 4px 8px; text-decoration: none; color: #0067ad;">3</a></li>
        <li><a href="?page=4" aria-label="Перейти на страницу 4" style="padding: 4px 8px; text-decoration: none; color: #0067ad;">4</a></li>
        <li><a href="?page=5" aria-label="Перейти на страницу 5" style="padding: 4px 8px; text-decoration: none; color: #0067ad;">5</a></li>
        <li><span aria-hidden="true" style="padding: 4px 8px;">...</span></li>
        <li><a href="?page=123" aria-label="Перейти на страницу 123" style="padding: 4px 8px; text-decoration: none; color: #0067ad;">123</a></li>
        <li><a href="?page=2" aria-label="Следующая страница" style="padding: 4px 8px; text-decoration: none; color: #0067ad;">Вперед</a></li>
    </ul>
</nav>'''
    
    html = html[:start_idx] + new_pagination + html[end_idx:]

html_path.write_text(html, encoding='utf-8')
print("Pagination replaced")
