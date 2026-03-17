# Orthodox Bible - Romanian Edition

**Complete Romanian Orthodox Bible in JSON and Markdown formats with bilingual pericope structure**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📖 Overview

This repository contains the complete Romanian Orthodox Bible (Biblia Ortodoxă Română) with:
- **78 biblical books** in JSON format (Romanian text from [BibliaOrtodoxa.ro](https://www.bibliaortodoxa.ro/))
- **English translation** (NRSVCE from BibleGateway)
- **Pericope structure** (2,746+ liturgical readings)
- **Complete processing pipeline** - all scripts to regenerate data from scratch

## 📊 Statistics

| Category | Count | Size |
|----------|-------|------|
| **Biblical Books (JSON)** | 78 | 7.4 MB |
| **Pericope JSON** | 71 | 8.2 MB |
| **Markdown Files (RO)** | 2,894 | 1.6 MB |
| **Markdown Files (EN)** | 2,925 | 1.6 MB |
| **Total Chapters** | 1,345 | - |
| **Total Verses** | ~31,000 | - |

## 🗂️ Repository Structure

```
orthodox-bible-ro/
│
├── 📁 source/                          # SOURCE DATA (truth)
│   ├── pericope_structure.json        # Pericope definitions (674 KB)
│   ├── bible_books_metadata.json      # Book metadata
│   └── bible_books/                   # 78 JSON files (7.4 MB)
│       ├── 01_Facerea.json            # Genesis
│       ├── 52_Matei.json              # Matthew
│       └── ...
│
├── 📁 scripts/                         # PROCESSING PIPELINE
│   ├── 1_scraping/                    # Data acquisition
│   │   ├── scrape_biblegateway.py     # Scrape English text
│   │   └── 1_download_bible.py        # Download Romanian text
│   │
│   ├── 2_processing/                  # Data transformation
│   │   ├── 3_create_pericopes.py      # Create pericope JSON
│   │   └── 4_generate_markdown.py     # Generate markdown
│   │
│   └── 3_validation/                  # Quality checks
│       ├── validate_completeness.py
│       └── compare_bibles.py
│
├── 📁 output/                          # GENERATED OUTPUT
│   ├── bible_books_pericopes/         # 71 JSON (pericope-based)
│   ├── markdown_ro/                   # Romanian markdown
│   ├── markdown_en/                   # English markdown
│   └── Biblia_Generata/               # Complete Bible markdown
│
├── 📁 docs/
│   ├── USAGE.md                       # How to use
│   ├── PIPELINE.md                    # Pipeline explained
│   └── API.md                         # Data format specification
│
├── .gitignore
├── LICENSE
└── README.md
```

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+
python --version

# Install dependencies
pip install -r scripts/requirements.txt
```

### Regenerate Everything

```bash
# 1. Download Romanian Bible (if needed)
python scripts/1_scraping/1_download_bible.py

# 2. Scrape English Bible (if needed)
python scripts/1_scraping/scrape_biblegateway.py

# 3. Create pericope JSON files
python scripts/2_processing/3_create_pericopes.py

# 4. Generate markdown files
python scripts/2_processing/4_generate_markdown.py

# 5. Validate completeness
python scripts/3_validation/validate_completeness.py
```

## 📚 Data Formats

### Bible Books JSON (source/bible_books/)

```json
{
  "id": 55,
  "book_number": 52,
  "name_en": "Matthew",
  "name_ro": "Matei",
  "testament": "NT",
  "chapter_count": 28,
  "url": "https://www.bibliaortodoxa.ro/carte.php?id=55",
  "chapters": [
    {
      "chapter": 1,
      "verses": [
        {
          "verse": 1,
          "text": "Cartea neamului lui Iisus Hristos..."
        }
      ]
    }
  ]
}
```

### Pericope Structure (source/pericope_structure.json)

```json
{
  "Matthew": {
    "1": [
      {
        "title": "The Genealogy of Jesus the Messiah",
        "start_verse": 1,
        "end_verse": 17
      }
    ]
  }
}
```

### Pericope JSON (output/bible_books_pericopes/)

```json
{
  "id": 55,
  "name_en": "Matthew",
  "name_ro": "Matei",
  "pericope_count": 156,
  "pericopes": [
    {
      "pericope_id": "Matthew_01_01",
      "chapter": 1,
      "pericope_num": "01",
      "title_en": "The Genealogy of Jesus the Messiah",
      "title_ro": "Neamul lui Iisus Hristos",
      "start_verse": 1,
      "end_verse": 17,
      "verse_count": 17,
      "verses": [...]
    }
  ]
}
```

## ⚠️ Known Issues

### Pericope Overlaps

The source `pericope_structure.json` contains **354 overlapping verse ranges** in 44 books. This appears to be intentional for liturgical context (e.g., a new pericope may start with verses from the previous one for continuity).

**Example:** 1 Chronicles 16
- Pericope 1: verses 1-16
- Pericope 2: verses 7-36 (overlaps 7-16)

**Impact:** When displaying pericopes sequentially, verses 7-16 appear twice.

**Solutions:**
1. Accept as liturgical feature (preserve overlap in data)
2. Filter duplicates at display time in consuming applications
3. Correct source data if overlaps are errors (requires theological review)

See `docs/PERICOPE_OVERLAPS.md` for full analysis.

## 📖 Orthodox Canon

This Bible follows the **Eastern Orthodox canon** (78 books total):

### Old Testament (50 books)
- **Pentateuch** (5): Genesis, Exodus, Leviticus, Numbers, Deuteronomy
- **Historical** (17): Joshua, Judges, Ruth, 1-4 Kings, 1-2 Paralipomena, Ezra, Nehemiah, Esther, Tobit, Judith, 1-3 Maccabees
- **Wisdom** (7): Job, Psalms, Proverbs, Ecclesiastes, Song of Songs, Wisdom of Solomon, Sirach
- **Major Prophets** (7): Isaiah, Jeremiah, Lamentations, Baruch, Ezekiel, Daniel, Prayer of Manasseh
- **Minor Prophets** (12): Hosea, Joel, Amos, Obadiah, Jonah, Micah, Nahum, Habakkuk, Zephaniah, Haggai, Zechariah, Malachi
- **Deuterocanonical additions** (2): 3 Ezra, Prayer of the Three Young Men

### New Testament (27 books)
- Standard Protestant/Catholic canon

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

For theological corrections to `pericope_structure.json`, please provide Orthodox liturgical sources.

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- [BibliaOrtodoxa.ro](https://www.bibliaortodoxa.ro/) - Romanian Orthodox Bible text
- [BibleGateway.com](https://www.biblegateway.com/) - English NRSVCE translation
- Orthodox Church for pericope liturgical structure

## 📧 Contact

For questions or theological consultations: [Issues](https://github.com/yourusername/orthodox-bible-ro/issues)

---

**Last Updated:** March 17, 2026
