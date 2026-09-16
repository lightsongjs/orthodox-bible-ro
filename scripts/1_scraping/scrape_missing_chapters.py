# -*- coding: utf-8 -*-
"""Scrape a chapter from bibliaortodoxa.ro.

The page markup changed since scrape_romanian_chapter.py was written: verses now
sit in `<tr id=versetN>` rows (unquoted attribute) with the text in the second
`<td>`, so the old `soup.find(id="versetN")` lookup no longer matches. This
module parses the current markup and needs no BeautifulSoup.

Usage: python3 scrape_missing_chapters.py --id 7 --chapter 1 --out file.json
       python3 scrape_missing_chapters.py --verify           # self-check
"""
import re, json, html, argparse, urllib.request, time

BASE = "https://www.bibliaortodoxa.ro/carte.php?id={bid}&cap={cap}"
ROW = re.compile(r'<tr\s+id=verset(\d+)>(.*?)</tr>', re.S | re.I)
CELLS = re.compile(r'<td[^>]*>(.*?)</td>', re.S | re.I)
TAG = re.compile(r'<[^>]+>')


def fetch(bid, cap=1, timeout=20):
    req = urllib.request.Request(BASE.format(bid=bid, cap=cap),
                                 headers={'User-Agent': 'Mozilla/5.0 (orthodox-bible-ro)'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
    for enc in ('utf-8', 'iso-8859-2', 'windows-1250'):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode('utf-8', 'replace')


def clean(fragment):
    text = html.unescape(TAG.sub('', fragment))
    return re.sub(r'\s+', ' ', text).strip()


def parse_chapter(page):
    verses = []
    for m in ROW.finditer(page):
        num = int(m.group(1))
        cells = CELLS.findall(m.group(2))
        if len(cells) < 2:
            continue
        text = clean(cells[1])
        if text:
            verses.append({'verse': num, 'text': text})
    return verses


def scrape(bid, cap=1, delay=1.0):
    v = parse_chapter(fetch(bid, cap))
    time.sleep(delay)
    return v


def verify():
    """Re-scrape books we already hold and require a byte-identical result."""
    import glob, os, sys
    SRC = os.path.join(os.path.dirname(__file__), '..', '..', 'source', 'bible_books')
    cases = [(54, '51_Manase.json', 1), (75, '47_Susanei.json', 1), (8, '42_Baruh.json', 1)]
    ok = True
    for bid, fname, cap in cases:
        path = [p for p in glob.glob(os.path.join(SRC, '*.json')) if os.path.basename(p) == fname][0]
        d = json.load(open(path, encoding='utf-8'))
        want = [(v['verse'], v['text'].strip())
                for v in [c for c in d['chapters'] if c['chapter'] == cap][0]['verses']]
        got = [(v['verse'], v['text'].strip()) for v in scrape(bid, cap)]
        same = got == want
        ok &= same
        print(f"  id={bid:<3} {d['name_ro']:<10} cap {cap}: sursa={len(want)} versete, "
              f"scrapat={len(got)} -> {'IDENTIC' if same else 'DIFERIT'}")
        if not same:
            for i, (a, b) in enumerate(zip(got, want)):
                if a != b:
                    print(f"     prima diferenta la versetul {a[0]}")
                    break
    return ok


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--id', type=int)
    ap.add_argument('--chapter', type=int, default=1)
    ap.add_argument('--out')
    ap.add_argument('--verify', action='store_true')
    a = ap.parse_args()
    if a.verify:
        raise SystemExit(0 if verify() else 1)
    verses = scrape(a.id, a.chapter)
    print(f"{len(verses)} versete")
    if a.out:
        json.dump(verses, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
