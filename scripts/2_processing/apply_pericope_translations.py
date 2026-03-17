#!/usr/bin/env python3
"""
Apply Romanian translations to pericope titles.
Reads from a translation dictionary and updates the pericope JSON files.

This script ONLY modifies the 'title_ro' field - it never touches the actual Bible text.
"""

import json
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def load_translation_dictionary(dict_file):
    """Load translation dictionary from JSON file."""
    try:
        with open(dict_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('translations', {})
    except FileNotFoundError:
        print(f"Error: Translation dictionary file not found: {dict_file}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in translation dictionary: {e}")
        return {}


def apply_translations_to_pericopes(translation_dict):
    """
    Apply translations to all pericope files.
    Only modifies title_ro field, never touches verse text.
    """
    pericopes_dir = Path("bible_books_pericopes")

    # Statistics
    books_updated = 0
    pericopes_updated = 0
    pericopes_skipped = 0
    pericopes_total = 0

    print("Applying translations to pericope files...")
    print(f"Translation dictionary has {len(translation_dict)} entries\n")

    for json_file in sorted(pericopes_dir.glob("*_pericopes.json")):
        try:
            # Read the book file
            with open(json_file, 'r', encoding='utf-8') as f:
                book_data = json.load(f)

            book_name = book_data.get('name_ro', json_file.stem)
            pericopes = book_data.get('pericopes', [])

            book_updated = 0
            modified = False

            # Update pericopes
            for pericope in pericopes:
                pericopes_total += 1
                title_en = pericope.get('title_en', '')
                title_ro = pericope.get('title_ro', '')

                # Normalize apostrophes for lookup (curly U+2019 to straight U+0027)
                normalized_title = title_en.replace('\u2019', "'")

                # Check if translation exists
                if normalized_title in translation_dict:
                    new_title_ro = translation_dict[normalized_title]

                    # Only update if different (or empty)
                    if not title_ro or title_ro == title_en or title_ro != new_title_ro:
                        pericope['title_ro'] = new_title_ro
                        book_updated += 1
                        pericopes_updated += 1
                        modified = True
                else:
                    # No translation available
                    if not title_ro or title_ro == title_en:
                        pericopes_skipped += 1

            # Save if modified
            if modified:
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(book_data, f, indent=2, ensure_ascii=False)
                books_updated += 1
                print(f"  ✓ {book_name}: {book_updated} pericopes updated")

        except Exception as e:
            print(f"  ✗ Error processing {json_file}: {e}")

    print(f"\n{'='*60}")
    print(f"Translation Summary:")
    print(f"  Total pericopes: {pericopes_total}")
    print(f"  Pericopes updated: {pericopes_updated}")
    print(f"  Pericopes still missing translation: {pericopes_skipped}")
    print(f"  Books updated: {books_updated}")
    print(f"{'='*60}")


def main():
    """Main execution."""
    # Default translation dictionary file
    dict_file = "pericope_translation_dictionary.json"

    # Allow custom file via command line
    if len(sys.argv) > 1:
        dict_file = sys.argv[1]

    print(f"Loading translation dictionary from: {dict_file}")
    translation_dict = load_translation_dictionary(dict_file)

    if not translation_dict:
        print("\nNo translations to apply. Please create a translation dictionary file.")
        print("Expected format:")
        print("""
{
  "translations": {
    "English Title 1": "Titlu Românesc 1",
    "English Title 2": "Titlu Românesc 2"
  }
}
""")
        return

    apply_translations_to_pericopes(translation_dict)


if __name__ == "__main__":
    main()
