#!/usr/bin/env python3
"""
Clean up old Psalm markdown files that have outdated titles.

After fixing the Psalm numbering, new files were created with titles like "Psalmul X".
This script removes the old files with previous Romanian titles.
"""

from pathlib import Path


def clean_old_psalm_files():
    """Remove old Psalm markdown files."""

    print("="*80)
    print("CLEANING OLD PSALM FILES")
    print("="*80)

    psalm_dir = Path("Biblia_Generata/Old Testament/19 Psalmi")

    if not psalm_dir.exists():
        print(f"\nError: Directory not found: {psalm_dir}")
        return

    # Find all markdown files
    all_files = list(psalm_dir.glob("*.md"))
    print(f"\nTotal files found: {len(all_files)}")

    # Identify files to keep (those with "Psalmul" in the title)
    files_to_keep = [f for f in all_files if "Psalmul" in f.name]
    print(f"Files to keep (with 'Psalmul'): {len(files_to_keep)}")

    # Identify files to delete
    files_to_delete = [f for f in all_files if "Psalmul" not in f.name]
    print(f"Files to delete (old titles): {len(files_to_delete)}")

    if not files_to_delete:
        print("\nNo old files to delete. All clean!")
        return

    # Show count
    print(f"\nProceeding to delete old files...")

    # Delete old files
    print(f"\nDeleting {len(files_to_delete)} old files...")
    deleted_count = 0

    for file_path in files_to_delete:
        try:
            file_path.unlink()
            deleted_count += 1
        except Exception as e:
            print(f"  Error deleting {file_path.name}: {e}")

    print(f"\nDeleted {deleted_count} files")

    # Verify
    remaining_files = list(psalm_dir.glob("*.md"))
    print(f"Remaining files: {len(remaining_files)}")

    print("\n" + "="*80)
    print("CLEANUP COMPLETE")
    print("="*80)
    print(f"\nAll Psalm files now have consistent 'Psalmul X' titles.")
    print("="*80 + "\n")


if __name__ == '__main__':
    clean_old_psalm_files()
