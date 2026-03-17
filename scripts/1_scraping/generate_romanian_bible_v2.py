"""
Extract the entire Romanian Orthodox Bible - VERSION 2
Uses Romanian book names for folders and English names for pericope matching
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

def scrape_and_split_book_v2(romanian_name, book_info, pericope_structure_all, output_base_dir, name_mapping):
    """
    Scrape and split a single book using Romanian name

    Args:
        romanian_name: Romanian book name (e.g., "Matei")
        book_info: Book data from romanian_book_ids.json
        pericope_structure_all: Complete pericope structure for all books
        output_base_dir: Base output directory
        name_mapping: Romanian to English name mapping
    """
    # Get English name for pericope structure lookup
    english_name = name_mapping.get(romanian_name)

    if not english_name:
        safe_print(f"[SKIP] {romanian_name}: No English mapping found")
        return {
            'romanian_name': romanian_name,
            'english_name': None,
            'chapters': 0,
            'pericopes': 0,
            'success': False,
            'error': 'No English mapping'
        }

    book_id = book_info['id']

    try:
        safe_print(f"[STARTED] {romanian_name} -> {english_name} (ID: {book_id})")

        # Check if we have pericope structure for English name
        if english_name not in pericope_structure_all:
            safe_print(f"[SKIP] {romanian_name}: No pericope structure for {english_name}")
            return {
                'romanian_name': romanian_name,
                'english_name': english_name,
                'chapters': 0,
                'pericopes': 0,
                'success': False,
                'error': f'No pericope structure for {english_name}'
            }

        book_structure = pericope_structure_all[english_name]

        # Determine testament
        testament = get_testament(english_name)
        # Use Romanian name for folder
        output_dir = os.path.join(output_base_dir, testament, romanian_name)
        os.makedirs(output_dir, exist_ok=True)

        total_chapters = 0
        total_pericopes = 0
        total_verses = 0

        # Process each chapter
        for chapter_num in sorted([int(k) for k in book_structure.keys()]):
            # Scrape Romanian chapter
            romanian_verses = scrape_romanian_chapter(book_id, chapter_num, delay=0.2)

            if not romanian_verses:
                safe_print(f"[WARN] {romanian_name} {chapter_num}: No content")
                break

            total_chapters += 1
            total_verses += len(romanian_verses)

            # Split by pericopes using ENGLISH name for filename compatibility
            files_created = split_chapter_by_pericopes(
                romanian_verses,
                english_name,  # Use English name in filenames for consistency
                chapter_num,
                book_structure,
                output_dir
            )

            total_pericopes += files_created

        safe_print(f"[DONE] {romanian_name}: {total_chapters} ch, {total_pericopes} pericopes, {total_verses} verses")

        return {
            'romanian_name': romanian_name,
            'english_name': english_name,
            'chapters': total_chapters,
            'pericopes': total_pericopes,
            'verses': total_verses,
            'success': True
        }

    except Exception as e:
        safe_print(f"[ERROR] {romanian_name}: {e}")
        return {
            'romanian_name': romanian_name,
            'english_name': english_name,
            'chapters': 0,
            'pericopes': 0,
            'error': str(e),
            'success': False
        }

def get_testament(english_name):
    """Determine testament for a book using English name"""
    nt_books = [
        "Matthew", "Mark", "Luke", "John", "Acts",
        "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
        "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
        "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews",
        "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John",
        "Jude", "Revelation"
    ]
    return "New Testament" if english_name in nt_books else "Old Testament"

def extract_romanian_bible_v2(max_workers=10):
    """
    Extract entire Romanian Bible using Romanian book names

    Args:
        max_workers: Number of parallel workers (default: 10)
    """
    print("="*80)
    print("EXTRACTING COMPLETE ROMANIAN ORTHODOX BIBLE - VERSION 2")
    print("Using Romanian book names for folders")
    print("="*80)
    print()

    overall_start = time.time()

    # Load Romanian to English name mapping
    print("Loading Romanian-English name mapping...")
    with open('romanian_english_book_names.json', 'r', encoding='utf-8') as f:
        name_mapping = json.load(f)
    print(f"  {len(name_mapping)} book names mapped")

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

    # Create reverse mapping (English -> Book ID info)
    english_to_id = {data['romanian_name']: data for data in book_ids.values()}

    # Prepare book list using Romanian names
    book_list = [(rom_name, english_to_id[rom_name]) for rom_name in name_mapping.keys()
                 if rom_name in english_to_id]

    print(f"Starting extraction with {max_workers} parallel workers...")
    print(f"Processing {len(book_list)} books")
    print()

    results = []

    # Use ThreadPoolExecutor to run multiple books in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all book extraction tasks
        future_to_book = {
            executor.submit(scrape_and_split_book_v2, romanian_name, book_info,
                          pericope_structure_all, output_base_dir, name_mapping): romanian_name
            for romanian_name, book_info in book_list
        }

        # Collect results as they complete
        completed = 0
        for future in as_completed(future_to_book):
            result = future.result()
            results.append(result)
            completed += 1

            if result['success']:
                safe_print(f"[{completed}/{len(book_list)}] Completed: {result['romanian_name']}")

    overall_end = time.time()
    total_elapsed = overall_end - overall_start

    # Calculate totals
    total_chapters = sum(r['chapters'] for r in results if r['success'])
    total_pericopes = sum(r['pericopes'] for r in results if r['success'])
    total_verses = sum(r.get('verses', 0) for r in results if r['success'])
    successful = sum(1 for r in results if r['success'])
    failed = sum(1 for r in results if not r['success'])

    # Separate by testament
    nt_results = [r for r in results if r['success'] and r['english_name'] and
                  get_testament(r['english_name']) == "New Testament"]
    ot_results = [r for r in results if r['success'] and r['english_name'] and
                  get_testament(r['english_name']) == "Old Testament"]

    # Final summary
    print()
    print("="*80)
    print("COMPLETE ROMANIAN BIBLE EXTRACTION FINISHED - VERSION 2")
    print("="*80)
    print(f"\nTotal time: {total_elapsed:.1f} seconds ({total_elapsed/60:.1f} minutes)")
    print(f"\nSuccessful: {successful}/{len(book_list)} books")
    if failed > 0:
        print(f"Failed: {failed}/{len(book_list)} books")
    print(f"\nTotal chapters: {total_chapters}")
    print(f"Total pericopes: {total_pericopes}")
    print(f"Total verses: {total_verses}")
    print(f"\nNew Testament: {len(nt_results)} books, {sum(r['pericopes'] for r in nt_results)} pericopes")
    print(f"Old Testament: {len(ot_results)} books, {sum(r['pericopes'] for r in ot_results)} pericopes")
    print(f"\nOutput: {output_base_dir}/")

    # Show any books with errors
    errors = [r for r in results if not r['success']]
    if errors:
        print(f"\nWARNING - {len(errors)} books had errors:")
        for r in errors:
            print(f"  - {r['romanian_name']}: {r.get('error', 'Unknown error')}")

    return results

if __name__ == "__main__":
    extract_romanian_bible_v2(max_workers=10)
