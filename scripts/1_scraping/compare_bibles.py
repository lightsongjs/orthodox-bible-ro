"""
Compare English and Romanian Bible pericope counts
Generate detailed report of differences
"""
import os
import json

def count_pericopes_in_directory(directory):
    """Count pericope files for each book"""
    book_counts = {}

    if not os.path.exists(directory):
        return book_counts

    for book_dir in os.listdir(directory):
        book_path = os.path.join(directory, book_dir)
        if os.path.isdir(book_path):
            # Count .md files
            files = [f for f in os.listdir(book_path) if f.endswith('.md')]
            book_counts[book_dir] = len(files)

    return book_counts

def generate_comparison_report():
    """Generate detailed comparison report"""

    print("="*80)
    print("BIBLE COMPARISON REPORT - ENGLISH vs ROMANIAN")
    print("="*80)
    print()

    # Count English pericopes
    print("Counting English Bible pericopes...")
    english_nt = count_pericopes_in_directory("New Testament")
    english_ot = count_pericopes_in_directory("Old Testament")

    # Count Romanian pericopes
    print("Counting Romanian Bible pericopes...")
    romanian_nt = count_pericopes_in_directory("Romanian Bible/New Testament")
    romanian_ot = count_pericopes_in_directory("Romanian Bible/Old Testament")

    print()
    print("="*80)
    print("NEW TESTAMENT COMPARISON")
    print("="*80)
    print()
    print(f"{'Book':<25} {'English':<12} {'Romanian':<12} {'Difference':<12} {'Status'}")
    print("-"*80)

    nt_total_diff = 0
    nt_missing_books = []
    nt_partial_books = []

    for book in sorted(english_nt.keys()):
        eng_count = english_nt[book]
        rom_count = romanian_nt.get(book, 0)
        diff = eng_count - rom_count
        nt_total_diff += abs(diff)

        if rom_count == 0:
            status = "MISSING"
            nt_missing_books.append(book)
        elif diff != 0:
            status = f"PARTIAL ({diff:+d})"
            nt_partial_books.append((book, diff))
        else:
            status = "OK"

        print(f"{book:<25} {eng_count:<12} {rom_count:<12} {diff:>+11} {status}")

    print()
    print(f"NT Total English: {sum(english_nt.values())}")
    print(f"NT Total Romanian: {sum(romanian_nt.values())}")
    print(f"NT Total Difference: {nt_total_diff}")

    print()
    print("="*80)
    print("OLD TESTAMENT COMPARISON")
    print("="*80)
    print()
    print(f"{'Book':<25} {'English':<12} {'Romanian':<12} {'Difference':<12} {'Status'}")
    print("-"*80)

    ot_total_diff = 0
    ot_missing_books = []
    ot_partial_books = []

    for book in sorted(english_ot.keys()):
        eng_count = english_ot[book]
        rom_count = romanian_ot.get(book, 0)
        diff = eng_count - rom_count
        ot_total_diff += abs(diff)

        if rom_count == 0:
            status = "MISSING"
            ot_missing_books.append(book)
        elif diff != 0:
            status = f"PARTIAL ({diff:+d})"
            ot_partial_books.append((book, diff))
        else:
            status = "OK"

        print(f"{book:<25} {eng_count:<12} {rom_count:<12} {diff:>+11} {status}")

    print()
    print(f"OT Total English: {sum(english_ot.values())}")
    print(f"OT Total Romanian: {sum(romanian_ot.values())}")
    print(f"OT Total Difference: {ot_total_diff}")

    # Summary
    print()
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print()

    total_eng = sum(english_nt.values()) + sum(english_ot.values())
    total_rom = sum(romanian_nt.values()) + sum(romanian_ot.values())

    print(f"Total English Pericopes: {total_eng}")
    print(f"Total Romanian Pericopes: {total_rom}")
    print(f"Total Difference: {total_eng - total_rom}")
    print(f"Completion Rate: {(total_rom/total_eng*100):.1f}%")

    # Missing books
    if nt_missing_books or ot_missing_books:
        print()
        print("="*80)
        print("COMPLETELY MISSING BOOKS")
        print("="*80)

        if nt_missing_books:
            print()
            print("New Testament Missing Books:")
            for book in nt_missing_books:
                print(f"  - {book}: {english_nt[book]} pericopes missing")

        if ot_missing_books:
            print()
            print("Old Testament Missing Books:")
            for book in ot_missing_books:
                print(f"  - {book}: {english_ot[book]} pericopes missing")

    # Partial books
    if nt_partial_books or ot_partial_books:
        print()
        print("="*80)
        print("PARTIALLY EXTRACTED BOOKS")
        print("="*80)

        if nt_partial_books:
            print()
            print("New Testament Partial Books:")
            for book, diff in sorted(nt_partial_books, key=lambda x: abs(x[1]), reverse=True):
                eng = english_nt[book]
                rom = romanian_nt.get(book, 0)
                print(f"  - {book}: {rom}/{eng} pericopes ({diff:+d})")

        if ot_partial_books:
            print()
            print("Old Testament Partial Books:")
            for book, diff in sorted(ot_partial_books, key=lambda x: abs(x[1]), reverse=True):
                eng = english_ot[book]
                rom = romanian_ot.get(book, 0)
                print(f"  - {book}: {rom}/{eng} pericopes ({diff:+d})")

    # Save detailed report to file
    report = {
        "english": {
            "new_testament": english_nt,
            "old_testament": english_ot,
            "total": total_eng
        },
        "romanian": {
            "new_testament": romanian_nt,
            "old_testament": romanian_ot,
            "total": total_rom
        },
        "missing_books": {
            "new_testament": nt_missing_books,
            "old_testament": ot_missing_books
        },
        "partial_books": {
            "new_testament": nt_partial_books,
            "old_testament": ot_partial_books
        }
    }

    with open("bible_comparison_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print()
    print("Detailed report saved to: bible_comparison_report.json")

if __name__ == "__main__":
    generate_comparison_report()
