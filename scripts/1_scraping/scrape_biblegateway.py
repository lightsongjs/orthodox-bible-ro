import requests
from bs4 import BeautifulSoup
import time
import re
import os

def scrape_chapter_from_biblegateway(book_name, chapter_num, version="NRSVCE"):
    """
    Scrape a single chapter and extract pericopes with individual verses

    Returns: List of pericopes with headings and verses
    """

    url = f"https://www.biblegateway.com/passage/?search={book_name}%20{chapter_num}&version={version}"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the main passage content
        passage = soup.find('div', class_='passage-text')

        if not passage:
            return None

        # The actual content is in a nested div with version class
        content_div = passage.find('div', class_='version-' + version)

        if not content_div:
            return None

        # Find all h3 headings (pericope titles)
        headings = content_div.find_all('h3')

        # If no headings, create a single pericope for the entire chapter
        if not headings:
            # Find all verse spans
            verse_spans = content_div.find_all('span', class_=re.compile(r'[A-Za-z]+-\d+-\d+'))

            if not verse_spans:
                return []

            verses = []
            for span in verse_spans:
                span_copy = BeautifulSoup(str(span), 'html.parser').find('span')

                # Remove footnotes and cross-references
                for footnote in span_copy.find_all('sup', class_='footnote'):
                    footnote.decompose()
                for crossref in span_copy.find_all('sup', class_='crossreference'):
                    crossref.decompose()

                # Get verse number
                versenum = span_copy.find('sup', class_='versenum')
                if versenum:
                    verse_num = versenum.get_text(strip=True).replace('\xa0', '').strip()
                    versenum.decompose()
                else:
                    chapternum = span_copy.find('span', class_='chapternum')
                    if chapternum:
                        verse_num = chapternum.get_text(strip=True).replace('\xa0', '').strip()
                        chapternum.decompose()
                    else:
                        continue

                verse_text = span_copy.get_text(strip=True)
                if verse_text:
                    verses.append({'number': verse_num, 'text': verse_text})

            if verses:
                return [{
                    'heading': f'{book_name} Chapter {chapter_num}',
                    'verses': verses
                }]
            else:
                return []

        pericopes = []

        # For each heading, collect verses until the next heading
        for i, heading in enumerate(headings):
            pericope_heading = heading.get_text(strip=True)
            verses = []

            # Find all verse spans between this heading and the next
            # Verses are in spans with class pattern like 'Matt-1-2'
            current = heading.next_sibling

            while current:
                # Stop if we hit another h3
                if hasattr(current, 'name') and current.name == 'h3':
                    break

                # Look for verse spans in this element (skip text nodes)
                if hasattr(current, 'name') and hasattr(current, 'find_all'):
                    # Find all verse spans (have class matching book-chapter-verse pattern)
                    verse_spans = current.find_all('span', class_=re.compile(r'[A-Za-z]+-\d+-\d+'))

                    for span in verse_spans:
                        # Skip if this is the heading itself
                        span_text = span.get_text(strip=True)
                        if span_text == pericope_heading:
                            continue

                        # Clone the span to avoid modifying the original
                        span_copy = BeautifulSoup(str(span), 'html.parser').find('span')

                        # Remove footnotes
                        for footnote in span_copy.find_all('sup', class_='footnote'):
                            footnote.decompose()

                        # Remove cross-references
                        for crossref in span_copy.find_all('sup', class_='crossreference'):
                            crossref.decompose()

                        # Get verse number
                        versenum = span_copy.find('sup', class_='versenum')
                        if versenum:
                            verse_num = versenum.get_text(strip=True).replace('\xa0', '').strip()
                            versenum.decompose()
                        else:
                            # Try to get from chapternum
                            chapternum = span_copy.find('span', class_='chapternum')
                            if chapternum:
                                verse_num = chapternum.get_text(strip=True).replace('\xa0', '').strip()
                                chapternum.decompose()
                            else:
                                continue  # Skip if no verse number found

                        # Get the verse text
                        verse_text = span_copy.get_text(strip=True)

                        if verse_text:
                            verses.append({
                                'number': verse_num,
                                'text': verse_text
                            })

                current = current.next_sibling

            if verses:
                pericopes.append({
                    'heading': pericope_heading,
                    'verses': verses
                })

        return pericopes

    except Exception as e:
        print(f"Error fetching chapter {chapter_num}: {e}")
        return None

def scrape_book_from_biblegateway(book_name, book_slug, max_chapters=50, output_dir="BibleGateway_Bible", version="NRSVCE"):
    """
    Scrape an entire book from BibleGateway

    Args:
        book_name: Display name (e.g., "Matthew")
        book_slug: URL slug (e.g., "Matthew" - same as book_name for NT)
        max_chapters: Maximum chapters to try (will stop when no content found)
    """

    # Create output directory
    book_dir = os.path.join(output_dir, book_name.replace(" ", "_"))
    os.makedirs(book_dir, exist_ok=True)

    print(f"Scraping {book_name} from BibleGateway...")

    total_pericopes = 0
    chapters_found = 0

    for chapter_num in range(1, max_chapters + 1):
        print(f"  Chapter {chapter_num}...", end=" ")

        pericopes = scrape_chapter_from_biblegateway(book_slug, chapter_num, version)

        if not pericopes:
            print("No content - end of book")
            break

        chapters_found += 1
        print(f"Found {len(pericopes)} pericopes")

        # Save each pericope as a separate file
        for pericope_num, pericope in enumerate(pericopes, 1):
            heading = pericope['heading']
            verses = pericope['verses']

            # Format verses - each verse on its own line with number
            formatted_verses = []
            for verse in verses:
                verse_num = verse['number']
                verse_text = verse['text']
                formatted_verses.append(f"{verse_num}. {verse_text}")

            content = '\n'.join(formatted_verses)

            # Create safe filename with pericope number for chronological ordering
            safe_heading = re.sub(r'[<>:"/\\|?*]', '', heading)
            chapter_str = str(chapter_num).zfill(2)
            pericope_str = str(pericope_num).zfill(2)
            filename = f"({book_name} {chapter_str}.{pericope_str}) {safe_heading}.md"
            filepath = os.path.join(book_dir, filename)

            # Skip if file already exists
            if os.path.exists(filepath):
                total_pericopes += 1
                continue

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {heading}\n\n")
                f.write(content)

            total_pericopes += 1

        # Be nice to the server
        time.sleep(0.5)

    print(f"\n{book_name}: {chapters_found} chapters, {total_pericopes} pericopes")
    return chapters_found, total_pericopes

if __name__ == "__main__":
    # Test with Matthew
    chapters, pericopes = scrape_book_from_biblegateway("Matthew", "Matthew")
    print(f"\nTotal: {chapters} chapters, {pericopes} pericopes extracted")
