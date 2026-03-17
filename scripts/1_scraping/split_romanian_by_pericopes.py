import json
import os
import re

def load_romanian_verses(verses_file):
    """Load Romanian verses from JSON file"""
    with open(verses_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_pericope_structure(structure_file):
    """Load pericope structure from JSON file"""
    with open(structure_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def split_chapter_by_pericopes(romanian_verses, book_name, chapter_num, pericope_structure, output_dir):
    """
    Split Romanian chapter verses according to pericope structure

    Args:
        romanian_verses: List of verse dicts [{"verse_num": 1, "text": "..."}]
        book_name: Name of the book (e.g., "Mark")
        chapter_num: Chapter number
        pericope_structure: Dict with pericope info for this chapter
        output_dir: Output directory to save pericope files

    Returns:
        Number of pericope files created
    """
    # Create verse lookup for easy access
    verse_lookup = {v['verse_num']: v['text'] for v in romanian_verses}

    # Get pericopes for this chapter
    chapter_key = str(chapter_num)
    if chapter_key not in pericope_structure:
        print(f"Warning: No pericope structure found for chapter {chapter_num}")
        return 0

    pericopes = pericope_structure[chapter_key]

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    files_created = 0

    for pericope in pericopes:
        pericope_num = pericope['pericope_num']
        title = pericope['title']
        start_verse = pericope['start_verse']
        end_verse = pericope['end_verse']

        # Extract verses for this pericope
        pericope_verses = []
        for verse_num in range(start_verse, end_verse + 1):
            if verse_num in verse_lookup:
                pericope_verses.append({
                    'verse_num': verse_num,
                    'text': verse_lookup[verse_num]
                })
            else:
                print(f"  Warning: Verse {verse_num} not found in Romanian text")

        if not pericope_verses:
            print(f"  Warning: No verses found for pericope {pericope_num}")
            continue

        # Format content
        content_lines = [f"# {title}", ""]

        for verse in pericope_verses:
            content_lines.append(f"{verse['verse_num']}. {verse['text']}")

        content = '\n'.join(content_lines)

        # Create filename matching English version
        chapter_str = str(chapter_num).zfill(2)
        filename = f"({book_name} {chapter_str}.{pericope_num}) {title}.md"
        filepath = os.path.join(output_dir, filename)

        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        files_created += 1
        print(f"  Created: {filename}")

    return files_created

def split_single_chapter(verses_file, structure_file, book_name, chapter_num, output_dir):
    """
    Split a single chapter - convenience function for testing

    Args:
        verses_file: JSON file with Romanian verses
        structure_file: JSON file with pericope structure
        book_name: Book name (e.g., "Mark")
        chapter_num: Chapter number
        output_dir: Output directory
    """
    print(f"Splitting {book_name} chapter {chapter_num}...")
    print('='*60)

    # Load data
    romanian_verses = load_romanian_verses(verses_file)
    structure_data = load_pericope_structure(structure_file)

    # Get structure for this book
    if book_name not in structure_data:
        print(f"Error: Book '{book_name}' not found in structure file")
        return

    book_structure = structure_data[book_name]

    # Split chapter
    files_created = split_chapter_by_pericopes(
        romanian_verses,
        book_name,
        chapter_num,
        book_structure,
        output_dir
    )

    print('='*60)
    print(f"Created {files_created} pericope files in {output_dir}/")

def split_entire_book(book_name, structure_file, romanian_chapters_dir, output_base_dir):
    """
    Split all chapters of a book using scraped Romanian chapters

    Args:
        book_name: Book name (e.g., "Mark")
        structure_file: JSON file with pericope structure
        romanian_chapters_dir: Directory containing Romanian chapter JSON files
        output_base_dir: Base output directory (e.g., "Romanian Bible/New Testament")
    """
    print(f"\n{'='*60}")
    print(f"Splitting {book_name} into pericopes")
    print('='*60)

    # Load structure
    structure_data = load_pericope_structure(structure_file)

    if book_name not in structure_data:
        print(f"Error: Book '{book_name}' not found in structure file")
        return

    book_structure = structure_data[book_name]

    # Create output directory for book
    output_dir = os.path.join(output_base_dir, book_name)
    os.makedirs(output_dir, exist_ok=True)

    total_files = 0

    # Process each chapter
    for chapter_num in sorted([int(k) for k in book_structure.keys()]):
        # Load Romanian verses for this chapter
        chapter_file = os.path.join(romanian_chapters_dir, f"{book_name}_ch{chapter_num:02d}.json")

        if not os.path.exists(chapter_file):
            print(f"  Warning: Chapter file not found: {chapter_file}")
            continue

        romanian_verses = load_romanian_verses(chapter_file)

        print(f"\nChapter {chapter_num}: {len(romanian_verses)} verses")

        # Split by pericopes
        files_created = split_chapter_by_pericopes(
            romanian_verses,
            book_name,
            chapter_num,
            book_structure,
            output_dir
        )

        total_files += files_created

    print(f"\n{'='*60}")
    print(f"{book_name}: {total_files} pericope files created")
    print(f"Output: {output_dir}/")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 5:
        print("Usage: python split_romanian_by_pericopes.py <verses_file> <structure_file> <book_name> <chapter_num> <output_dir>")
        print("Example: python split_romanian_by_pericopes.py mark_ch1_ro.json mark_structure.json Mark 1 \"Romanian Bible/New Testament/Mark\"")
        sys.exit(1)

    verses_file = sys.argv[1]
    structure_file = sys.argv[2]
    book_name = sys.argv[3]
    chapter_num = int(sys.argv[4])
    output_dir = sys.argv[5]

    split_single_chapter(verses_file, structure_file, book_name, chapter_num, output_dir)
