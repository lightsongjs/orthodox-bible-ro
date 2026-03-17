#!/usr/bin/env python3
"""
Generate markdown files from pericope JSON data.

Creates files with:
- YAML frontmatter metadata
- Navigation links (previous/next pericope)
- Romanian verse text
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class MarkdownGenerator:
    """Generate markdown files from pericope JSON."""

    def __init__(self, pericopes_dir: str, output_dir: str, metadata_path: str):
        """
        Initialize generator.

        Args:
            pericopes_dir: Path to bible_books_pericopes/
            output_dir: Path to output directory (e.g., Biblia_Generata/)
            metadata_path: Path to bible_books_metadata.json
        """
        self.pericopes_dir = Path(pericopes_dir)
        self.output_dir = Path(output_dir)
        self.metadata_path = Path(metadata_path)

        # Load metadata
        with open(self.metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            self.metadata = metadata

        # Create book number to Romanian name mapping
        self.book_num_to_ro_name = {}
        all_books = metadata['old_testament'] + metadata['new_testament']
        for book in all_books:
            # Find the book number by looking at the filename pattern
            for json_file in self.pericopes_dir.glob('*.json'):
                book_data = json.load(open(json_file, 'r', encoding='utf-8'))
                if book_data['id'] == book['id']:
                    self.book_num_to_ro_name[book_data['book_number']] = book['name_ro']
                    break

    def sanitize_filename(self, filename: str) -> str:
        """
        Remove invalid characters from filename.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename safe for Windows/Unix
        """
        # Replace invalid characters with safe alternatives
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        return filename

    def get_pericope_filename(self, book_num: int, book_name_ro: str, chapter: int,
                             pericope_num: str, title: str) -> str:
        """
        Generate filename for pericope markdown file.

        Args:
            book_num: Book number (1-78)
            book_name_ro: Romanian book name
            chapter: Chapter number
            pericope_num: Pericope number (zero-padded string)
            title: Pericope title

        Returns:
            Filename like: (51 Matei 01.01) The Genealogy of Jesus the Messiah.md
        """
        # Sanitize title to remove invalid filename characters
        safe_title = self.sanitize_filename(title)
        return f"({book_num:02d} {book_name_ro} {chapter:02d}.{pericope_num}) {safe_title}.md"

    def get_prev_next_pericopes(self, all_pericopes: List[Dict], current_index: int,
                               all_books_data: List[Dict]) -> tuple:
        """
        Get previous and next pericope filenames for navigation.

        Args:
            all_pericopes: Flattened list of all pericopes across all books
            current_index: Index of current pericope
            all_books_data: List of all book data (for cross-book navigation)

        Returns:
            Tuple of (prev_filename, next_filename) or None if at boundary
        """
        prev_filename = None
        next_filename = None

        if current_index > 0:
            prev = all_pericopes[current_index - 1]
            prev_filename = self.get_pericope_filename(
                prev['book_num'],
                prev['book_name_ro'],
                prev['chapter'],
                prev['pericope_num'],
                prev['title_ro']
            )

        if current_index < len(all_pericopes) - 1:
            next_p = all_pericopes[current_index + 1]
            next_filename = self.get_pericope_filename(
                next_p['book_num'],
                next_p['book_name_ro'],
                next_p['chapter'],
                next_p['pericope_num'],
                next_p['title_ro']
            )

        return prev_filename, next_filename

    def generate_markdown_content(self, pericope: Dict, book_data: Dict,
                                  prev_file: Optional[str], next_file: Optional[str]) -> str:
        """
        Generate markdown content for a pericope.

        Args:
            pericope: Pericope data
            book_data: Book metadata
            prev_file: Previous pericope filename (for navigation)
            next_file: Next pericope filename (for navigation)

        Returns:
            Complete markdown content with YAML frontmatter
        """
        # Generate YAML frontmatter
        frontmatter = "---\n"
        frontmatter += f"testament: {book_data['testament']}\n"
        frontmatter += f"book: {book_data['name_en']}\n"
        frontmatter += f"book_romanian: {book_data['name_ro']}\n"
        frontmatter += f"chapter: {pericope['chapter']}\n"
        frontmatter += f"pericope: {int(pericope['pericope_num'])}\n"
        frontmatter += f'pericope_title_en: "{pericope["title_en"]}"\n'
        frontmatter += f'pericope_title_ro: "{pericope["title_ro"]}"\n'
        frontmatter += f"verses_start: {pericope['start_verse']}\n"
        frontmatter += f"verses_end: {pericope['end_verse']}\n"
        frontmatter += f"verses_total: {pericope['verse_count']}\n"
        frontmatter += f"language: ro\n"
        frontmatter += "---\n"

        # Generate title
        content = f"# {pericope['title_en']}\n\n"

        # Generate navigation (top)
        nav = ""
        if prev_file:
            nav += f"← [[{prev_file}]]"
        if prev_file and next_file:
            nav += " | "
        if next_file:
            nav += f"[[{next_file}]] →"

        if nav:
            content += nav + "\n\n"

        # Generate verses
        for verse in pericope['verses']:
            content += f"{verse['verse']}. {verse['text']}\n"

        # Generate navigation (bottom)
        if nav:
            content += f"\n{nav}\n"

        return frontmatter + content

    def generate_all_books(self):
        """Generate markdown files for all books."""

        print(f"\n{'='*60}")
        print("GENERATING PERICOPE MARKDOWN FILES")
        print(f"{'='*60}\n")

        # Create output directories
        ot_dir = self.output_dir / "Old Testament"
        nt_dir = self.output_dir / "New Testament"
        ot_dir.mkdir(parents=True, exist_ok=True)
        nt_dir.mkdir(parents=True, exist_ok=True)

        # Load all books and flatten pericopes for navigation
        all_books_data = []
        all_pericopes_flat = []

        for json_file in sorted(self.pericopes_dir.glob('*.json')):
            book_data = json.load(open(json_file, 'r', encoding='utf-8'))
            all_books_data.append(book_data)

            # Flatten pericopes with book info
            for pericope in book_data['pericopes']:
                all_pericopes_flat.append({
                    **pericope,
                    'book_num': book_data['book_number'],
                    'book_name_en': book_data['name_en'],
                    'book_name_ro': book_data['name_ro'],
                    'testament': book_data['testament']
                })

        # Sort by book number and pericope order
        all_pericopes_flat.sort(key=lambda x: (x['book_num'], x['chapter'], x['pericope_num']))

        print(f"Total books: {len(all_books_data)}")
        print(f"Total pericopes: {len(all_pericopes_flat)}\n")

        # Generate markdown for each book
        total_files = 0

        for book_data in all_books_data:
            book_num = book_data['book_number']
            book_name_ro = book_data['name_ro']
            book_name_en = book_data['name_en']
            testament = book_data['testament']

            # Determine output directory
            if testament == 'OT':
                book_dir = ot_dir / f"{book_num:02d} {book_name_ro}"
            else:
                book_dir = nt_dir / f"{book_num:02d} {book_name_ro}"

            book_dir.mkdir(parents=True, exist_ok=True)

            print(f"[{book_num:02d}] {book_name_en} - {len(book_data['pericopes'])} pericopes")

            # Generate markdown for each pericope
            for pericope in book_data['pericopes']:
                # Find this pericope in the flat list to get prev/next
                pericope_id = pericope['pericope_id']
                current_index = next(
                    i for i, p in enumerate(all_pericopes_flat)
                    if p['pericope_id'] == pericope_id
                )

                prev_file, next_file = self.get_prev_next_pericopes(
                    all_pericopes_flat, current_index, all_books_data
                )

                # Generate markdown content
                markdown = self.generate_markdown_content(
                    pericope, book_data, prev_file, next_file
                )

                # Generate filename
                filename = self.get_pericope_filename(
                    book_num,
                    book_name_ro,
                    pericope['chapter'],
                    pericope['pericope_num'],
                    pericope['title_ro']
                )

                # Write file
                output_file = book_dir / filename
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(markdown)

                total_files += 1

        print(f"\n{'='*60}")
        print("GENERATION SUMMARY")
        print(f"{'='*60}")
        print(f"Total files generated: {total_files}")
        print(f"Output directory: {self.output_dir.resolve()}")
        print(f"{'='*60}\n")


def main():
    """Main entry point."""
    generator = MarkdownGenerator(
        pericopes_dir='bible_books_pericopes',
        output_dir='Biblia_Generata',
        metadata_path='bible_books_metadata.json'
    )

    generator.generate_all_books()


if __name__ == '__main__':
    main()
