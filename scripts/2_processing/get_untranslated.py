import json
import os

base_path = r"bible_books_pericopes"
files = [
    "01_Facerea_pericopes.json",
    "02_Ieșirea_pericopes.json",
    "03_Leviticul_pericopes.json",
    "04_Numerii_pericopes.json",
    "05_Deuteronomul_pericopes.json"
]

not_found = []
for filename in files:
    file_path = os.path.join(base_path, filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for p in data['pericopes']:
        if p['title_en'] == p['title_ro']:  # Not translated yet
            not_found.append(p['title_en'])

for title in sorted(set(not_found)):
    print(f'"{title}"')
