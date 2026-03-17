#!/usr/bin/env python3
"""
Simplified script to download all chapters from the Romanian Orthodox Bible.
This version does everything in one pass:
- Downloads all chapters
- Adds book_number and chapter_count fields
- Saves files with proper naming: ##_RomanianName.json
"""

import json
import requests
from bs4 import BeautifulSoup
import time
from pathlib import Path

def fetch_chapter(book_id, chapter_num):
    """Fetch a specific chapter from a book."""
    url = f"https://www.bibliaortodoxa.ro/carte.php?id={book_id}&cap={chapter_num}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract verses from table rows
        verses = []

        # Find all table rows with verse content
        verse_rows = soup.find_all('tr', id=lambda x: x and x.startswith('verset'))

        if not verse_rows:
            print(f"Warning: No verses found for book_id={book_id}, chapter={chapter_num}")
            return None

        for row in verse_rows:
            # Find the verse number
            verse_num_span = row.find('span', class_='nr')
            if not verse_num_span:
                continue

            verse_num = verse_num_span.get_text(strip=True).replace('.', '')

            # Find the verse text - it's in the second td
            tds = row.find_all('td')
            if len(tds) >= 2:
                verse_text = tds[1].get_text(strip=True)

                verses.append({
                    "verse": int(verse_num) if verse_num.isdigit() else verse_num,
                    "text": verse_text
                })

        if not verses:
            print(f"Warning: Could not extract verses for book_id={book_id}, chapter={chapter_num}")
            return None

        return {
            "chapter": chapter_num,
            "verses": verses,
            "url": url
        }

    except requests.RequestException as e:
        print(f"Error fetching chapter {chapter_num} of book {book_id}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error for book {book_id}, chapter {chapter_num}: {e}")
        return None

def download_all_chapters():
    """Download all chapters for all books with complete metadata."""

    # Load metadata
    with open('bible_books_metadata.json', 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    # Create output directory
    output_dir = Path('bible_books')
    output_dir.mkdir(exist_ok=True)

    # Statistics
    stats = {
        'total_books': 0,
        'total_chapters': 0,
        'successful_chapters': 0,
        'failed_chapters': 0
    }

    book_number = 1

    # Process both testaments
    for testament_name in ['old_testament', 'new_testament']:
        testament_display = "OLD TESTAMENT" if testament_name == "old_testament" else "NEW TESTAMENT"
        print(f"\n{'='*70}")
        print(f"{testament_display}")
        print('='*70)

        books = metadata[testament_name]
        stats['total_books'] += len(books)

        for book in books:
            book_id = book['id']
            name_en = book['name_en']
            name_ro = book['name_ro']
            num_chapters = book['chapters']

            stats['total_chapters'] += num_chapters

            print(f"\nBook #{book_number:2d}: {name_en} ({name_ro}) - {num_chapters} chapters")

            # Create book data with all fields including book_number and chapter_count
            book_data = {
                'id': book_id,
                'book_number': book_number,
                'name_en': name_en,
                'name_ro': name_ro,
                'chapter_count': num_chapters,
                'url': book['url'],
                'chapters': []
            }

            for chapter_num in range(1, num_chapters + 1):
                print(f"  Chapter {chapter_num:3d}/{num_chapters}...", end=' ')

                chapter_data = fetch_chapter(book_id, chapter_num)

                if chapter_data:
                    book_data['chapters'].append(chapter_data)
                    stats['successful_chapters'] += 1
                    print("✓")
                else:
                    stats['failed_chapters'] += 1
                    print("✗")

                # Be nice to the server
                time.sleep(0.5)

            # Save book data to file with Romanian name and book number
            safe_name_ro = name_ro.replace(' ', '_').replace('/', '_')
            output_file = output_dir / f"{book_number:02d}_{safe_name_ro}.json"

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(book_data, f, ensure_ascii=False, indent=2)

            print(f"  ✓ Saved to {output_file}")

            book_number += 1

    # Print statistics
    print("\n" + "="*70)
    print("DOWNLOAD COMPLETE")
    print("="*70)
    print(f"Total books: {stats['total_books']}")
    print(f"Total chapters: {stats['total_chapters']}")
    print(f"Successful: {stats['successful_chapters']}")
    print(f"Failed: {stats['failed_chapters']}")

    if stats['total_chapters'] > 0:
        success_rate = stats['successful_chapters'] / stats['total_chapters'] * 100
        print(f"Success rate: {success_rate:.1f}%")

    # Save statistics
    with open('download_stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

    print(f"\nFiles saved in: {output_dir}/")
    print("Format: ##_RomanianName.json (e.g., 01_Facerea.json)")

if __name__ == '__main__':
    download_all_chapters()
