import os
import re
import json
from collections import defaultdict

def parse_verse_numbers(content):
    """
    Extract verse numbers from pericope content

    Args:
        content: Text content from markdown file

    Returns:
        tuple: (start_verse, end_verse) as integers
    """
    # Remove the heading line (starts with #)
    lines = content.strip().split('\n')
    verse_lines = [line for line in lines if line.strip() and not line.startswith('#')]

    if not verse_lines:
        return None, None

    # Extract verse numbers from lines like "1. Text..." or "12. Text..."
    verse_numbers = []
    for line in verse_lines:
        match = re.match(r'^(\d+)\.', line.strip())
        if match:
            verse_numbers.append(int(match.group(1)))

    if not verse_numbers:
        return None, None

    return min(verse_numbers), max(verse_numbers)

def extract_book_structure(testament_dir, book_name):
    """
    Extract pericope structure for a single book

    Args:
        testament_dir: Path to testament directory (e.g., "New Testament")
        book_name: Name of the book (e.g., "Mark")

    Returns:
        dict: Chapter-organized pericope structure
    """
    book_path = os.path.join(testament_dir, book_name)

    if not os.path.exists(book_path):
        print(f"Book not found: {book_path}")
        return None

    # Get all markdown files
    files = sorted([f for f in os.listdir(book_path) if f.endswith('.md')])

    print(f"Found {len(files)} pericope files for {book_name}")

    # Parse filenames to extract chapter, pericope number, and title
    # Format: (Book CC.PP) Title.md
    # Example: (Mark 01.01) The Proclamation of John the Baptist.md

    book_structure = defaultdict(list)

    # Handle book names with spaces by replacing underscores with spaces
    book_name_display = book_name.replace('_', ' ')
    pattern = re.compile(rf'^\({re.escape(book_name_display)} (\d+)\.(\d+)\) (.+)\.md$')

    for filename in files:
        match = pattern.match(filename)
        if not match:
            print(f"  Warning: Could not parse filename: {filename}")
            continue

        chapter_num = int(match.group(1))
        pericope_num = match.group(2)  # Keep as string with leading zero
        title = match.group(3)

        # Read file content to get verse range
        filepath = os.path.join(book_path, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        start_verse, end_verse = parse_verse_numbers(content)

        if start_verse is None:
            print(f"  Warning: Could not extract verses from: {filename}")
            continue

        book_structure[chapter_num].append({
            'pericope_num': pericope_num,
            'title': title,
            'start_verse': start_verse,
            'end_verse': end_verse,
            'filename': filename
        })

    # Convert to regular dict and sort chapters
    return dict(sorted(book_structure.items()))

def extract_all_books_structure(output_file='pericope_structure.json'):
    """
    Extract pericope structure from all books in both testaments

    Args:
        output_file: JSON file to save structure
    """
    all_structure = {}

    testaments = ['New Testament', 'Old Testament']

    for testament in testaments:
        if not os.path.exists(testament):
            print(f"Testament directory not found: {testament}")
            continue

        print(f"\n{'='*60}")
        print(f"Processing {testament}")
        print('='*60)

        # Get all book directories
        books = sorted([d for d in os.listdir(testament)
                       if os.path.isdir(os.path.join(testament, d))])

        for book in books:
            print(f"\nExtracting structure for {book}...")
            structure = extract_book_structure(testament, book)

            if structure:
                all_structure[book] = structure

                # Print summary
                total_pericopes = sum(len(pericopes) for pericopes in structure.values())
                print(f"  OK - {len(structure)} chapters, {total_pericopes} pericopes")

    # Save to JSON
    print(f"\n{'='*60}")
    print(f"Saving structure to {output_file}")
    print('='*60)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_structure, f, indent=2, ensure_ascii=False)

    # Print final summary
    total_books = len(all_structure)
    total_pericopes = sum(
        sum(len(pericopes) for pericopes in book.values())
        for book in all_structure.values()
    )

    print(f"\nExtraction complete!")
    print(f"  Books: {total_books}")
    print(f"  Total pericopes: {total_pericopes}")
    print(f"  Output: {output_file}")

    return all_structure

def extract_single_book(book_name, testament='New Testament', output_file=None):
    """
    Extract pericope structure for a single book (for testing)

    Args:
        book_name: Name of the book (e.g., "Mark")
        testament: Testament directory
        output_file: Optional JSON file to save structure
    """
    print(f"Extracting pericope structure for {book_name}...")
    print('='*60)

    structure = extract_book_structure(testament, book_name)

    if structure:
        # Print detailed structure
        total_pericopes = 0
        for chapter_num, pericopes in sorted(structure.items()):
            print(f"\nChapter {chapter_num}: {len(pericopes)} pericopes")
            for p in pericopes:
                print(f"  {p['pericope_num']}: {p['title']} (verses {p['start_verse']}-{p['end_verse']})")
                total_pericopes += 1

        print(f"\n{'='*60}")
        print(f"Total: {len(structure)} chapters, {total_pericopes} pericopes")

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({book_name: structure}, f, indent=2, ensure_ascii=False)
            print(f"Saved to: {output_file}")

        return structure
    else:
        print(f"Failed to extract structure for {book_name}")
        return None

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Extract single book for testing
        book_name = sys.argv[1]
        output_file = f"{book_name.lower()}_structure.json"
        extract_single_book(book_name, output_file=output_file)
    else:
        # Extract all books
        extract_all_books_structure()
