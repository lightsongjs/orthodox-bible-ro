#!/usr/bin/env python3
"""
Extract all unique English pericope titles from pericope JSON files.
Creates a clean JSON file with only the titles that need translation.
"""

import json
import os
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def extract_all_titles():
    """Extract all unique pericope titles from all books."""
    pericopes_dir = Path("bible_books_pericopes")

    # Collect all unique titles
    all_titles = set()
    untranslated_titles = set()

    # Statistics
    total_pericopes = 0
    books_processed = 0

    print("Scanning pericope files...")

    for json_file in sorted(pericopes_dir.glob("*_pericopes.json")):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                book_data = json.load(f)

            book_name = book_data.get('name_ro', json_file.stem)
            pericopes = book_data.get('pericopes', [])

            books_processed += 1
            book_untranslated = 0

            for pericope in pericopes:
                total_pericopes += 1
                title_en = pericope.get('title_en', '')
                title_ro = pericope.get('title_ro', '')

                if title_en:
                    all_titles.add(title_en)

                    # Check if needs translation
                    # (title_ro is empty, same as English, or clearly untranslated)
                    if not title_ro or title_ro == title_en or title_ro == '':
                        untranslated_titles.add(title_en)
                        book_untranslated += 1

            if book_untranslated > 0:
                print(f"  {book_name}: {book_untranslated} untranslated")

        except Exception as e:
            print(f"Error processing {json_file}: {e}")

    # Create output structure
    output = {
        "stats": {
            "total_books": books_processed,
            "total_pericopes": total_pericopes,
            "unique_titles": len(all_titles),
            "untranslated_count": len(untranslated_titles)
        },
        "untranslated_titles": sorted(list(untranslated_titles)),
        "all_unique_titles": sorted(list(all_titles))
    }

    # Save to JSON file
    output_file = "pericope_titles_to_translate.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Extraction complete!")
    print(f"  Total books: {books_processed}")
    print(f"  Total pericopes: {total_pericopes}")
    print(f"  Unique titles: {len(all_titles)}")
    print(f"  Need translation: {len(untranslated_titles)}")
    print(f"\n✓ Saved to: {output_file}")

    # Also create a simple text file for easy viewing
    text_file = "untranslated_titles.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(f"Untranslated Pericope Titles ({len(untranslated_titles)} total)\n")
        f.write("=" * 60 + "\n\n")
        for title in sorted(untranslated_titles):
            f.write(f"{title}\n")

    print(f"✓ Text list saved to: {text_file}")

    return output

if __name__ == "__main__":
    extract_all_titles()
