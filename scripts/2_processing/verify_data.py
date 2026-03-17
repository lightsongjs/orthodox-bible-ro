#!/usr/bin/env python3
"""
Verification script to ensure all Bible chapters have been downloaded correctly.
"""

import json
from pathlib import Path

def verify_completeness():
    """Verify that all chapters from all books have been downloaded."""

    # Load metadata
    with open('bible_books_metadata.json', 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    chapters_dir = Path('bible_books')

    all_good = True
    total_expected_chapters = 0
    total_found_chapters = 0
    missing_chapters = []

    print("Verifying Bible chapter completeness...")
    print("="*60)

    for testament in ['old_testament', 'new_testament']:
        books = metadata[testament]

        for book in books:
            book_id = book['id']
            name_en = book['name_en']
            name_ro = book['name_ro']
            expected_chapters = book['chapters']

            total_expected_chapters += expected_chapters

            # Find the book file using Romanian name
            safe_name_ro = name_ro.replace(' ', '_').replace('/', '_')
            # Try to find the file - it should have the format ##_{romanian_name}.json
            # Use more specific pattern to avoid partial matches
            matching_files = [f for f in chapters_dir.glob(f"??_{safe_name_ro}.json") if f.stem.endswith(f"_{safe_name_ro}")]

            if not matching_files:
                print(f"✗ MISSING FILE for {name_en}")
                all_good = False
                missing_chapters.append({
                    'book': name_en,
                    'reason': 'File not found',
                    'expected': expected_chapters
                })
                continue

            book_file = matching_files[0]

            # Load and check chapter count
            with open(book_file, 'r', encoding='utf-8') as f:
                book_data = json.load(f)

            found_chapters = len(book_data['chapters'])
            total_found_chapters += found_chapters

            if found_chapters != expected_chapters:
                print(f"✗ {name_en} ({name_ro}): Expected {expected_chapters} chapters, found {found_chapters}")
                all_good = False
                missing_chapters.append({
                    'book': name_en,
                    'expected': expected_chapters,
                    'found': found_chapters,
                    'missing': expected_chapters - found_chapters
                })
            else:
                # Verify each chapter has verses
                for chapter in book_data['chapters']:
                    if not chapter.get('verses'):
                        print(f"✗ {name_en} - Chapter {chapter['chapter']} has no verses!")
                        all_good = False
                        missing_chapters.append({
                            'book': name_en,
                            'chapter': chapter['chapter'],
                            'reason': 'No verses found'
                        })

                print(f"✓ {name_en} ({name_ro}): {found_chapters} chapters verified")

    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    print(f"Total expected chapters: {total_expected_chapters}")
    print(f"Total found chapters: {total_found_chapters}")

    if all_good:
        print("\n✓✓✓ ALL CHAPTERS VERIFIED SUCCESSFULLY! ✓✓✓")
        print("The complete Romanian Orthodox Bible has been downloaded.")
    else:
        print(f"\n✗ Issues found: {len(missing_chapters)}")
        print("\nMissing or incomplete:")
        for issue in missing_chapters:
            print(f"  - {issue}")

    return all_good

if __name__ == '__main__':
    success = verify_completeness()
    exit(0 if success else 1)
