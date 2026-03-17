#!/usr/bin/env python3
"""
Check all Psalms for verse count mismatches between pericope and main JSON.

The pericope structure is based on Catholic/Protestant Bible numbering,
but the Orthodox Bible uses Septuagint (LXX) numbering, which differs
for Psalms 9-147.
"""

import json
from pathlib import Path


def check_all_psalms():
    """Check all psalms for verse count issues."""

    print("="*80)
    print("CHECKING ALL PSALMS FOR VERSE COUNT MISMATCHES")
    print("="*80)

    # Load main Bible data
    print("\nLoading main Psalms data...")
    with open('bible_books/19_Psalmi.json', 'r', encoding='utf-8') as f:
        bible_data = json.load(f)

    # Load pericope data
    print("Loading pericope data...")
    with open('bible_books_pericopes/19_Psalmi_pericopes.json', 'r', encoding='utf-8') as f:
        pericope_data = json.load(f)

    # Create lookup for main Bible chapters
    main_chapters = {}
    for chapter in bible_data['chapters']:
        main_chapters[chapter['chapter']] = len(chapter['verses'])

    # Create lookup for pericope chapters
    pericope_chapters = {}
    for pericope in pericope_data['pericopes']:
        chapter_num = pericope['chapter']
        if chapter_num not in pericope_chapters:
            pericope_chapters[chapter_num] = {
                'max_verse': 0,
                'pericopes': []
            }
        pericope_chapters[chapter_num]['max_verse'] = max(
            pericope_chapters[chapter_num]['max_verse'],
            pericope['end_verse']
        )
        pericope_chapters[chapter_num]['pericopes'].append(pericope)

    print(f"\nTotal chapters in main JSON: {len(main_chapters)}")
    print(f"Total chapters with pericopes: {len(pericope_chapters)}")

    # Compare
    print("\n" + "="*80)
    print("CHECKING FOR MISMATCHES")
    print("="*80)

    issues = []

    for chapter_num in sorted(main_chapters.keys()):
        main_verse_count = main_chapters[chapter_num]

        if chapter_num in pericope_chapters:
            pericope_max_verse = pericope_chapters[chapter_num]['max_verse']

            if main_verse_count != pericope_max_verse:
                issues.append({
                    'psalm': chapter_num,
                    'main_verses': main_verse_count,
                    'pericope_verses': pericope_max_verse,
                    'difference': main_verse_count - pericope_max_verse
                })
        else:
            issues.append({
                'psalm': chapter_num,
                'main_verses': main_verse_count,
                'pericope_verses': 0,
                'difference': main_verse_count
            })

    # Report issues
    if issues:
        print(f"\nFound {len(issues)} Psalms with verse count mismatches:\n")
        print(f"{'Psalm':<8} {'Main JSON':<12} {'Pericope':<12} {'Missing':<10} {'Status':<10}")
        print("-"*80)

        for issue in issues:
            status = "MISSING" if issue['difference'] > 0 else "OK"
            print(f"{issue['psalm']:<8} {issue['main_verses']:<12} "
                  f"{issue['pericope_verses']:<12} {issue['difference']:<10} {status}")

        # Summary
        total_missing = sum(i['difference'] for i in issues if i['difference'] > 0)
        print("\n" + "="*80)
        print(f"Total Psalms with issues: {len(issues)}")
        print(f"Total verses missing from pericopes: {total_missing}")
        print("="*80)

        # Note about numbering
        print("\nNOTE:")
        print("The pericope structure uses Catholic/Protestant numbering.")
        print("The Orthodox Bible uses Septuagint (LXX) numbering.")
        print("Psalm numbers differ between these systems for Psalms 9-147.")
        print("\nThis mismatch is why verse counts don't align properly.")

    else:
        print("\nAll Psalms have matching verse counts!")

    print("\n" + "="*80 + "\n")


if __name__ == '__main__':
    check_all_psalms()
