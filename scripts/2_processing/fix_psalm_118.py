#!/usr/bin/env python3
"""
Fix Psalm 118 pericope data.

The pericope file incorrectly has only verses 1-29, but Psalm 118
(119 in Protestant numbering) has 176 verses - the famous alphabetic
acrostic psalm with 22 sections of 8 verses each.

This script:
1. Reads the original bible_books/19_Psalmi.json
2. Extracts all 176 verses for chapter 118
3. Updates the pericope in bible_books_pericopes/19_Psalmi_pericopes.json
"""

import json
from pathlib import Path


def fix_psalm_118():
    """Fix Psalm 118 pericope data to include all 176 verses."""

    print("="*60)
    print("FIXING PSALM 118 PERICOPE DATA")
    print("="*60)

    # Load original Bible data
    print("\n1. Loading original Psalms data...")
    bible_path = Path("bible_books/19_Psalmi.json")
    with open(bible_path, 'r', encoding='utf-8') as f:
        bible_data = json.load(f)

    # Find chapter 118
    chapter_118 = None
    for chapter in bible_data['chapters']:
        if chapter['chapter'] == 118:
            chapter_118 = chapter
            break

    if not chapter_118:
        raise ValueError("Chapter 118 not found in Psalms data")

    print(f"   Found chapter 118 with {len(chapter_118['verses'])} verses")

    # Load pericope data
    print("\n2. Loading pericope data...")
    pericope_path = Path("bible_books_pericopes/19_Psalmi_pericopes.json")
    with open(pericope_path, 'r', encoding='utf-8') as f:
        pericope_data = json.load(f)

    # Find Psalm 118 pericope
    psalm_118_pericope = None
    psalm_118_index = None
    for idx, pericope in enumerate(pericope_data['pericopes']):
        if pericope['chapter'] == 118:
            psalm_118_pericope = pericope
            psalm_118_index = idx
            break

    if not psalm_118_pericope:
        raise ValueError("Psalm 118 pericope not found")

    print(f"   Found pericope with {psalm_118_pericope['verse_count']} verses (should be 176)")

    # Extract all verses from chapter 118
    print("\n3. Extracting all 176 verses from chapter 118...")
    all_verses = []
    for verse in chapter_118['verses']:
        all_verses.append({
            'verse': verse['verse'],
            'text': verse['text']
        })

    print(f"   Extracted {len(all_verses)} verses")

    # Update pericope with all verses
    print("\n4. Updating pericope data...")
    pericope_data['pericopes'][psalm_118_index]['end_verse'] = 176
    pericope_data['pericopes'][psalm_118_index]['verse_count'] = len(all_verses)
    pericope_data['pericopes'][psalm_118_index]['verses'] = all_verses

    # Also update the title to be more descriptive
    if pericope_data['pericopes'][psalm_118_index].get('title_ro'):
        # Keep existing Romanian title
        print(f"   Keeping existing Romanian title")

    # Save updated pericope data
    print("\n5. Saving updated pericope data...")
    with open(pericope_path, 'w', encoding='utf-8') as f:
        json.dump(pericope_data, f, ensure_ascii=False, indent=2)

    print(f"   Saved to {pericope_path}")

    print("\n" + "="*60)
    print("PSALM 118 FIX COMPLETE")
    print("="*60)
    print(f"\nPsalm 118 now has:")
    print(f"  - Start verse: {pericope_data['pericopes'][psalm_118_index]['start_verse']}")
    print(f"  - End verse: {pericope_data['pericopes'][psalm_118_index]['end_verse']}")
    print(f"  - Total verses: {pericope_data['pericopes'][psalm_118_index]['verse_count']}")
    print(f"\nNext step: Run 4_generate_markdown.py to regenerate the markdown file")
    print("="*60 + "\n")


if __name__ == '__main__':
    fix_psalm_118()
