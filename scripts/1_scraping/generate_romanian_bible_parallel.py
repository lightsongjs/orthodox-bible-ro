"""
Extract the entire Romanian Orthodox Bible in parallel
Using English pericope structure to split Romanian chapters
"""
import os
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from scrape_romanian_chapter import scrape_romanian_chapter
from split_romanian_by_pericopes import split_chapter_by_pericopes, load_pericope_structure

# Thread-safe printing
print_lock = threading.Lock()

def safe_print(message):
    """Thread-safe print function"""
    with print_lock:
        print(message)

def scrape_and_split_book(book_info, pericope_structure_all, output_base_dir):
    """
    Scrape and split a single book - designed to run in parallel

    Args:
        book_info: Tuple of (book_name, book_data) from romanian_book_ids.json
        pericope_structure_all: Complete pericope structure for all books
        output_base_dir: Base output directory (e.g., "Romanian Bible")

    Returns:
        dict: Results with success/error info
    """
    book_name, book_data = book_info
    book_id = book_data['id']
    romanian_name = book_data['romanian_name']

    try:
        safe_print(f"[STARTED] {book_name} (ID: {book_id})")

        # Check if we have pericope structure for this book
        if book_name not in pericope_structure_all:
            safe_print(f"[SKIP] {book_name}: No pericope structure found")
            return {
                'book': book_name,
                'chapters': 0,
                'pericopes': 0,
                'success': False,
                'error': 'No pericope structure'
            }

        book_structure = pericope_structure_all[book_name]

        # Determine testament
        testament = get_testament(book_name)
        output_dir = os.path.join(output_base_dir, testament, book_name)
        os.makedirs(output_dir, exist_ok=True)

        total_chapters = 0
        total_pericopes = 0
        total_verses = 0

        # Process each chapter
        for chapter_num in sorted([int(k) for k in book_structure.keys()]):
            # Scrape Romanian chapter
            romanian_verses = scrape_romanian_chapter(book_id, chapter_num, delay=0.3)

            if not romanian_verses:
                safe_print(f"[WARN] {book_name} {chapter_num}: No content")
                break

            total_chapters += 1
            total_verses += len(romanian_verses)

            # Split by pericopes
            files_created = split_chapter_by_pericopes(
                romanian_verses,
                book_name,
                chapter_num,
                book_structure,
                output_dir
            )

            total_pericopes += files_created

        safe_print(f"[DONE] {book_name}: {total_chapters} ch, {total_pericopes} pericopes, {total_verses} verses")

        return {
            'book': book_name,
            'chapters': total_chapters,
            'pericopes': total_pericopes,
            'verses': total_verses,
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

def get_testament(book_name):
    """Determine testament for a book"""
    nt_books = [
        "Matthew", "Mark", "Luke", "John", "Acts",
        "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
        "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
        "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews",
        "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John",
        "Jude", "Revelation"
    ]
    return "New Testament" if book_name in nt_books else "Old Testament"

def extract_romanian_bible_parallel(max_workers=10):
    """
    Extract entire Romanian Bible in parallel

    Args:
        max_workers: Number of parallel workers (default: 10)
    """
    print("="*80)
    print("EXTRACTING COMPLETE ROMANIAN ORTHODOX BIBLE")
    print("="*80)
    print()

    overall_start = time.time()

    # Load book IDs
    print("Loading book ID mappings...")
    with open('romanian_book_ids.json', 'r', encoding='utf-8') as f:
        book_ids = json.load(f)
    print(f"  {len(book_ids)} books found")

    # Load pericope structure
    print("Loading pericope structure...")
    pericope_structure_all = load_pericope_structure('pericope_structure.json')
    print(f"  Structure loaded for {len(pericope_structure_all)} books")
    print()

    # Create output directories
    output_base_dir = "Romanian Bible"
    os.makedirs(os.path.join(output_base_dir, "New Testament"), exist_ok=True)
    os.makedirs(os.path.join(output_base_dir, "Old Testament"), exist_ok=True)

    # Prepare book list
    book_list = list(book_ids.items())

    print(f"Starting extraction with {max_workers} parallel workers...")
    print()

    results = []

    # Use ThreadPoolExecutor to run multiple books in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all book extraction tasks
        future_to_book = {
            executor.submit(scrape_and_split_book, book_info, pericope_structure_all, output_base_dir): book_info[0]
            for book_info in book_list
        }

        # Collect results as they complete
        completed = 0
        for future in as_completed(future_to_book):
            result = future.result()
            results.append(result)
            completed += 1

            if result['success']:
                safe_print(f"[{completed}/{len(book_list)}] Completed: {result['book']}")

    overall_end = time.time()
    total_elapsed = overall_end - overall_start

    # Calculate totals
    total_chapters = sum(r['chapters'] for r in results if r['success'])
    total_pericopes = sum(r['pericopes'] for r in results if r['success'])
    total_verses = sum(r.get('verses', 0) for r in results if r['success'])
    successful = sum(1 for r in results if r['success'])
    failed = sum(1 for r in results if not r['success'])

    # Separate by testament
    nt_results = [r for r in results if r['success'] and get_testament(r['book']) == "New Testament"]
    ot_results = [r for r in results if r['success'] and get_testament(r['book']) == "Old Testament"]

    # Final summary
    print()
    print("="*80)
    print("COMPLETE ROMANIAN BIBLE EXTRACTION FINISHED")
    print("="*80)
    print(f"\nTotal time: {total_elapsed:.1f} seconds ({total_elapsed/60:.1f} minutes)")
    print(f"\nSuccessful: {successful}/{len(book_list)} books")
    if failed > 0:
        print(f"Failed: {failed}/{len(book_list)} books")
    print(f"\nTotal chapters: {total_chapters}")
    print(f"Total pericopes: {total_pericopes}")
    print(f"Total verses: {total_verses}")
    print(f"\nNew Testament: {len(nt_results)} books")
    print(f"Old Testament: {len(ot_results)} books")
    print(f"\nOutput: {output_base_dir}/")

    # Show any books with errors
    errors = [r for r in results if not r['success']]
    if errors:
        print(f"\nWARNING - {len(errors)} books had errors:")
        for r in errors:
            print(f"  - {r['book']}: {r.get('error', 'Unknown error')}")

    return results

if __name__ == "__main__":
    extract_romanian_bible_parallel(max_workers=10)
