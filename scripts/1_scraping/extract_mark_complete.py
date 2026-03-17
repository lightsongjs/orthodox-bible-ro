"""
Extract all 16 chapters of Mark from Romanian Bible and split by pericopes
"""
import os
import json
from scrape_romanian_chapter import scrape_romanian_chapter
from split_romanian_by_pericopes import split_chapter_by_pericopes, load_pericope_structure

def extract_mark_complete():
    """
    Extract all 16 chapters of Mark from Romanian Bible
    """
    print("="*80)
    print("EXTRACTING COMPLETE BOOK OF MARK (ROMANIAN)")
    print("="*80)
    print()

    # Configuration
    BOOK_NAME = "Mark"
    BOOK_ID = 53  # Mark ID on bibliaortodoxa.ro
    STRUCTURE_FILE = "mark_structure.json"
    OUTPUT_DIR = "Romanian Bible/New Testament/Mark"
    TEMP_DIR = "temp_romanian_chapters"

    # Create temp directory for chapter files
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load pericope structure
    print("Loading pericope structure...")
    structure_data = load_pericope_structure(STRUCTURE_FILE)
    book_structure = structure_data[BOOK_NAME]
    print(f"  Structure loaded: {len(book_structure)} chapters")
    print()

    total_pericopes = 0
    total_verses = 0

    # Process each chapter
    for chapter_num in range(1, 17):  # Mark has 16 chapters
        print(f"Chapter {chapter_num}:")
        print("-" * 60)

        # Step 1: Scrape Romanian chapter
        print(f"  Scraping from bibliaortodoxa.ro...")
        romanian_verses = scrape_romanian_chapter(BOOK_ID, chapter_num, delay=0.5)

        if not romanian_verses:
            print(f"  ERROR: Could not scrape chapter {chapter_num}")
            continue

        verse_count = len(romanian_verses)
        total_verses += verse_count
        print(f"  OK - Scraped {verse_count} verses")

        # Save chapter to temp file (for debugging)
        chapter_file = os.path.join(TEMP_DIR, f"Mark_ch{chapter_num:02d}.json")
        with open(chapter_file, 'w', encoding='utf-8') as f:
            json.dump(romanian_verses, f, indent=2, ensure_ascii=False)

        # Step 2: Split by pericopes
        print(f"  Splitting into pericopes...")
        chapter_key = str(chapter_num)

        if chapter_key not in book_structure:
            print(f"  WARNING: No structure found for chapter {chapter_num}")
            continue

        files_created = split_chapter_by_pericopes(
            romanian_verses,
            BOOK_NAME,
            chapter_num,
            book_structure,
            OUTPUT_DIR
        )

        total_pericopes += files_created
        print(f"  OK - Created {files_created} pericope files")
        print()

    # Final summary
    print("="*80)
    print("EXTRACTION COMPLETE")
    print("="*80)
    print(f"\nBook: {BOOK_NAME}")
    print(f"Chapters: 16")
    print(f"Total verses scraped: {total_verses}")
    print(f"Total pericope files: {total_pericopes}")
    print(f"\nOutput directory: {OUTPUT_DIR}/")
    print(f"Temp chapter files: {TEMP_DIR}/")
    print()

    # Verify file count
    actual_files = len([f for f in os.listdir(OUTPUT_DIR) if f.endswith('.md')])
    print(f"Verification: {actual_files} markdown files created")

    if actual_files == 94:
        print("SUCCESS: All 94 pericopes extracted (matches English version)")
    else:
        print(f"WARNING: Expected 94 files, found {actual_files}")

if __name__ == "__main__":
    extract_mark_complete()
