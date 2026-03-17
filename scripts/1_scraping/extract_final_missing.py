"""
Extract the final 48 missing pericopes to complete the Romanian Bible.
Uses missing_pericopes_detailed.csv as input.
"""
import csv
import json
import os
import time
import random
from pathlib import Path
from scrape_romanian_chapter import scrape_romanian_chapter
from split_romanian_by_pericopes import split_chapter_by_pericopes, load_pericope_structure

DELAY_MIN = 10  # seconds between requests
DELAY_MAX = 20
TEMP_CHAPTERS_DIR = "temp_romanian_chapters"

def load_missing_pericopes_csv():
    """Load the detailed CSV of missing pericopes"""
    missing = []

    with open('missing_pericopes_detailed.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            missing.append(row)

    # Group by book and chapter
    by_book_chapter = {}

    for item in missing:
        book = item['book_english']
        chapter = item['chapter']

        if book not in by_book_chapter:
            by_book_chapter[book] = {}

        if chapter not in by_book_chapter[book]:
            by_book_chapter[book][chapter] = []

        by_book_chapter[book][chapter].append(item)

    return by_book_chapter

def extract_chapter_if_needed(book_english, book_id, chapter_num, book_name_romanian):
    """Extract chapter if not cached"""
    # Check cache
    chapter_file = Path(TEMP_CHAPTERS_DIR) / f"{book_english}_ch{int(chapter_num):02d}.json"

    if chapter_file.exists():
        print(f"  Using cached chapter: {chapter_file.name}")
        with open(chapter_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    # Scrape
    print(f"  Scraping {book_name_romanian} chapter {chapter_num} (Book ID: {book_id})...")

    delay = random.uniform(DELAY_MIN, DELAY_MAX)
    print(f"  Waiting {delay:.1f} seconds...")
    time.sleep(delay)

    verses = scrape_romanian_chapter(book_id, int(chapter_num), delay=0)

    if verses:
        print(f"  ✓ Scraped {len(verses)} verses")

        # Cache
        os.makedirs(TEMP_CHAPTERS_DIR, exist_ok=True)
        with open(chapter_file, 'w', encoding='utf-8') as f:
            json.dump(verses, f, indent=2, ensure_ascii=False)

        return verses
    else:
        print(f"  ✗ Failed to scrape chapter {chapter_num}")
        return None

def extract_final_missing():
    """Extract all remaining missing pericopes"""

    print("="*80)
    print("EXTRACTING FINAL 48 MISSING PERICOPES")
    print("="*80)
    print()

    # Load data
    missing_by_book = load_missing_pericopes_csv()
    pericope_structure = load_pericope_structure('pericope_structure.json')

    total_missing = sum(
        len(pericopes)
        for book_chapters in missing_by_book.values()
        for pericopes in book_chapters.values()
    )

    print(f"Books to process: {len(missing_by_book)}")
    print(f"Total pericopes to extract: {total_missing}")
    print()

    # Statistics
    chapters_extracted = 0
    pericopes_created = 0
    failed_chapters = []

    # Process each book
    for book_idx, (book_english, chapters) in enumerate(missing_by_book.items(), 1):
        print(f"\n{'='*80}")
        print(f"[{book_idx}/{len(missing_by_book)}] {book_english}")
        print(f"{'='*80}")

        # Get first item to determine book info
        first_chapter = list(chapters.keys())[0]
        first_item = chapters[first_chapter][0]

        book_id = int(first_item['book_id'])
        book_name_romanian = first_item['book_romanian']
        testament = first_item['testament']
        testament_folder = 'New Testament' if testament == 'NT' else 'Old Testament'

        # Process each chapter
        for chapter_num in sorted(chapters.keys(), key=lambda x: int(x)):
            print(f"\nChapter {chapter_num}:")
            pericopes_to_extract = chapters[chapter_num]
            print(f"  Missing pericopes: {len(pericopes_to_extract)}")

            # Extract chapter
            verses = extract_chapter_if_needed(
                book_english,
                book_id,
                chapter_num,
                book_name_romanian
            )

            if not verses:
                print(f"  ✗ Failed - chapter may not exist on site")
                failed_chapters.append(f"{book_english} {chapter_num}")
                continue

            chapters_extracted += 1

            # Split into pericopes
            output_dir = Path('Romanian Bible') / testament_folder / book_name_romanian
            output_dir.mkdir(parents=True, exist_ok=True)

            try:
                files_created = split_chapter_by_pericopes(
                    verses,
                    book_english,
                    int(chapter_num),
                    pericope_structure[book_english],
                    str(output_dir)
                )

                pericopes_created += files_created
                print(f"  ✓ Created {files_created} pericope files")

            except Exception as e:
                print(f"  ✗ Error splitting chapter: {e}")

    # Final summary
    print()
    print("="*80)
    print("EXTRACTION COMPLETE")
    print("="*80)
    print(f"Chapters successfully extracted: {chapters_extracted}")
    print(f"Pericopes created: {pericopes_created}")
    print(f"Failed chapters: {len(failed_chapters)}")

    if failed_chapters:
        print("\nFailed chapters (likely don't exist):")
        for fc in failed_chapters:
            print(f"  - {fc}")

    print("="*80)

if __name__ == '__main__':
    import sys
    import io

    # Fix Windows encoding
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    extract_final_missing()
