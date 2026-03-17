"""
Thorough validation report comparing English and Romanian Bible pericopes.
Uses the romanian_book_ids.json mapping to correctly match book names.
"""
import os
import json
from pathlib import Path

def load_book_mapping():
    """Load the English to Romanian book name mapping"""
    with open('romanian_book_ids.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def count_pericopes(directory, book_name):
    """Count pericope .md files in a book directory"""
    book_path = Path(directory) / book_name
    if not book_path.exists():
        return 0

    md_files = list(book_path.glob('*.md'))
    return len(md_files)

def get_testament(book_english):
    """Determine testament based on book"""
    ot_books = {
        'Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy',
        'Joshua', 'Judges', 'Ruth', '1 Samuel', '2 Samuel',
        '1 Kings', '2 Kings', '1 Chronicles', '2 Chronicles',
        'Ezra', 'Nehemiah', 'Tobit', 'Judith', 'Esther',
        '1 Maccabees', '2 Maccabees', 'Job', 'Psalms', 'Proverbs',
        'Ecclesiastes', 'Song of Solomon', 'Wisdom', 'Sirach',
        'Isaiah', 'Jeremiah', 'Lamentations', 'Baruch', 'Ezekiel',
        'Daniel', 'Hosea', 'Joel', 'Amos', 'Obadiah', 'Jonah',
        'Micah', 'Nahum', 'Habakkuk', 'Zephaniah', 'Haggai',
        'Zechariah', 'Malachi'
    }
    return 'OT' if book_english in ot_books else 'NT'

def generate_completeness_report():
    """Generate comprehensive validation report"""

    print("="*80)
    print("BIBLE COMPLETENESS VALIDATION REPORT")
    print("Comparing English vs Romanian Pericopes")
    print("="*80)
    print()

    # Load mapping
    book_mapping = load_book_mapping()

    # Organize books by testament
    nt_books = []
    ot_books = []

    for english_name in book_mapping.keys():
        testament = get_testament(english_name)
        if testament == 'NT':
            nt_books.append(english_name)
        else:
            ot_books.append(english_name)

    # Sort books
    nt_books.sort()
    ot_books.sort()

    # Statistics
    nt_stats = {
        'total_english': 0,
        'total_romanian': 0,
        'missing_books': [],
        'partial_books': [],
        'complete_books': []
    }

    ot_stats = {
        'total_english': 0,
        'total_romanian': 0,
        'missing_books': [],
        'partial_books': [],
        'complete_books': []
    }

    # NEW TESTAMENT
    print("="*80)
    print("NEW TESTAMENT")
    print("="*80)
    print()
    print(f"{'Book (English)':<25} {'Romanian Name':<25} {'EN':<6} {'RO':<6} {'Diff':<8} {'Status'}")
    print("-"*80)

    for book_english in nt_books:
        book_romanian = book_mapping[book_english]['romanian_name']

        # Convert underscores for English directory names
        english_dir_name = book_english.replace(' ', '_')

        # Count pericopes
        english_count = count_pericopes('New Testament', english_dir_name)
        romanian_count = count_pericopes('Romanian Bible/New Testament', book_romanian)

        diff = english_count - romanian_count

        # Update stats
        nt_stats['total_english'] += english_count
        nt_stats['total_romanian'] += romanian_count

        # Determine status
        if romanian_count == 0:
            status = "MISSING"
            nt_stats['missing_books'].append((book_english, english_count))
        elif diff != 0:
            status = f"PARTIAL ({diff:+d})"
            nt_stats['partial_books'].append((book_english, romanian_count, english_count, diff))
        else:
            status = "✓ COMPLETE"
            nt_stats['complete_books'].append(book_english)

        print(f"{book_english:<25} {book_romanian:<25} {english_count:<6} {romanian_count:<6} {diff:>+7} {status}")

    print()
    print(f"NT Totals: English={nt_stats['total_english']}, Romanian={nt_stats['total_romanian']}, Diff={nt_stats['total_english']-nt_stats['total_romanian']:+d}")
    print(f"Completion: {len(nt_stats['complete_books'])}/{len(nt_books)} books complete ({len(nt_stats['complete_books'])/len(nt_books)*100:.1f}%)")

    # OLD TESTAMENT
    print()
    print("="*80)
    print("OLD TESTAMENT")
    print("="*80)
    print()
    print(f"{'Book (English)':<25} {'Romanian Name':<25} {'EN':<6} {'RO':<6} {'Diff':<8} {'Status'}")
    print("-"*80)

    for book_english in ot_books:
        book_romanian = book_mapping[book_english]['romanian_name']

        # Convert underscores for English directory names
        english_dir_name = book_english.replace(' ', '_')

        # Count pericopes
        english_count = count_pericopes('Old Testament', english_dir_name)
        romanian_count = count_pericopes('Romanian Bible/Old Testament', book_romanian)

        diff = english_count - romanian_count

        # Update stats
        ot_stats['total_english'] += english_count
        ot_stats['total_romanian'] += romanian_count

        # Determine status
        if romanian_count == 0:
            status = "MISSING"
            ot_stats['missing_books'].append((book_english, english_count))
        elif diff != 0:
            status = f"PARTIAL ({diff:+d})"
            ot_stats['partial_books'].append((book_english, romanian_count, english_count, diff))
        else:
            status = "✓ COMPLETE"
            ot_stats['complete_books'].append(book_english)

        print(f"{book_english:<25} {book_romanian:<25} {english_count:<6} {romanian_count:<6} {diff:>+7} {status}")

    print()
    print(f"OT Totals: English={ot_stats['total_english']}, Romanian={ot_stats['total_romanian']}, Diff={ot_stats['total_english']-ot_stats['total_romanian']:+d}")
    print(f"Completion: {len(ot_stats['complete_books'])}/{len(ot_books)} books complete ({len(ot_stats['complete_books'])/len(ot_books)*100:.1f}%)")

    # OVERALL SUMMARY
    total_english = nt_stats['total_english'] + ot_stats['total_english']
    total_romanian = nt_stats['total_romanian'] + ot_stats['total_romanian']
    total_books = len(nt_books) + len(ot_books)
    complete_books = len(nt_stats['complete_books']) + len(ot_stats['complete_books'])

    print()
    print("="*80)
    print("OVERALL SUMMARY")
    print("="*80)
    print()
    print(f"Total Books: {total_books}")
    print(f"  Complete: {complete_books} ({complete_books/total_books*100:.1f}%)")
    print(f"  Partial: {len(nt_stats['partial_books']) + len(ot_stats['partial_books'])}")
    print(f"  Missing: {len(nt_stats['missing_books']) + len(ot_stats['missing_books'])}")
    print()
    print(f"Total Pericopes:")
    print(f"  English: {total_english}")
    print(f"  Romanian: {total_romanian}")
    print(f"  Difference: {total_english - total_romanian:+d}")
    print(f"  Completion Rate: {total_romanian/total_english*100:.1f}%")

    # DETAILED MISSING/PARTIAL
    if nt_stats['missing_books'] or ot_stats['missing_books']:
        print()
        print("="*80)
        print("MISSING BOOKS (0 pericopes extracted)")
        print("="*80)

        if nt_stats['missing_books']:
            print()
            print("New Testament:")
            for book, count in nt_stats['missing_books']:
                print(f"  - {book}: 0/{count} pericopes")

        if ot_stats['missing_books']:
            print()
            print("Old Testament:")
            for book, count in ot_stats['missing_books']:
                print(f"  - {book}: 0/{count} pericopes")

    if nt_stats['partial_books'] or ot_stats['partial_books']:
        print()
        print("="*80)
        print("PARTIALLY EXTRACTED BOOKS")
        print("="*80)

        if nt_stats['partial_books']:
            print()
            print("New Testament:")
            for book, rom_count, eng_count, diff in sorted(nt_stats['partial_books'], key=lambda x: abs(x[3]), reverse=True):
                print(f"  - {book}: {rom_count}/{eng_count} pericopes ({diff:+d})")

        if ot_stats['partial_books']:
            print()
            print("Old Testament:")
            for book, rom_count, eng_count, diff in sorted(ot_stats['partial_books'], key=lambda x: abs(x[3]), reverse=True):
                print(f"  - {book}: {rom_count}/{eng_count} pericopes ({diff:+d})")

    # COMPLETE BOOKS
    if nt_stats['complete_books'] or ot_stats['complete_books']:
        print()
        print("="*80)
        print("✓ COMPLETE BOOKS (All pericopes extracted)")
        print("="*80)

        if nt_stats['complete_books']:
            print()
            print(f"New Testament ({len(nt_stats['complete_books'])} books):")
            for book in nt_stats['complete_books']:
                print(f"  ✓ {book}")

        if ot_stats['complete_books']:
            print()
            print(f"Old Testament ({len(ot_stats['complete_books'])} books):")
            for book in ot_stats['complete_books']:
                print(f"  ✓ {book}")

    # Save JSON report
    report = {
        'summary': {
            'total_books': total_books,
            'complete_books': complete_books,
            'partial_books': len(nt_stats['partial_books']) + len(ot_stats['partial_books']),
            'missing_books': len(nt_stats['missing_books']) + len(ot_stats['missing_books']),
            'total_english_pericopes': total_english,
            'total_romanian_pericopes': total_romanian,
            'completion_rate_percent': round(total_romanian/total_english*100, 2)
        },
        'new_testament': {
            'complete': nt_stats['complete_books'],
            'partial': nt_stats['partial_books'],
            'missing': nt_stats['missing_books'],
            'total_english': nt_stats['total_english'],
            'total_romanian': nt_stats['total_romanian']
        },
        'old_testament': {
            'complete': ot_stats['complete_books'],
            'partial': ot_stats['partial_books'],
            'missing': ot_stats['missing_books'],
            'total_english': ot_stats['total_english'],
            'total_romanian': ot_stats['total_romanian']
        }
    }

    with open('completeness_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print()
    print("="*80)
    print(f"Report saved to: completeness_report.json")
    print("="*80)

if __name__ == '__main__':
    import sys
    import io

    # Fix Windows encoding for Unicode characters
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    generate_completeness_report()
