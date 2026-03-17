from scrape_biblegateway import scrape_book_from_biblegateway
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import os

# All Old Testament books (39 books)
OT_BOOKS = [
    ("Genesis", "Genesis"),
    ("Exodus", "Exodus"),
    ("Leviticus", "Leviticus"),
    ("Numbers", "Numbers"),
    ("Deuteronomy", "Deuteronomy"),
    ("Joshua", "Joshua"),
    ("Judges", "Judges"),
    ("Ruth", "Ruth"),
    ("1 Samuel", "1%20Samuel"),
    ("2 Samuel", "2%20Samuel"),
    ("1 Kings", "1%20Kings"),
    ("2 Kings", "2%20Kings"),
    ("1 Chronicles", "1%20Chronicles"),
    ("2 Chronicles", "2%20Chronicles"),
    ("Ezra", "Ezra"),
    ("Nehemiah", "Nehemiah"),
    ("Tobit", "Tobit"),
    ("Judith", "Judith"),
    ("Esther", "Esther"),
    ("1 Maccabees", "1%20Maccabees"),
    ("2 Maccabees", "2%20Maccabees"),
    ("Job", "Job"),
    ("Psalms", "Psalms"),
    ("Proverbs", "Proverbs"),
    ("Ecclesiastes", "Ecclesiastes"),
    ("Song of Solomon", "Song%20of%20Solomon"),
    ("Wisdom", "Wisdom"),
    ("Sirach", "Sirach"),
    ("Isaiah", "Isaiah"),
    ("Jeremiah", "Jeremiah"),
    ("Lamentations", "Lamentations"),
    ("Baruch", "Baruch"),
    ("Ezekiel", "Ezekiel"),
    ("Daniel", "Daniel"),
    ("Hosea", "Hosea"),
    ("Joel", "Joel"),
    ("Amos", "Amos"),
    ("Obadiah", "Obadiah"),
    ("Jonah", "Jonah"),
    ("Micah", "Micah"),
    ("Nahum", "Nahum"),
    ("Habakkuk", "Habakkuk"),
    ("Zephaniah", "Zephaniah"),
    ("Haggai", "Haggai"),
    ("Zechariah", "Zechariah"),
    ("Malachi", "Malachi"),
]

# All New Testament books (27 books)
NT_BOOKS = [
    ("Matthew", "Matthew"),
    ("Mark", "Mark"),
    ("Luke", "Luke"),
    ("John", "John"),
    ("Acts", "Acts"),
    ("Romans", "Romans"),
    ("1 Corinthians", "1%20Corinthians"),
    ("2 Corinthians", "2%20Corinthians"),
    ("Galatians", "Galatians"),
    ("Ephesians", "Ephesians"),
    ("Philippians", "Philippians"),
    ("Colossians", "Colossians"),
    ("1 Thessalonians", "1%20Thessalonians"),
    ("2 Thessalonians", "2%20Thessalonians"),
    ("1 Timothy", "1%20Timothy"),
    ("2 Timothy", "2%20Timothy"),
    ("Titus", "Titus"),
    ("Philemon", "Philemon"),
    ("Hebrews", "Hebrews"),
    ("James", "James"),
    ("1 Peter", "1%20Peter"),
    ("2 Peter", "2%20Peter"),
    ("1 John", "1%20John"),
    ("2 John", "2%20John"),
    ("3 John", "3%20John"),
    ("Jude", "Jude"),
    ("Revelation", "Revelation"),
]

# Thread-safe printing
print_lock = threading.Lock()

def safe_print(message):
    """Thread-safe print function"""
    with print_lock:
        print(message)

def scrape_single_book(book_info, output_dir):
    """Scrape a single book - designed to run in parallel"""
    book_name, book_slug = book_info

    try:
        safe_print(f"[STARTED] {book_name}")

        chapters, pericopes = scrape_book_from_biblegateway(
            book_name,
            book_slug,
            max_chapters=200,  # Psalms has 150 chapters
            output_dir=output_dir,
            version="NRSVCE"
        )

        safe_print(f"[DONE] {book_name}: {chapters} chapters, {pericopes} pericopes")

        return {
            'book': book_name,
            'chapters': chapters,
            'pericopes': pericopes,
            'success': True
        }

    except Exception as e:
        safe_print(f"[ERROR] {book_name}: {e}")
        return {
            'book': book_name,
            'chapters': 0,
            'pericopes': 0,
            'error': str(e),
            'success': False
        }

def scrape_testament_parallel(books, testament_name, output_dir, max_workers=10):
    """
    Scrape all books of a testament in parallel

    Args:
        books: List of (book_name, book_slug) tuples
        testament_name: "Old Testament" or "New Testament"
        output_dir: Output directory path
        max_workers: Number of parallel workers (default: 10)
    """

    print("=" * 80)
    print(f"SCRAPING {testament_name.upper()} ({len(books)} books, {max_workers} workers)")
    print("=" * 80)
    print()

    start_time = time.time()
    results = []

    # Use ThreadPoolExecutor to run multiple books in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all book scraping tasks
        future_to_book = {
            executor.submit(scrape_single_book, book_info, output_dir): book_info[0]
            for book_info in books
        }

        # Collect results as they complete
        completed = 0
        for future in as_completed(future_to_book):
            result = future.result()
            results.append(result)
            completed += 1

            if result['success']:
                safe_print(f"[{completed}/{len(books)}] Completed: {result['book']}")

    end_time = time.time()
    elapsed = end_time - start_time

    # Calculate totals
    total_chapters = sum(r['chapters'] for r in results if r['success'])
    total_pericopes = sum(r['pericopes'] for r in results if r['success'])
    successful = sum(1 for r in results if r['success'])
    failed = sum(1 for r in results if not r['success'])

    # Summary
    print("\n" + "=" * 80)
    print(f"{testament_name.upper()} EXTRACTION COMPLETE")
    print("=" * 80)
    print(f"\nTime elapsed: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
    print(f"Successful: {successful}/{len(books)} books")
    if failed > 0:
        print(f"Failed: {failed}/{len(books)} books")
    print(f"Total chapters: {total_chapters}")
    print(f"Total pericopes: {total_pericopes}")
    print(f"\nAll files saved to: {output_dir}/")

    # Show any books with errors
    errors = [r for r in results if not r['success']]
    if errors:
        print(f"\nWARNING - {len(errors)} books had errors:")
        for r in errors:
            print(f"  - {r['book']}: {r.get('error', 'Unknown error')}")

    return results

def scrape_entire_bible():
    """Scrape the entire Bible - both Old and New Testaments"""

    print("\n" + "=" * 80)
    print("STARTING COMPLETE BIBLE EXTRACTION")
    print("=" * 80)
    print()

    overall_start = time.time()

    # Scrape Old Testament
    ot_results = scrape_testament_parallel(
        OT_BOOKS,
        "Old Testament",
        "Old Testament",
        max_workers=10
    )

    print("\n\n")

    # Scrape New Testament
    nt_results = scrape_testament_parallel(
        NT_BOOKS,
        "New Testament",
        "New Testament",
        max_workers=10
    )

    overall_end = time.time()
    total_elapsed = overall_end - overall_start

    # Final summary
    print("\n\n" + "=" * 80)
    print("COMPLETE BIBLE EXTRACTION FINISHED")
    print("=" * 80)
    print(f"\nTotal time: {total_elapsed:.1f} seconds ({total_elapsed/60:.1f} minutes)")
    print(f"\nOld Testament: {len([r for r in ot_results if r['success']])}/46 books")
    print(f"New Testament: {len([r for r in nt_results if r['success']])}/27 books")
    print(f"\nTotal: {len([r for r in ot_results + nt_results if r['success']])}/73 books")

if __name__ == "__main__":
    scrape_entire_bible()
