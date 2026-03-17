"""
Identify exactly which pericopes are missing by comparing
pericope_structure.json with what exists in Romanian directories.
"""
import json
from pathlib import Path

def load_pericope_structure():
    """Load the expected pericope structure"""
    with open('pericope_structure.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_book_mapping():
    """Load the English to Romanian book name mapping"""
    with open('romanian_book_ids.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_existing_pericopes(testament_dir, book_name):
    """Get list of existing pericope files for a book"""
    book_path = Path(testament_dir) / book_name
    if not book_path.exists():
        return set()

    # Get all .md files and extract their identifiers
    existing = set()
    for md_file in book_path.glob('*.md'):
        # File format: BookName_chXX_pYY.md or similar
        existing.add(md_file.name)

    return existing

def get_testament(book_english):
    """Determine testament"""
    ot_books = {
        'Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy',
        'Joshua', 'Judges', 'Ruth', '1 Samuel', '2 Samuel',
        '1 Kings', '2 Kings', '1 Chronicles', '2 Chronicles',
        'Ezra', 'Nehemiah', 'Tobit', 'Judith', 'Esther',
        '1 Maccabees', '2 Maccabees', 'Job', 'Psalms', 'Proverbs',
        'Ecclesiastes', 'Song of Solomon', 'Wisdom', 'Sirach',
        'Isaiah', 'Jeremiah', 'Lamentations', 'Baruch', 'Ezekiel',
        'Daniel', 'Hosea', 'Joel', 'Amos', 'Obadiah', 'Jonah',
        'Micah', 'Nahum', 'Habakkuk', 'Zephaniah', 'Haggai',
        'Zechariah', 'Malachi'
    }
    return 'OT' if book_english in ot_books else 'NT'

def identify_missing_pericopes():
    """Identify all missing pericopes"""

    pericope_structure = load_pericope_structure()
    book_mapping = load_book_mapping()

    # Books that are partially complete (from the report)
    partial_books = [
        'Obadiah', 'Daniel', 'Baruch', 'Joel', 'Sirach',
        'Deuteronomy', 'Esther', 'Exodus', 'Hosea', 'Malachi', 'Zechariah'
    ]

    missing_details = []
    total_missing = 0

    print("="*80)
    print("IDENTIFYING MISSING PERICOPES")
    print("="*80)
    print()

    for book_english in partial_books:
        if book_english not in book_mapping:
            print(f"⚠️  {book_english} not in book_mapping - skipping")
            continue

        if book_english not in pericope_structure:
            print(f"⚠️  {book_english} not in pericope_structure - skipping")
            continue

        book_romanian = book_mapping[book_english]['romanian_name']
        testament = get_testament(book_english)
        testament_dir = f'Romanian Bible/{"New Testament" if testament == "NT" else "Old Testament"}'

        # Get existing pericopes
        existing_files = get_existing_pericopes(testament_dir, book_romanian)

        # Check each expected pericope
        book_missing = []

        for chapter_num, pericopes in pericope_structure[book_english].items():
            for pericope in pericopes:
                # Get the expected filename from structure
                expected_filename = pericope.get('filename', '')
                pericope_num = pericope['pericope_num']

                # Also check alternative naming patterns
                pattern2 = f"{book_romanian}_ch{int(chapter_num):02d}_p{int(pericope_num):02d}.md"
                pattern3 = f"{book_english}_ch{int(chapter_num):02d}_p{int(pericope_num):02d}.md"

                # Check if the file exists (using filename or alternative patterns)
                found = (expected_filename in existing_files or
                        pattern2 in existing_files or
                        pattern3 in existing_files)

                if not found:
                    book_missing.append({
                        'book_english': book_english,
                        'book_romanian': book_romanian,
                        'book_id': book_mapping[book_english]['id'],
                        'testament': testament,
                        'chapter': chapter_num,
                        'pericope': pericope_num,
                        'title': pericope.get('title', ''),
                        'start_verse': pericope.get('start_verse', ''),
                        'end_verse': pericope.get('end_verse', '')
                    })

        if book_missing:
            print(f"\n{book_english} ({book_romanian}):")
            print(f"  Missing: {len(book_missing)} pericopes")

            # Show first few
            for item in book_missing[:5]:
                print(f"    - Ch {item['chapter']}, Pericope {item['pericope']}: {item['title']}")

            if len(book_missing) > 5:
                print(f"    ... and {len(book_missing) - 5} more")

            missing_details.extend(book_missing)
            total_missing += len(book_missing)

    print()
    print("="*80)
    print(f"Total Missing: {total_missing} pericopes")
    print("="*80)

    # Save to CSV
    if missing_details:
        import csv

        with open('missing_pericopes_detailed.csv', 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['book_english', 'book_romanian', 'book_id', 'testament',
                         'chapter', 'pericope', 'title', 'start_verse', 'end_verse']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(missing_details)

        print(f"\nDetailed list saved to: missing_pericopes_detailed.csv")
        print(f"You can now run the extraction script on these {total_missing} pericopes.")

    return missing_details

if __name__ == '__main__':
    import sys
    import io

    # Fix Windows encoding
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    identify_missing_pericopes()
