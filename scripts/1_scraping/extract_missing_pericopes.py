#!/usr/bin/env python3
"""
Extract missing Romanian pericopes with conservative delays to avoid blocking.

Uses the pericope_missing.csv file to know exactly what to extract.
Implements safe delays (30-60 seconds) and single-threaded extraction.
"""

import csv
import json
import os
import time
import random
import sys
from pathlib import Path
from datetime import datetime
from scrape_romanian_chapter import scrape_romanian_chapter
from split_romanian_by_pericopes import split_chapter_by_pericopes, load_pericope_structure

# Constants
DELAY_MIN = 30  # Minimum delay between requests (seconds)
DELAY_MAX = 60  # Maximum delay between requests (seconds)
TEMP_CHAPTERS_DIR = "temp_romanian_chapters"
LOG_FILE = "extraction_log.txt"

def log_message(message, also_print=True):
    """Log a message to file and optionally print to console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"

    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')

    if also_print:
        print(log_entry)

def load_book_ids():
    """Load the Romanian book IDs mapping"""
    with open('romanian_book_ids.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_missing_pericopes(csv_file='pericope_missing.csv'):
    """
    Load missing pericopes from CSV and organize by book and chapter.

    Returns:
        dict: {
            'Matthew': {
                '1': [(pericope_num, title, start_verse, end_verse), ...],
                '2': [...]
            },
            ...
        }
    """
    missing_by_book = {}

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            book_english = row['Book_English']
            chapter = row['Chapter']
            pericope_num = row['Pericope']

            # Initialize book if needed
            if book_english not in missing_by_book:
                missing_by_book[book_english] = {}

            # Initialize chapter if needed
            if chapter not in missing_by_book[book_english]:
                missing_by_book[book_english][chapter] = []

            # Add pericope info
            missing_by_book[book_english][chapter].append({
                'pericope_num': pericope_num,
                'chapter': chapter,
                'testament': row['Testament'],
                'book_romanian': row['Book_Romanian']
            })

    return missing_by_book

def check_site_accessibility():
    """Test if the Romanian Bible site is accessible"""
    import requests

    test_url = "https://www.bibliaortodoxa.ro/carte.php?id=53&cap=1"

    try:
        log_message("Testing site accessibility...")
        response = requests.get(test_url, timeout=10)

        if response.status_code == 200:
            log_message(f"✓ Site accessible (HTTP {response.status_code})")
            return True
        else:
            log_message(f"✗ Site returned HTTP {response.status_code}")
            return False

    except Exception as e:
        log_message(f"✗ Connection error: {e}")
        return False

def extract_chapter_if_needed(book_english, book_id, chapter_num, book_name_romanian):
    """
    Extract a chapter from the Romanian site if not already cached.

    Returns:
        List of verses or None if failed
    """
    # Check if already cached
    chapter_file = Path(TEMP_CHAPTERS_DIR) / f"{book_english}_ch{int(chapter_num):02d}.json"

    if chapter_file.exists():
        log_message(f"  Using cached chapter: {chapter_file.name}")
        with open(chapter_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    # Need to scrape
    log_message(f"  Scraping {book_name_romanian} chapter {chapter_num} (Book ID: {book_id})...")

    # Random delay before request
    delay = random.uniform(DELAY_MIN, DELAY_MAX)
    log_message(f"  Waiting {delay:.1f} seconds before request...")
    time.sleep(delay)

    # Scrape the chapter
    verses = scrape_romanian_chapter(book_id, int(chapter_num), delay=0)

    if verses:
        log_message(f"  ✓ Scraped {len(verses)} verses")

        # Cache to temp directory
        os.makedirs(TEMP_CHAPTERS_DIR, exist_ok=True)
        with open(chapter_file, 'w', encoding='utf-8') as f:
            json.dump(verses, f, indent=2, ensure_ascii=False)

        return verses
    else:
        log_message(f"  ✗ Failed to scrape chapter")
        return None

def extract_missing_pericopes(
    priority_books=None,
    testament_filter=None,
    max_chapters=None,
    dry_run=False
):
    """
    Extract missing Romanian pericopes with conservative delays.

    Args:
        priority_books: List of book names to extract first (None = all books)
        testament_filter: 'OT' or 'NT' to filter by testament (None = both)
        max_chapters: Maximum chapters to extract (None = all)
        dry_run: If True, only show what would be extracted without doing it
    """
    log_message("="*70)
    log_message("ROMANIAN PERICOPE EXTRACTION - CONSERVATIVE MODE")
    log_message(f"Delay range: {DELAY_MIN}-{DELAY_MAX} seconds")
    log_message(f"Mode: {'DRY RUN' if dry_run else 'LIVE EXTRACTION'}")
    log_message("="*70)

    # Load data
    book_ids_data = load_book_ids()
    missing_data = load_missing_pericopes()
    pericope_structure = load_pericope_structure('pericope_structure.json')

    # Calculate statistics
    total_books = len(missing_data)
    total_chapters = sum(len(chapters) for chapters in missing_data.values())
    total_pericopes = sum(
        len(pericopes)
        for book_chapters in missing_data.values()
        for pericopes in book_chapters.values()
    )

    log_message(f"\nMissing content summary:")
    log_message(f"  Books with missing pericopes: {total_books}")
    log_message(f"  Chapters to extract: {total_chapters}")
    log_message(f"  Total missing pericopes: {total_pericopes}")

    # Estimate time
    avg_delay = (DELAY_MIN + DELAY_MAX) / 2
    estimated_time_minutes = (total_chapters * avg_delay) / 60
    log_message(f"  Estimated time: {estimated_time_minutes:.1f} minutes ({estimated_time_minutes/60:.1f} hours)")

    if dry_run:
        log_message("\n*** DRY RUN - No extraction will be performed ***")
        return

    # Check site accessibility
    if not check_site_accessibility():
        log_message("\n✗ Site is not accessible. Aborting extraction.")
        log_message("Please check:")
        log_message("  1. Your internet connection")
        log_message("  2. VPN status (if using one)")
        log_message("  3. Wait 24-48 hours if you were blocked")
        return

    # Determine books to process
    books_to_process = list(missing_data.keys())

    if priority_books:
        # Sort: priority books first, then others
        books_to_process.sort(key=lambda b: (b not in priority_books, b))

    # Filter by testament if specified
    if testament_filter:
        filtered_books = []
        for book in books_to_process:
            # Get testament from first chapter's first pericope
            first_chapter = list(missing_data[book].keys())[0]
            first_pericope = missing_data[book][first_chapter][0]
            if first_pericope['testament'] == testament_filter:
                filtered_books.append(book)
        books_to_process = filtered_books

    log_message(f"\nProcessing {len(books_to_process)} books...")

    # Statistics tracking
    chapters_extracted = 0
    chapters_failed = 0
    pericopes_created = 0
    start_time = datetime.now()

    # Process each book
    for book_idx, book_english in enumerate(books_to_process, 1):
        log_message(f"\n{'='*70}")
        log_message(f"[{book_idx}/{len(books_to_process)}] {book_english}")
        log_message(f"{'='*70}")

        # Get book info
        # Handle underscore vs space in book names
        book_key = book_english.replace('_', ' ')
        if book_key not in book_ids_data:
            log_message(f"  ✗ Book '{book_key}' not found in book_ids.json")
            continue

        book_info = book_ids_data[book_key]
        book_id = book_info['id']
        book_name_romanian = book_info['romanian_name']

        # Get testament
        first_chapter_key = list(missing_data[book_english].keys())[0]
        testament = missing_data[book_english][first_chapter_key][0]['testament']
        testament_folder = 'New Testament' if testament == 'NT' else 'Old Testament'

        # Process each chapter
        chapters = sorted(missing_data[book_english].keys(), key=lambda x: int(x))

        for chapter_num in chapters:
            # Check max chapters limit
            if max_chapters and chapters_extracted >= max_chapters:
                log_message(f"\n✓ Reached max chapters limit ({max_chapters})")
                break

            log_message(f"\nChapter {chapter_num}:")
            pericopes = missing_data[book_english][chapter_num]
            log_message(f"  Missing pericopes: {len(pericopes)}")

            # Extract chapter
            verses = extract_chapter_if_needed(
                book_english,
                book_id,
                chapter_num,
                book_name_romanian
            )

            if not verses:
                log_message(f"  ✗ Failed to extract chapter {chapter_num}")
                chapters_failed += 1
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
                log_message(f"  ✓ Created {files_created} pericope files")

            except Exception as e:
                log_message(f"  ✗ Error splitting chapter: {e}")

        # Stop if max chapters reached
        if max_chapters and chapters_extracted >= max_chapters:
            break

    # Final summary
    end_time = datetime.now()
    duration = end_time - start_time

    log_message("\n" + "="*70)
    log_message("EXTRACTION COMPLETE")
    log_message("="*70)
    log_message(f"Chapters extracted: {chapters_extracted}")
    log_message(f"Chapters failed: {chapters_failed}")
    log_message(f"Pericopes created: {pericopes_created}")
    log_message(f"Duration: {duration}")
    log_message(f"Log saved to: {LOG_FILE}")
    log_message("="*70)

if __name__ == '__main__':
    import sys, io

    # Fix Windows encoding for Romanian characters
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser(
        description='Extract missing Romanian Bible pericopes with conservative delays'
    )
    parser.add_argument(
        '--testament',
        choices=['OT', 'NT'],
        help='Extract only Old Testament (OT) or New Testament (NT)'
    )
    parser.add_argument(
        '--books',
        nargs='+',
        help='Priority books to extract first (e.g., Matthew Mark Luke)'
    )
    parser.add_argument(
        '--max-chapters',
        type=int,
        help='Maximum number of chapters to extract (for testing)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be extracted without actually doing it'
    )
    parser.add_argument(
        '--delay-min',
        type=int,
        default=30,
        help='Minimum delay in seconds (default: 30)'
    )
    parser.add_argument(
        '--delay-max',
        type=int,
        default=60,
        help='Maximum delay in seconds (default: 60)'
    )

    args = parser.parse_args()

    # Update delay constants
    DELAY_MIN = args.delay_min
    DELAY_MAX = args.delay_max

    # Run extraction
    extract_missing_pericopes(
        priority_books=args.books,
        testament_filter=args.testament,
        max_chapters=args.max_chapters,
        dry_run=args.dry_run
    )
