#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
import codecs

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

files = [
    'bible_books_pericopes/01_Facerea_pericopes.json',
    'bible_books_pericopes/02_Ieșirea_pericopes.json',
    'bible_books_pericopes/03_Leviticul_pericopes.json',
    'bible_books_pericopes/04_Numerii_pericopes.json',
    'bible_books_pericopes/05_Deuteronomul_pericopes.json'
]

total_pericopes = 0
translated = 0
untranslated = 0

for file_path in files:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    book_name = data['name_ro']
    pericope_count = len(data['pericopes'])
    total_pericopes += pericope_count

    untrans_in_book = 0
    trans_in_book = 0

    for p in data['pericopes']:
        if p['title_en'] == p['title_ro']:
            untranslated += 1
            untrans_in_book += 1
        else:
            translated += 1
            trans_in_book += 1

    status = "✓ COMPLETE" if untrans_in_book == 0 else f"✗ {untrans_in_book} untranslated"
    print(f"{book_name}: {trans_in_book}/{pericope_count} translated - {status}")

print(f"\n{'='*60}")
print(f"TOTAL: {translated}/{total_pericopes} translated")
if untranslated == 0:
    print("✓ ALL TRANSLATIONS COMPLETE!")
else:
    print(f"✗ {untranslated} titles still need translation")
