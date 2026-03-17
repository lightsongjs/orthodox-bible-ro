#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apply Romanian translations to Bible pericope JSON files
"""

import json
import sys
import os
import io

# Set UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pericope_translations import PERICOPE_TRANSLATIONS

def translate_pericope_file(filepath):
    """
    Translate pericope titles in a JSON file
    Only updates titles that are currently in English (not already translated)
    """
    print(f"\n{'='*70}")
    print(f"Processing: {os.path.basename(filepath)}")
    print(f"{'='*70}")

    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Count translations
    total = len(data['pericopes'])
    updated = 0
    already_translated = 0
    missing_translation = 0
    missing_titles = []

    # Update pericopes
    for pericope in data['pericopes']:
        title_en = pericope['title_en']
        title_ro = pericope.get('title_ro', '')

        # Check if already translated (not just copy of English)
        if title_ro and title_ro != title_en:
            already_translated += 1
            continue

        # Try to translate
        if title_en in PERICOPE_TRANSLATIONS:
            new_title_ro = PERICOPE_TRANSLATIONS[title_en]
            pericope['title_ro'] = new_title_ro
            updated += 1
            # Use simple [OK] instead of checkmark for Windows console
            print(f"[OK] {pericope['pericope_id']}")
            print(f"  EN: {title_en}")
            print(f"  RO: {new_title_ro}")
        else:
            missing_translation += 1
            missing_titles.append(title_en)
            # Keep the English title as placeholder
            pericope['title_ro'] = title_en

    # Write back to file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n{'-'*70}")
    print(f"Summary for {data['name_ro']}:")
    print(f"  Total pericopes:        {total:3}")
    print(f"  Already translated:     {already_translated:3}")
    print(f"  Newly translated:       {updated:3}")
    print(f"  Missing translations:   {missing_translation:3}")

    if missing_titles:
        print(f"\n  Missing translations:")
        for title in missing_titles[:10]:
            print(f"    - {title}")
        if len(missing_titles) > 10:
            print(f"    ... and {len(missing_titles) - 10} more")

    return {
        'book': data['name_ro'],
        'total': total,
        'already_translated': already_translated,
        'updated': updated,
        'missing': missing_translation,
        'missing_titles': missing_titles
    }

def main():
    base_path = 'C:/Users/User/Documents/GitHub/orthodox_bible/bible_books_pericopes'

    files = [
        f'{base_path}/52_Matei_pericopes.json',
        f'{base_path}/53_Marcu_pericopes.json',
        f'{base_path}/54_Luca_pericopes.json',
        f'{base_path}/55_Ioan_pericopes.json',
        f'{base_path}/56_Faptele Apostolilor_pericopes.json'
    ]

    print("\n" + "="*70)
    print("Bible Pericope Title Translation - English to Romanian")
    print("Using Orthodox Romanian Bible Terminology")
    print("="*70)

    results = []
    all_missing = []
    for filepath in files:
        if os.path.exists(filepath):
            result = translate_pericope_file(filepath)
            results.append(result)
            all_missing.extend(result['missing_titles'])
        else:
            print(f"\nERROR: File not found: {filepath}")

    # Overall summary
    print("\n" + "="*70)
    print("OVERALL SUMMARY")
    print("="*70)
    print(f"{'Book':<25} | {'Total':>5} | {'Already':>7} | {'New':>5} | {'Missing':>7}")
    print("-"*70)
    for r in results:
        print(f"{r['book']:<25} | {r['total']:>5} | {r['already_translated']:>7} | {r['updated']:>5} | {r['missing']:>7}")

    total_all = sum(r['total'] for r in results)
    total_already = sum(r['already_translated'] for r in results)
    total_updated = sum(r['updated'] for r in results)
    total_missing = sum(r['missing'] for r in results)

    print("-"*70)
    print(f"{'TOTAL':<25} | {total_all:>5} | {total_already:>7} | {total_updated:>5} | {total_missing:>7}")

    if all_missing:
        print(f"\n\nTotal unique missing translations: {len(set(all_missing))}")
        print("\nFirst 20 missing translations:")
        for title in sorted(set(all_missing))[:20]:
            print(f"  - {title}")

    print("\n" + "="*70)
    print("Translation complete!")
    print("="*70)

if __name__ == '__main__':
    main()
