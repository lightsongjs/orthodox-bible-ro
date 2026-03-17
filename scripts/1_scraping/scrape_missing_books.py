"""
Scrape the 3 missing Orthodox books from bibliaortodoxa.ro
- III Ezra (ID: 24)
- Epistola lui Ieremia (ID: 20)
- III Macabei (ID: 51)

These books will be scraped by chapter (not split by pericopes)
"""
import os
import json
import time
import sys
import io
from scrape_romanian_chapter import scrape_romanian_chapter

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MISSING_BOOKS = [
    {
        "english_name": "3_Esdras",
        "romanian_name": "III Ezra",
        "id": 24,
        "testament": "Old Testament",
        "max_chapters": 10  # Estimated max chapters
    },
    {
        "english_name": "Epistle_of_Jeremiah",
        "romanian_name": "Epistola lui Ieremia",
        "id": 20,
        "testament": "Old Testament",
        "max_chapters": 5  # Likely just 1 chapter, but check up to 5
    },
    {
        "english_name": "3_Maccabees",
        "romanian_name": "III Macabei",
        "id": 51,
        "testament": "Old Testament",
        "max_chapters": 10  # Estimated max chapters
    }
]

def create_chapter_markdown(book_info, chapter_num, verses, book_num):
    """
    Create a markdown file for a chapter

    Args:
        book_info: Book information dict
        chapter_num: Chapter number
        verses: List of verse dicts
        book_num: Book number for filename

    Returns:
        str: Markdown content
    """
    # Create frontmatter
    frontmatter = f"""---
testament: OT
book: {book_info['english_name']}
romanian_book: {book_info['romanian_name']}
chapter: {chapter_num}
source: bibliaortodoxa.ro
book_id: {book_info['id']}
---

# {book_info['romanian_name']} - Capitolul {chapter_num}

"""

    # Add verses
    verses_text = ""
    for verse in verses:
        verses_text += f"{verse['verse_num']}. {verse['text']}\n"

    return frontmatter + verses_text

def scrape_missing_book(book_info, output_base_dir, book_num):
    """
    Scrape a single missing book by chapters

    Args:
        book_info: Book information dict
        output_base_dir: Base output directory
        book_num: Book number for folder naming

    Returns:
        dict: Statistics about the scraping
    """
    print(f"\n{'='*80}")
    print(f"Scraping: {book_info['romanian_name']} (ID: {book_info['id']})")
    print('='*80)

    # Create output directory
    book_folder = f"{book_num:02d} {book_info['romanian_name']}"
    output_dir = os.path.join(output_base_dir, book_info['testament'], book_folder)
    os.makedirs(output_dir, exist_ok=True)

    total_chapters = 0
    total_verses = 0

    # Scrape chapters
    for chapter_num in range(1, book_info['max_chapters'] + 1):
        print(f"  Chapter {chapter_num}...", end=" ")

        verses = scrape_romanian_chapter(book_info['id'], chapter_num, delay=2.0)

        if not verses:
            print("No content - end of book")
            break

        print(f"Found {len(verses)} verses")

        total_chapters += 1
        total_verses += len(verses)

        # Create markdown file
        filename = f"({book_num:02d} {book_info['english_name']} {chapter_num:02d}.00) Capitolul {chapter_num}.md"
        filepath = os.path.join(output_dir, filename)

        markdown_content = create_chapter_markdown(book_info, chapter_num, verses, book_num)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"    → Saved: {filename}")

    print(f"\n✓ {book_info['romanian_name']}: {total_chapters} chapters, {total_verses} verses")

    return {
        'book': book_info['romanian_name'],
        'chapters': total_chapters,
        'verses': total_verses
    }

def main():
    """Main execution"""
    print("="*80)
    print("SCRAPING MISSING ORTHODOX BOOKS")
    print("="*80)
    print()

    output_base_dir = "Romanian Bible"

    # Ensure testament directories exist
    os.makedirs(os.path.join(output_base_dir, "Old Testament"), exist_ok=True)

    # Book numbers for the missing books in the 77-book system
    book_numbers = {
        "III Ezra": 17,
        "Epistola lui Ieremia": 33,
        "III Macabei": 50
    }

    results = []

    for book_info in MISSING_BOOKS:
        book_num = book_numbers[book_info['romanian_name']]
        result = scrape_missing_book(book_info, output_base_dir, book_num)
        results.append(result)

    # Summary
    print()
    print("="*80)
    print("SCRAPING COMPLETE")
    print("="*80)
    print()

    total_chapters = sum(r['chapters'] for r in results)
    total_verses = sum(r['verses'] for r in results)

    print(f"Total: {len(results)} books, {total_chapters} chapters, {total_verses} verses")
    print()

    for result in results:
        print(f"  {result['book']}: {result['chapters']} chapters, {result['verses']} verses")

    print()
    print(f"Output: {output_base_dir}/Old Testament/")

if __name__ == "__main__":
    main()
