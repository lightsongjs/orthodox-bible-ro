# Usage Guide

## Installation

### Prerequisites

```bash
# Python 3.8 or higher
python --version

# Git
git --version
```

### Clone Repository

```bash
git clone https://github.com/yourusername/orthodox-bible-ro.git
cd orthodox-bible-ro
```

### Install Dependencies

```bash
pip install -r scripts/requirements.txt
```

Required packages:
- `requests` - HTTP requests for scraping
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parser

## Data Pipeline

### Step 1: Download Romanian Bible

Downloads all 78 books from BibliaOrtodoxa.ro:

```bash
python scripts/1_scraping/1_download_bible.py
```

**Output:** `source/bible_books/*.json` (7.4 MB, 78 files)

**Note:** Only needed if source data is missing or you want to refresh from BibliaOrtodoxa.ro

### Step 2: Scrape English Bible (Optional)

Downloads English NRSVCE translation from BibleGateway:

```bash
python scripts/1_scraping/scrape_biblegateway.py
```

**Output:** `output/markdown_en/*.md` (1.6 MB, 2,925 files)

**Note:** Rate-limited, takes ~2-3 hours. Only needed for English markdown.

### Step 3: Create Pericope JSON

Splits Bible books into pericopes based on `pericope_structure.json`:

```bash
python scripts/2_processing/3_create_pericopes.py
```

**Input:**
- `source/bible_books/*.json`
- `source/pericope_structure.json`
- `source/bible_books_metadata.json`

**Output:** `output/bible_books_pericopes/*.json` (8.2 MB, 71 files)

### Step 4: Generate Markdown

Converts pericope JSON to markdown files:

```bash
python scripts/2_processing/4_generate_markdown.py
```

**Input:** `output/bible_books_pericopes/*.json`

**Output:**
- `output/Biblia_Generata/` (14 MB, 2,746+ files)
- Romanian markdown with Romanian filenames

### Step 5: Validate (Optional)

Check data completeness:

```bash
python scripts/3_validation/validate_completeness.py
```

Verifies:
- All books present
- All chapters present
- All verses present
- Pericope coverage

## Common Tasks

### Regenerate Everything from Scratch

```bash
# Full pipeline (excluding scraping)
python scripts/2_processing/3_create_pericopes.py
python scripts/2_processing/4_generate_markdown.py
python scripts/3_validation/validate_completeness.py
```

### Update Only Romanian Markdown

```bash
python scripts/2_processing/4_generate_markdown.py --language ro
```

### Fix Corrupted Pericopes

```bash
python scripts/1_scraping/fix_corrupted_pericopes.py
```

### Extract Missing Pericopes

If some pericopes are missing:

```bash
python scripts/1_scraping/identify_missing_pericopes.py
python scripts/1_scraping/extract_missing_pericopes.py
```

## Data Access

### Reading Bible Books

```python
import json

# Load a book
with open('source/bible_books/52_Matei.json', 'r', encoding='utf-8') as f:
    matthew = json.load(f)

# Access verse
chapter_1 = matthew['chapters'][0]
verse_1 = chapter_1['verses'][0]
print(verse_1['text'])  # "Cartea neamului lui Iisus Hristos..."
```

### Reading Pericopes

```python
import json

# Load pericope-based book
with open('output/bible_books_pericopes/52_Matei_pericopes.json', 'r', encoding='utf-8') as f:
    matthew_pericopes = json.load(f)

# Access first pericope
pericope = matthew_pericopes['pericopes'][0]
print(f"{pericope['title_ro']} ({pericope['verses_start']}-{pericope['verses_end']})")
```

### Reading Markdown

Markdown files have YAML frontmatter:

```markdown
---
testament: NT
book: Matthew
book_romanian: Matei
chapter: 1
pericope: 1
pericope_title_en: "The Genealogy of Jesus the Messiah"
pericope_title_ro: "Neamul lui Iisus Hristos"
verses_start: 1
verses_end: 17
verses_total: 17
language: ro
---

1. Cartea neamului lui Iisus Hristos...
```

## Troubleshooting

### "Module not found"

```bash
pip install -r scripts/requirements.txt
```

### "File not found: pericope_structure.json"

Ensure you're running from repo root:

```bash
cd orthodox-bible-ro
python scripts/2_processing/3_create_pericopes.py
```

### "Permission denied"

On Windows, close OneDrive sync for the folder.

### Rate Limiting (BibleGateway)

The scraper includes delays. If rate-limited:
- Increase sleep time in `scrape_biblegateway.py`
- Run overnight
- Use existing English markdown in repo

## Performance

| Task | Time | Output Size |
|------|------|-------------|
| Download Romanian Bible | 5-10 min | 7.4 MB |
| Scrape English Bible | 2-3 hours | 1.6 MB |
| Create Pericopes | 30 sec | 8.2 MB |
| Generate Markdown | 1 min | 16 MB |
| Validate | 10 sec | - |

## Next Steps

- See [PIPELINE.md](PIPELINE.md) for detailed architecture
- See [API.md](API.md) for JSON schema
- See [PERICOPE_OVERLAPS.md](PERICOPE_OVERLAPS.md) for known issues
