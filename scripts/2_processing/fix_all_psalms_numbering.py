#!/usr/bin/env python3
"""
Fix all Psalms by mapping between Catholic/Protestant and Orthodox/Septuagint numbering.

Numbering differences:
- Psalms 1-8: Same in both
- Psalms 9-10 (Hebrew/Catholic) = Psalm 9 (LXX/Orthodox)
- Psalm 11-113 (Hebrew) = Psalm 10-112 (LXX) [off by 1]
- Psalms 114-115 (Hebrew) = Psalm 113 (LXX) [combined]
- Psalm 116:1-9 (Hebrew) = Psalm 114 (LXX)
- Psalm 116:10-19 (Hebrew) = Psalm 115 (LXX)
- Psalms 117-146 (Hebrew) = Psalms 116-145 (LXX) [off by 1]
- Psalm 147:1-11 (Hebrew) = Psalm 146 (LXX)
- Psalm 147:12-20 (Hebrew) = Psalm 147 (LXX)
- Psalms 148-150: Same in both
- Psalm 151: Only in LXX/Orthodox
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple


# Mapping: Orthodox/LXX number -> (Catholic/Hebrew number, verse_mapping)
# verse_mapping can be:
# - None: use all verses from the Catholic psalm
# - (start, end): use only verses start-end from the Catholic psalm
ORTHODOX_TO_CATHOLIC_MAPPING = {
    # Psalms 1-8: Same
    1: (1, None),
    2: (2, None),
    3: (3, None),
    4: (4, None),
    5: (5, None),
    6: (6, None),
    7: (7, None),
    8: (8, None),

    # Psalm 9 (LXX) = Psalms 9+10 (Hebrew) combined
    9: [(9, None), (10, None)],  # Special case: combines two psalms

    # Psalms 10-112 (LXX) = Psalms 11-113 (Hebrew)
    10: (11, None),
    11: (12, None),
    12: (13, None),
    13: (14, None),
    14: (15, None),
    15: (16, None),
    16: (17, None),
    17: (18, None),
    18: (19, None),
    19: (20, None),
    20: (21, None),
    21: (22, None),
    22: (23, None),
    23: (24, None),
    24: (25, None),
    25: (26, None),
    26: (27, None),
    27: (28, None),
    28: (29, None),
    29: (30, None),
    30: (31, None),
    31: (32, None),
    32: (33, None),
    33: (34, None),
    34: (35, None),
    35: (36, None),
    36: (37, None),
    37: (38, None),
    38: (39, None),
    39: (40, None),
    40: (41, None),
    41: (42, None),
    42: (43, None),
    43: (44, None),
    44: (45, None),
    45: (46, None),
    46: (47, None),
    47: (48, None),
    48: (49, None),
    49: (50, None),
    50: (51, None),
    51: (52, None),
    52: (53, None),
    53: (54, None),
    54: (55, None),
    55: (56, None),
    56: (57, None),
    57: (58, None),
    58: (59, None),
    59: (60, None),
    60: (61, None),
    61: (62, None),
    62: (63, None),
    63: (64, None),
    64: (65, None),
    65: (66, None),
    66: (67, None),
    67: (68, None),
    68: (69, None),
    69: (70, None),
    70: (71, None),
    71: (72, None),
    72: (73, None),
    73: (74, None),
    74: (75, None),
    75: (76, None),
    76: (77, None),
    77: (78, None),
    78: (79, None),
    79: (80, None),
    80: (81, None),
    81: (82, None),
    82: (83, None),
    83: (84, None),
    84: (85, None),
    85: (86, None),
    86: (87, None),
    87: (88, None),
    88: (89, None),
    89: (90, None),
    90: (91, None),
    91: (92, None),
    92: (93, None),
    93: (94, None),
    94: (95, None),
    95: (96, None),
    96: (97, None),
    97: (98, None),
    98: (99, None),
    99: (100, None),
    100: (101, None),
    101: (102, None),
    102: (103, None),
    103: (104, None),
    104: (105, None),
    105: (106, None),
    106: (107, None),
    107: (108, None),
    108: (109, None),
    109: (110, None),
    110: (111, None),
    111: (112, None),
    112: (113, None),

    # Psalm 113 (LXX) = Psalms 114+115 (Hebrew) combined
    113: [(114, None), (115, None)],  # Special case: combines two psalms

    # Psalm 114 (LXX) = Psalm 116:1-9 (Hebrew)
    114: (116, (1, 9)),

    # Psalm 115 (LXX) = Psalm 116:10-19 (Hebrew)
    115: (116, (10, 19)),

    # Psalms 116-145 (LXX) = Psalms 117-146 (Hebrew)
    116: (117, None),
    117: (118, None),
    118: (119, None),  # The long psalm!
    119: (120, None),
    120: (121, None),
    121: (122, None),
    122: (123, None),
    123: (124, None),
    124: (125, None),
    125: (126, None),
    126: (127, None),
    127: (128, None),
    128: (129, None),
    129: (130, None),
    130: (131, None),
    131: (132, None),
    132: (133, None),
    133: (134, None),
    134: (135, None),
    135: (136, None),
    136: (137, None),
    137: (138, None),
    138: (139, None),
    139: (140, None),
    140: (141, None),
    141: (142, None),
    142: (143, None),
    143: (144, None),
    144: (145, None),
    145: (146, None),

    # Psalm 146 (LXX) = Psalm 147:1-11 (Hebrew)
    146: (147, (1, 11)),

    # Psalm 147 (LXX) = Psalm 147:12-20 (Hebrew)
    147: (147, (12, 20)),

    # Psalms 148-150: Same
    148: (148, None),
    149: (149, None),
    150: (150, None),

    # Psalm 151: Only in LXX (no Catholic equivalent in pericope structure)
    151: None,
}


def load_pericope_structure(pericope_file: str) -> Dict:
    """Load the original pericope structure (Catholic numbering)."""
    # Check if we still have the source file
    pericope_path = Path(pericope_file)
    if not pericope_path.exists():
        raise FileNotFoundError(
            f"Pericope structure file not found: {pericope_file}\n"
            "This script needs the original pericope_structure.json file "
            "with Catholic/Protestant psalm numbering."
        )

    with open(pericope_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def fix_all_psalms():
    """Fix all Psalms in the pericope data by remapping from Catholic to Orthodox numbering."""

    print("="*80)
    print("FIXING ALL PSALMS - REMAPPING CATHOLIC TO ORTHODOX NUMBERING")
    print("="*80)

    # Load Orthodox Bible data (correct verse counts)
    print("\n1. Loading Orthodox Psalms data (correct verses)...")
    with open('bible_books/19_Psalmi.json', 'r', encoding='utf-8') as f:
        orthodox_data = json.load(f)

    # Create lookup by chapter number
    orthodox_chapters = {}
    for chapter in orthodox_data['chapters']:
        orthodox_chapters[chapter['chapter']] = chapter

    print(f"   Loaded {len(orthodox_chapters)} Orthodox psalms")

    # Load current pericope data (has Catholic numbering, incorrect)
    print("\n2. Loading current pericope data (incorrect numbering)...")
    with open('bible_books_pericopes/19_Psalmi_pericopes.json', 'r', encoding='utf-8') as f:
        pericope_data = json.load(f)

    print(f"   Loaded {len(pericope_data['pericopes'])} pericopes")

    # Build new pericope list with correct Orthodox numbering
    print("\n3. Remapping all psalms to Orthodox numbering...")
    new_pericopes = []
    fixed_count = 0
    skipped_count = 0

    for orthodox_num in sorted(ORTHODOX_TO_CATHOLIC_MAPPING.keys()):
        mapping = ORTHODOX_TO_CATHOLIC_MAPPING[orthodox_num]

        # Get Orthodox chapter data
        if orthodox_num not in orthodox_chapters:
            print(f"   Warning: Orthodox Psalm {orthodox_num} not found in Bible data")
            continue

        orthodox_chapter = orthodox_chapters[orthodox_num]

        # Handle special case: Psalm 151 (LXX only, no Catholic equivalent)
        if mapping is None:
            print(f"   Psalm {orthodox_num}: LXX only, creating from Orthodox data")
            # Create a single pericope with all verses
            pericope_entry = {
                'pericope_id': f"Psalms_{orthodox_num:03d}_01",
                'chapter': orthodox_num,
                'pericope_num': "01",
                'title_en': f"Psalm {orthodox_num}",
                'title_ro': f"Psalmul {orthodox_num}",
                'start_verse': 1,
                'end_verse': len(orthodox_chapter['verses']),
                'verse_count': len(orthodox_chapter['verses']),
                'verses': [{'verse': v['verse'], 'text': v['text']}
                          for v in orthodox_chapter['verses']]
            }
            new_pericopes.append(pericope_entry)
            fixed_count += 1
            continue

        # Handle combined psalms (9, 113)
        if isinstance(mapping, list):
            print(f"   Psalm {orthodox_num}: Combined from Catholic Psalms {[m[0] for m in mapping]}")
            # For now, just use all verses from Orthodox version as one pericope
            pericope_entry = {
                'pericope_id': f"Psalms_{orthodox_num:03d}_01",
                'chapter': orthodox_num,
                'pericope_num': "01",
                'title_en': f"Psalm {orthodox_num}",
                'title_ro': f"Psalmul {orthodox_num}",
                'start_verse': 1,
                'end_verse': len(orthodox_chapter['verses']),
                'verse_count': len(orthodox_chapter['verses']),
                'verses': [{'verse': v['verse'], 'text': v['text']}
                          for v in orthodox_chapter['verses']]
            }
            new_pericopes.append(pericope_entry)
            fixed_count += 1
            continue

        # Regular mapping
        catholic_num, verse_range = mapping

        # For now, create a single pericope with all verses from the Orthodox psalm
        # (We'll lose the detailed pericope structure, but at least the verses will be correct)
        pericope_entry = {
            'pericope_id': f"Psalms_{orthodox_num:03d}_01",
            'chapter': orthodox_num,
            'pericope_num': "01",
            'title_en': f"Psalm {orthodox_num}",
            'title_ro': f"Psalmul {orthodox_num}",
            'start_verse': 1,
            'end_verse': len(orthodox_chapter['verses']),
            'verse_count': len(orthodox_chapter['verses']),
            'verses': [{'verse': v['verse'], 'text': v['text']}
                      for v in orthodox_chapter['verses']]
        }
        new_pericopes.append(pericope_entry)
        fixed_count += 1

    # Update pericope data
    print("\n4. Updating pericope data structure...")
    pericope_data['pericopes'] = new_pericopes
    pericope_data['pericope_count'] = len(new_pericopes)

    # Save updated pericope data
    print("\n5. Saving fixed pericope data...")
    output_path = Path('bible_books_pericopes/19_Psalmi_pericopes.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(pericope_data, f, ensure_ascii=False, indent=2)

    print(f"   Saved to {output_path}")

    print("\n" + "="*80)
    print("PSALM NUMBERING FIX COMPLETE")
    print("="*80)
    print(f"\nPsalms fixed: {fixed_count}")
    print(f"Psalms skipped: {skipped_count}")
    print(f"\nNote: Each Psalm now has 1 pericope containing all verses.")
    print("The detailed pericope structure from Catholic numbering was lost,")
    print("but all verses are now correct according to Orthodox numbering.")
    print("\nNext step: Run 4_generate_markdown.py to regenerate all Psalm markdown files")
    print("="*80 + "\n")


if __name__ == '__main__':
    fix_all_psalms()
