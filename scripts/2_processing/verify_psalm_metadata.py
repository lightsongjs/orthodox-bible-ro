#!/usr/bin/env python3
"""
Verify that all Psalm metadata (frontmatter) matches actual verse counts.
"""

import json
from pathlib import Path


def verify_psalm_metadata():
    """Check that metadata in pericope JSON matches actual Bible verses."""

    print("="*80)
    print("VERIFICARE METADATA PSALMI")
    print("="*80)

    # Load pericope data
    with open('bible_books_pericopes/19_Psalmi_pericopes.json', 'r', encoding='utf-8') as f:
        pericope_data = json.load(f)

    # Load main Bible data
    with open('bible_books/19_Psalmi.json', 'r', encoding='utf-8') as f:
        bible_data = json.load(f)

    # Create lookup
    bible_chapters = {ch['chapter']: ch for ch in bible_data['chapters']}

    print(f"\nTotal psalmi in pericope: {len(pericope_data['pericopes'])}")
    print(f"Total psalmi in Biblie: {len(bible_data['chapters'])}")

    # Check all psalms
    print("\nVerificare metadata:")
    print("-"*80)
    print(f"{'Psalm':<8} {'Start':<8} {'End':<8} {'Total':<8} {'Actual':<8} {'Status':<10}")
    print("-"*80)

    errors = []

    for pericope in pericope_data['pericopes']:
        psalm_num = pericope['chapter']

        # Get actual verse count from Bible
        bible_ch = bible_chapters[psalm_num]
        actual_verses = len(bible_ch['verses'])

        # Get metadata from pericope
        meta_start = pericope['start_verse']
        meta_end = pericope['end_verse']
        meta_total = pericope['verse_count']
        pericope_verses = len(pericope['verses'])

        # Check if all match
        is_correct = (
            meta_start == 1 and
            meta_end == actual_verses and
            meta_total == actual_verses and
            pericope_verses == actual_verses
        )

        status = "OK" if is_correct else "ERROR"

        # Only print first 20 and last 5, plus any errors
        if psalm_num <= 20 or psalm_num >= 147 or not is_correct:
            print(f"{psalm_num:<8} {meta_start:<8} {meta_end:<8} {meta_total:<8} "
                  f"{actual_verses:<8} {status:<10}")

        if not is_correct:
            errors.append({
                'psalm': psalm_num,
                'meta_start': meta_start,
                'meta_end': meta_end,
                'meta_total': meta_total,
                'actual': actual_verses
            })

    print("-"*80)

    if errors:
        print(f"\nERRORI GASITE: {len(errors)} psalmi")
        print("\nDetalii erori:")
        for err in errors:
            print(f"  Psalm {err['psalm']}: metadata end={err['meta_end']}, "
                  f"total={err['meta_total']}, actual={err['actual']}")
    else:
        print("\nTOATE CORECTE! Toti cei 151 psalmi au metadata corecta.")
        print("verses_start=1, verses_end=actual, verses_total=actual")

    print("\n" + "="*80 + "\n")

    return len(errors) == 0


if __name__ == '__main__':
    verify_psalm_metadata()
