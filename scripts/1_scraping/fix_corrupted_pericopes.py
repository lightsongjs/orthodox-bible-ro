#!/usr/bin/env python3
"""
Fix corrupted pericope files for short single-chapter books.

These books (2 John, 3 John, Philemon, Jude) only have 1 chapter,
but the extraction created fake "chapter 2, 3, 4..." files.

This script:
1. Identifies and removes corrupted files
2. Updates pericope_structure.json to only include chapter 1
3. Allows re-extraction of these books
"""

import os
import json
import shutil
from pathlib import Path

# Books with corruption and their correct chapter count
SINGLE_CHAPTER_BOOKS = {
    '2_John': {
        'english_dir': 'New Testament/2_John',
        'romanian_dir': 'Romanian Bible/New Testament/II Ioan',
        'correct_chapters': 1,
        'correct_pericopes_ch1': 3  # Only 3 pericopes in chapter 1
    },
    '3_John': {
        'english_dir': 'New Testament/3_John',
        'romanian_dir': 'Romanian Bible/New Testament/III Ioan',
        'correct_chapters': 1,
        'correct_pericopes_ch1': 4  # Only 4 pericopes in chapter 1
    },
    'Philemon': {
        'english_dir': 'New Testament/Philemon',
        'romanian_dir': 'Romanian Bible/New Testament/Filimon',
        'correct_chapters': 1,
        'correct_pericopes_ch1': 4  # Only 4 pericopes in chapter 1
    },
    'Jude': {
        'english_dir': 'New Testament/Jude',
        'romanian_dir': 'Romanian Bible/New Testament/Iuda',
        'correct_chapters': 1,
        'correct_pericopes_ch1': 5  # Only 5 pericopes in chapter 1
    }
}

def backup_structure():
    """Backup pericope_structure.json"""
    shutil.copy('pericope_structure.json', 'pericope_structure.json.backup')
    print("✓ Backed up pericope_structure.json")

def clean_english_files(book_name, book_info):
    """Remove corrupted English pericope files (chapter > 1)"""
    english_dir = Path(book_info['english_dir'])

    if not english_dir.exists():
        print(f"  ⚠ Directory not found: {english_dir}")
        return 0

    removed = 0
    for file in english_dir.glob('*.md'):
        filename = file.name

        # Extract chapter number from filename like "(2 John 02.01) ..."
        if '(' in filename and ')' in filename:
            pericope_id = filename[filename.index('(')+1:filename.index(')')]
            parts = pericope_id.split()

            # For "2 John 02.01", parts = ["2", "John", "02.01"]
            # For "3 John 02.01", parts = ["3", "John", "02.01"]
            # We want the last part
            if len(parts) >= 1:
                chapter_pericope = parts[-1]  # e.g., "02.01"
                try:
                    chapter_num = int(chapter_pericope.split('.')[0])
                except ValueError:
                    continue  # Skip files that don't match pattern

                # If chapter > 1, it's corrupted (these are single-chapter books)
                if chapter_num > 1:
                    print(f"    Removing: {filename}")
                    file.unlink()
                    removed += 1

    return removed

def clean_romanian_files(book_name, book_info):
    """Remove corrupted Romanian pericope files (chapter > 1)"""
    romanian_dir = Path(book_info['romanian_dir'])

    if not romanian_dir.exists():
        print(f"  ⚠ Romanian directory not found: {romanian_dir}")
        return 0

    removed = 0
    for file in romanian_dir.glob('*.md'):
        filename = file.name

        # Extract chapter number
        if '(' in filename and ')' in filename:
            pericope_id = filename[filename.index('(')+1:filename.index(')')]
            parts = pericope_id.split()

            if len(parts) >= 1:
                chapter_pericope = parts[-1]  # e.g., "02.01"
                try:
                    chapter_num = int(chapter_pericope.split('.')[0])
                except ValueError:
                    continue  # Skip files that don't match pattern

                if chapter_num > 1:
                    print(f"    Removing: {filename}")
                    file.unlink()
                    removed += 1

    return removed

def fix_pericope_structure(book_name):
    """Fix pericope_structure.json to only include chapter 1"""
    with open('pericope_structure.json', 'r', encoding='utf-8') as f:
        structure = json.load(f)

    if book_name not in structure:
        print(f"  ⚠ {book_name} not found in pericope_structure.json")
        return False

    # Keep only chapter 1
    original_chapters = len(structure[book_name])
    structure[book_name] = {
        '1': structure[book_name]['1']
    }

    # Save updated structure
    with open('pericope_structure.json', 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)

    print(f"    Updated structure: {original_chapters} chapters → 1 chapter")
    return True

def main():
    import sys, io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("="*70)
    print("FIXING CORRUPTED PERICOPE FILES")
    print("="*70)
    print()

    # Backup first
    backup_structure()
    print()

    total_english_removed = 0
    total_romanian_removed = 0

    for book_name, book_info in SINGLE_CHAPTER_BOOKS.items():
        print(f"Processing {book_name}:")

        # Clean English files
        english_removed = clean_english_files(book_name, book_info)
        total_english_removed += english_removed
        print(f"  ✓ Removed {english_removed} corrupted English files")

        # Clean Romanian files (if any)
        romanian_removed = clean_romanian_files(book_name, book_info)
        total_romanian_removed += romanian_removed
        print(f"  ✓ Removed {romanian_removed} corrupted Romanian files")

        # Fix pericope structure
        fix_pericope_structure(book_name)
        print()

    print("="*70)
    print("CLEANUP COMPLETE")
    print("="*70)
    print(f"English files removed: {total_english_removed}")
    print(f"Romanian files removed: {total_romanian_removed}")
    print()
    print("Next steps:")
    print("1. Regenerate CSV: python create_pericope_mapping_csv.py")
    print("2. Re-extract these books: python extract_missing_pericopes.py --books 2_John 3_John Philemon Jude")
    print()

if __name__ == '__main__':
    main()
