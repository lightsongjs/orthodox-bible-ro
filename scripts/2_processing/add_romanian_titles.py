#!/usr/bin/env python3
"""
Add Romanian titles to pericope JSON files.

Changes:
- Rename 'title' to 'title_en'
- Add 'title_ro' with Romanian translation
"""

import json
from pathlib import Path
from typing import Dict


# Translation dictionary for common pericope titles
TITLE_TRANSLATIONS = {
    # Common words
    "The": "",
    "A": "Un",
    "An": "Un",
    "And": "Și",
    "Of": "A",
    "To": "Către",
    "In": "În",
    "On": "Pe",
    "At": "La",
    "By": "De",
    "For": "Pentru",
    "From": "Din",
    "With": "Cu",

    # Genesis
    "The Genealogy of Jesus the Messiah": "Genealogia lui Isus Hristos",
    "The Birth of Jesus the Messiah": "Nașterea lui Isus Hristos",
    "The Visit of the Wise Men": "Vizita Magilor",
    "The Escape to Egypt": "Fuga în Egipt",
    "The Massacre of the Infants": "Masacrul Pruncilor",
    "The Return from Egypt": "Întoarcerea din Egipt",
    "Cain Murders Abel": "Cain îl ucide pe Abel",
    "Beginnings of Civilization": "Începuturile Civilizației",
    "The First Sin and Its Punishment": "Primul Păcat și Pedeapsa lui",
    "Another Account of the Creation": "O Altă Relatare a Creației",

    # Common Bible themes
    "The Call of": "Chemarea lui",
    "The Death of": "Moartea lui",
    "The Birth of": "Nașterea lui",
    "The Genealogy of": "Genealogia lui",
    "Jesus Heals": "Isus vindecă",
    "Jesus Calls": "Isus cheamă",
    "Jesus Teaches": "Isus învață",
    "The Parable of": "Pilda",
    "The Resurrection": "Învierea",
    "The Crucifixion": "Răstignirea",
    "The Ascension": "Înălțarea",
    "The Transfiguration": "Schimbarea la Față",
    "Salutation": "Salutare",
    "Proclamation": "Proclamare",
    "Ministry": "Slujire",
    "Mission": "Misiune",
    "Teaching": "Învățătură",
    "Prayer": "Rugăciune",
    "Faith": "Credință",
    "Love": "Dragoste",
    "Hope": "Speranță",
}


def simple_translate(title_en: str) -> str:
    """
    Simple translation of English title to Romanian.

    For now, returns the English title with a marker.
    A more sophisticated translation would use a translation API.

    Args:
        title_en: English title

    Returns:
        Romanian title (or marked English if no translation)
    """
    # Check if we have a direct translation
    if title_en in TITLE_TRANSLATIONS:
        return TITLE_TRANSLATIONS[title_en]

    # For now, return the English title
    # You can replace this with API translation or manual translation later
    return title_en


def update_pericope_file(json_file: Path):
    """
    Update a single pericope JSON file to add Romanian titles.

    Args:
        json_file: Path to pericope JSON file
    """
    # Read the file
    with open(json_file, 'r', encoding='utf-8') as f:
        book_data = json.load(f)

    # Update each pericope
    for pericope in book_data['pericopes']:
        # Rename 'title' to 'title_en' if it exists
        if 'title' in pericope:
            pericope['title_en'] = pericope.pop('title')

        # Add 'title_ro' if it doesn't exist
        if 'title_ro' not in pericope:
            title_en = pericope.get('title_en', '')
            pericope['title_ro'] = simple_translate(title_en)

    # Write back with proper field order
    updated_pericopes = []
    for pericope in book_data['pericopes']:
        ordered_pericope = {
            'pericope_id': pericope['pericope_id'],
            'chapter': pericope['chapter'],
            'pericope_num': pericope['pericope_num'],
            'title_en': pericope.get('title_en', ''),
            'title_ro': pericope.get('title_ro', ''),
            'start_verse': pericope['start_verse'],
            'end_verse': pericope['end_verse'],
            'verse_count': pericope['verse_count'],
            'verses': pericope['verses']
        }
        updated_pericopes.append(ordered_pericope)

    book_data['pericopes'] = updated_pericopes

    # Write back to file
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(book_data, f, ensure_ascii=False, indent=2)


def main():
    """Main entry point."""
    pericopes_dir = Path('bible_books_pericopes')

    print(f"\n{'='*60}")
    print("ADDING ROMANIAN TITLES TO PERICOPES")
    print(f"{'='*60}\n")

    json_files = sorted(pericopes_dir.glob('*.json'))

    print(f"Processing {len(json_files)} books...\n")

    total_pericopes = 0

    for json_file in json_files:
        book_data = json.load(open(json_file, 'r', encoding='utf-8'))
        book_name = book_data['name_en']
        pericope_count = len(book_data['pericopes'])

        update_pericope_file(json_file)

        print(f"  [{book_data['book_number']:02d}] {book_name} - {pericope_count} pericopes updated")
        total_pericopes += pericope_count

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Books updated: {len(json_files)}")
    print(f"Total pericopes: {total_pericopes}")
    print(f"\nNote: Romanian titles are currently set to English titles.")
    print(f"You can add more translations to TITLE_TRANSLATIONS dictionary")
    print(f"or use a translation API for automatic translation.")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
