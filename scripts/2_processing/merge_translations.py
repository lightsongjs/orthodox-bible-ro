#!/usr/bin/env python3
"""
Merge translation files from multiple agents into one master dictionary.
"""

import json
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def merge_translation_files():
    """Merge all translation_*.json files into one master dictionary."""

    # Translation files to merge
    translation_files = [
        "translations_psalms.json",
        "translations_wisdom.json",
        "translations_prophets.json",
        "translations_historical.json",
        "translations_remaining.json",
        "translations_final.json"
    ]

    master_translations = {}
    stats = {
        "files_processed": 0,
        "files_missing": 0,
        "total_translations": 0,
        "duplicates_found": 0
    }

    print("Merging translation files...")
    print("=" * 60)

    for filename in translation_files:
        filepath = Path(filename)

        if not filepath.exists():
            print(f"⚠ Missing: {filename}")
            stats["files_missing"] += 1
            continue

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            translations = data.get('translations', {})
            books = data.get('books', data.get('book', 'unknown'))

            print(f"✓ {filename}: {len(translations)} translations")
            if isinstance(books, list):
                print(f"  Books: {', '.join(books)}")
            else:
                print(f"  Book: {books}")

            # Merge translations
            for en_title, ro_title in translations.items():
                if en_title in master_translations:
                    # Check if duplicate
                    if master_translations[en_title] != ro_title:
                        print(f"  ⚠ Duplicate with different translation: {en_title}")
                        print(f"    Existing: {master_translations[en_title]}")
                        print(f"    New: {ro_title}")
                        stats["duplicates_found"] += 1
                else:
                    master_translations[en_title] = ro_title

            stats["files_processed"] += 1

        except Exception as e:
            print(f"✗ Error processing {filename}: {e}")

    stats["total_translations"] = len(master_translations)

    print("=" * 60)
    print(f"Merge Summary:")
    print(f"  Files processed: {stats['files_processed']}")
    print(f"  Files missing: {stats['files_missing']}")
    print(f"  Total unique translations: {stats['total_translations']}")
    print(f"  Duplicates found: {stats['duplicates_found']}")
    print("=" * 60)

    # Create master dictionary file
    output = {
        "description": "Master translation dictionary for Romanian Orthodox Bible pericope titles",
        "source_files": translation_files,
        "stats": stats,
        "translations": master_translations
    }

    output_file = "pericope_translation_dictionary.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Master dictionary saved to: {output_file}")
    print(f"✓ Ready to apply with: python apply_pericope_translations.py")

    return stats


if __name__ == "__main__":
    merge_translation_files()
