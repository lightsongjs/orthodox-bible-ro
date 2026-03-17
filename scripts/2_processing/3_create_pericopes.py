#!/usr/bin/env python3
"""
Convert Romanian Orthodox Bible from chapter/verse format to pericope-based format.

This script:
1. Reads pericope structure from the OneDrive folder
2. Reads Romanian Bible data from bible_books/
3. Maps book names between English and Romanian
4. Splits verses according to pericope boundaries
5. Outputs pericope-based JSON files to bible_books_pericopes/

Author: Generated for Romanian Orthodox Bible Project
Date: 2026-01-02
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any


class PericopeConverter:
    """Convert Bible books from chapter/verse to pericope format."""

    def __init__(self, pericope_structure_path: str, bible_books_path: str, metadata_path: str):
        """
        Initialize converter with paths to data sources.

        Args:
            pericope_structure_path: Path to pericope_structure.json
            bible_books_path: Path to bible_books/ directory
            metadata_path: Path to bible_books_metadata.json
        """
        self.pericope_structure_path = Path(pericope_structure_path)
        self.bible_books_path = Path(bible_books_path)
        self.metadata_path = Path(metadata_path)

        self.pericope_structure = None
        self.metadata = None
        self.book_name_mapping = {}

    def load_data(self):
        """Load pericope structure and metadata."""
        print("Loading pericope structure...")
        with open(self.pericope_structure_path, 'r', encoding='utf-8') as f:
            self.pericope_structure = json.load(f)

        print("Loading metadata...")
        with open(self.metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)

        print("Building book name mapping...")
        self._build_book_name_mapping()

    def _build_book_name_mapping(self):
        """
        Build mapping between English pericope names and Romanian book names.

        Handles variations like:
        - "Matthew" -> "Matei"
        - "1_Corinthians" -> "I Corinteni"
        - "1 Corinthians" -> "I Corinteni"
        """
        all_books = self.metadata['old_testament'] + self.metadata['new_testament']

        for book in all_books:
            en_name = book['name_en']
            ro_name = book['name_ro']

            # Store multiple variations of English name
            self.book_name_mapping[en_name] = ro_name
            self.book_name_mapping[en_name.replace(' ', '_')] = ro_name
            self.book_name_mapping[en_name.replace(' ', '')] = ro_name

            # Handle special cases
            # "1 Kings" might be "1_Kings" or "1Kings" in pericope structure
            if en_name.startswith(('1 ', '2 ', '3 ', '4 ')):
                number = en_name[0]
                rest = en_name[2:]
                self.book_name_mapping[f"{number}_{rest}"] = ro_name
                self.book_name_mapping[f"{number}{rest}"] = ro_name

        # Special mappings for Protestant vs Orthodox naming differences
        # Orthodox: 1-2 Kings = Protestant: 1-2 Samuel
        # Orthodox: 3-4 Kings = Protestant: 1-2 Kings
        self.book_name_mapping['1_Samuel'] = 'I Regi'
        self.book_name_mapping['2_Samuel'] = 'II Regi'

        # Ezra variations
        self.book_name_mapping['Ezra'] = 'I Ezdra'
        self.book_name_mapping['1_Ezra'] = 'I Ezdra'

        # Song of Songs / Song of Solomon variations
        self.book_name_mapping['Song_of_Solomon'] = 'Cântări'
        self.book_name_mapping['SongofSolomon'] = 'Cântări'

        # Wisdom of Solomon
        self.book_name_mapping['Wisdom'] = 'Solomon'
        self.book_name_mapping['Wisdom_of_Solomon'] = 'Solomon'

    def find_romanian_book(self, english_book_name: str) -> Dict[str, Any]:
        """
        Find Romanian book data by English name.

        Args:
            english_book_name: English book name from pericope structure

        Returns:
            Dictionary with Romanian book data

        Raises:
            FileNotFoundError: If book file doesn't exist
        """
        # Get Romanian name
        ro_name = self.book_name_mapping.get(english_book_name)
        if not ro_name:
            raise ValueError(f"Cannot find Romanian name for '{english_book_name}'")

        # Find matching file in bible_books/
        # Files are named like: 52_Matei.json, 53_Marcu.json, etc.
        # Romanian name may have spaces that are replaced with underscores in filename
        ro_name_underscore = ro_name.replace(' ', '_')

        matching_files = list(self.bible_books_path.glob(f"*_{ro_name_underscore}.json"))

        # Also try without replacing spaces
        if not matching_files:
            matching_files = list(self.bible_books_path.glob(f"*_{ro_name}.json"))

        if not matching_files:
            raise FileNotFoundError(f"Cannot find file for '{ro_name}' (tried '{ro_name_underscore}') in {self.bible_books_path}")

        if len(matching_files) > 1:
            print(f"Warning: Multiple files found for '{ro_name}': {matching_files}")

        # Load the book data
        with open(matching_files[0], 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_verses_from_chapter(self, chapter_data: Dict, start_verse: int, end_verse: int) -> List[Dict]:
        """
        Extract verses from a chapter.

        Args:
            chapter_data: Chapter data with verses array
            start_verse: First verse number to extract
            end_verse: Last verse number to extract

        Returns:
            List of verse dictionaries
        """
        verses = []
        for verse in chapter_data['verses']:
            verse_num = verse['verse']
            if start_verse <= verse_num <= end_verse:
                verses.append({
                    'verse': verse_num,
                    'text': verse['text']
                })
        return verses

    def convert_book(self, english_book_name: str) -> Dict[str, Any]:
        """
        Convert a single book to pericope format.

        Args:
            english_book_name: English book name from pericope structure

        Returns:
            Dictionary with pericope-based book data
        """
        print(f"\nConverting '{english_book_name}'...")

        # Get pericope structure for this book
        if english_book_name not in self.pericope_structure:
            raise ValueError(f"No pericope structure found for '{english_book_name}'")

        book_pericopes = self.pericope_structure[english_book_name]

        # Load Romanian book data
        romanian_book = self.find_romanian_book(english_book_name)

        # Build pericope array
        pericopes = []
        total_pericopes = 0

        for chapter_num_str, chapter_pericopes in book_pericopes.items():
            chapter_num = int(chapter_num_str)

            # Find corresponding chapter in Romanian book
            chapter_data = None
            for ch in romanian_book['chapters']:
                if ch['chapter'] == chapter_num:
                    chapter_data = ch
                    break

            if not chapter_data:
                print(f"  Warning: Chapter {chapter_num} not found in Romanian data, skipping...")
                continue

            # Process each pericope in this chapter
            for idx, pericope in enumerate(chapter_pericopes):
                pericope_num = pericope['pericope_num']
                title = pericope['title']
                start_verse = pericope['start_verse']
                end_verse = pericope['end_verse']

                # FIX: If this is the first pericope in the chapter and starts after verse 1,
                # automatically include verse 1 (common issue with pericope structures)
                if idx == 0 and start_verse > 1:
                    start_verse = 1

                # Extract verses
                verses = self.get_verses_from_chapter(chapter_data, start_verse, end_verse)

                if not verses:
                    print(f"  Warning: No verses found for {english_book_name} {chapter_num}:{start_verse}-{end_verse}")
                    continue

                # Create pericope entry
                pericope_id = f"{english_book_name}_{chapter_num:02d}_{pericope_num}"
                pericope_entry = {
                    'pericope_id': pericope_id,
                    'chapter': chapter_num,
                    'pericope_num': pericope_num,
                    'title': title,
                    'start_verse': start_verse,
                    'end_verse': end_verse,
                    'verse_count': len(verses),
                    'verses': verses
                }

                pericopes.append(pericope_entry)
                total_pericopes += 1

        # Determine testament
        all_books = self.metadata['old_testament'] + self.metadata['new_testament']
        testament = 'OT'
        for book in all_books:
            if book['name_en'] == english_book_name or book['name_ro'] == self.book_name_mapping.get(english_book_name):
                if book in self.metadata['new_testament']:
                    testament = 'NT'
                break

        # Build final book structure
        result = {
            'id': romanian_book['id'],
            'book_number': romanian_book['book_number'],
            'name_en': romanian_book['name_en'],
            'name_ro': romanian_book['name_ro'],
            'testament': testament,
            'chapter_count': romanian_book['chapter_count'],
            'pericope_count': total_pericopes,
            'url': romanian_book['url'],
            'pericopes': pericopes
        }

        print(f"  [OK] Converted {total_pericopes} pericopes across {romanian_book['chapter_count']} chapters")

        return result

    def convert_all_books(self, output_dir: str = 'bible_books_pericopes'):
        """
        Convert all books in pericope structure to pericope format.

        Args:
            output_dir: Directory to write output JSON files
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        print(f"\n{'='*60}")
        print(f"CONVERTING ALL BOOKS TO PERICOPE FORMAT")
        print(f"{'='*60}")

        total_books = len(self.pericope_structure)
        successful = 0
        failed = []

        for idx, english_book_name in enumerate(self.pericope_structure.keys(), 1):
            try:
                print(f"\n[{idx}/{total_books}] Processing '{english_book_name}'...")

                result = self.convert_book(english_book_name)

                # Determine output filename using Romanian name
                ro_name = result['name_ro']
                book_num = result['book_number']
                output_file = output_path / f"{book_num:02d}_{ro_name}_pericopes.json"

                # Write to file
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

                print(f"  [SAVED] {output_file}")
                successful += 1

            except Exception as e:
                print(f"  [ERROR] {e}")
                failed.append((english_book_name, str(e)))

        # Print summary
        print(f"\n{'='*60}")
        print(f"CONVERSION SUMMARY")
        print(f"{'='*60}")
        print(f"Total books processed: {total_books}")
        print(f"Successful: {successful}")
        print(f"Failed: {len(failed)}")

        if failed:
            print(f"\nFailed books:")
            for book_name, error in failed:
                print(f"  - {book_name}: {error}")

        print(f"\nOutput directory: {output_path.resolve()}")
        print(f"{'='*60}\n")


def main():
    """Main entry point."""
    # Configure paths
    pericope_structure = "OneDrive_2026-01-02/2025-11-14 - obisidianBibleStudy/pericope_structure.json"
    bible_books = "bible_books"
    metadata = "bible_books_metadata.json"
    output_dir = "bible_books_pericopes"

    # Create converter
    converter = PericopeConverter(pericope_structure, bible_books, metadata)

    # Load data
    converter.load_data()

    # Convert all books
    converter.convert_all_books(output_dir)


if __name__ == '__main__':
    main()
