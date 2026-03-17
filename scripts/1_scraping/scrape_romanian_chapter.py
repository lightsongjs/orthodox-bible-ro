import requests
from bs4 import BeautifulSoup
import json
import time
import re

def scrape_romanian_chapter(book_id, chapter_num, delay=0.5):
    """
    Scrape a chapter from Romanian Orthodox Bible

    Args:
        book_id: Book ID from bibliaortodoxa.ro (e.g., 53 for Mark)
        chapter_num: Chapter number (1-based)
        delay: Delay in seconds between requests (default 0.5)

    Returns:
        List of verse dicts: [{"verse_num": 1, "text": "..."}, ...]
        Returns None if chapter not found or error occurs
    """
    url = f"https://www.bibliaortodoxa.ro/carte.php?id={book_id}&cap={chapter_num}"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            print(f"Error: HTTP {response.status_code}")
            return None

        # Ensure proper encoding for Romanian characters
        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all verse elements
        # They have IDs like "verset1", "verset2", etc.
        verses = []

        verse_num = 1
        while True:
            verse_elem = soup.find(id=f"verset{verse_num}")

            if not verse_elem:
                # No more verses found
                break

            # Extract the text from the verse element
            verse_text = verse_elem.get_text(strip=True)

            # Remove the verse number prefix if it exists (e.g., "1. Text" -> "Text")
            # But keep it for consistency with our format
            verse_text = verse_text.strip()

            # Sometimes the verse number is included in the text, sometimes not
            # Normalize by removing it if present and we'll add it back consistently
            verse_text_cleaned = re.sub(r'^\d+\.\s*', '', verse_text)

            if verse_text_cleaned:
                verses.append({
                    'verse_num': verse_num,
                    'text': verse_text_cleaned
                })

            verse_num += 1

        # Add delay to be respectful to server
        time.sleep(delay)

        return verses if verses else None

    except Exception as e:
        print(f"Error scraping chapter: {e}")
        return None

def scrape_and_save_chapter(book_id, chapter_num, output_file, book_name=None):
    """
    Scrape a chapter and save to JSON file

    Args:
        book_id: Book ID from bibliaortodoxa.ro
        chapter_num: Chapter number
        output_file: JSON file to save verses
        book_name: Optional book name for display
    """
    print(f"Scraping {book_name or f'Book {book_id}'} chapter {chapter_num}...")

    verses = scrape_romanian_chapter(book_id, chapter_num)

    if verses:
        print(f"  Found {len(verses)} verses")

        # Save to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(verses, f, indent=2, ensure_ascii=False)

        print(f"  Saved to: {output_file}")

        # Display first verse as sample
        if verses:
            print(f"  Sample: {verses[0]['verse_num']}. {verses[0]['text'][:60]}...")

        return verses
    else:
        print(f"  No verses found")
        return None

def scrape_entire_book(book_id, book_name, max_chapters=50, output_dir=None):
    """
    Scrape all chapters from a book

    Args:
        book_id: Book ID from bibliaortodoxa.ro
        book_name: Book name for display and output
        max_chapters: Maximum chapters to try (will stop when no content)
        output_dir: Optional directory to save chapter files

    Returns:
        dict: {chapter_num: [verses]}
    """
    print(f"\n{'='*60}")
    print(f"Scraping {book_name} (ID: {book_id})")
    print('='*60)

    all_chapters = {}

    for chapter_num in range(1, max_chapters + 1):
        verses = scrape_romanian_chapter(book_id, chapter_num)

        if not verses:
            print(f"  Chapter {chapter_num}: No content - end of book")
            break

        all_chapters[chapter_num] = verses
        print(f"  Chapter {chapter_num}: {len(verses)} verses")

        # Save individual chapter file if output_dir specified
        if output_dir:
            import os
            os.makedirs(output_dir, exist_ok=True)
            chapter_file = os.path.join(output_dir, f"{book_name}_ch{chapter_num:02d}.json")
            with open(chapter_file, 'w', encoding='utf-8') as f:
                json.dump(verses, f, indent=2, ensure_ascii=False)

    print(f"\n{book_name}: {len(all_chapters)} chapters scraped")

    return all_chapters

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python scrape_romanian_chapter.py <book_id> <chapter_num> [output_file] [book_name]")
        print("Example: python scrape_romanian_chapter.py 53 1 mark_ch1_ro.json Mark")
        sys.exit(1)

    book_id = int(sys.argv[1])
    chapter_num = int(sys.argv[2])
    output_file = sys.argv[3] if len(sys.argv) > 3 else f"chapter_{book_id}_{chapter_num}.json"
    book_name = sys.argv[4] if len(sys.argv) > 4 else None

    scrape_and_save_chapter(book_id, chapter_num, output_file, book_name)
