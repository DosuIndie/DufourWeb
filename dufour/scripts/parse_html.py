import json
import os
from bs4 import BeautifulSoup


def parse_html(html_content: str) -> list[dict]:
    """Parse HTML content and extract topic, references with categories."""
    soup = BeautifulSoup(html_content, "html.parser")
    topic = soup.h1.get_text(strip=True) if soup.h1 else ""
    results = []

    for p in soup.find_all("p"):
        for a in p.find_all("a", href=True):
            reference = a.get_text(strip=True)
            if not reference:
                continue
            # Determine category based on surrounding context
            category = _determine_category(p, reference)
            results.append({
                "topic": topic,
                "reference": reference,
                "category": category,
            })

    return results


def _determine_category(paragraph, reference: str) -> str:
    """Heuristic category detection based on paragraph content."""
    text = paragraph.get_text()
    
    if any(term in text for term in ["Mt ", "Mk ", "Lk ", "Joh "]):
        return "Evangelien"
    if any(term in text for term in ["Röm ", "1 Kor ", "2 Kor ", "Gal ", "Eph ", "Phil ", "Kol ",
                                       "1 Thess ", "2 Thess ", "1 Tim ", "2 Tim ", "Tit ", "Phlm ",
                                       "Hebr ", "Jak ", "1 Petr ", "2 Petr ", "1 Joh ", "2 Joh ",
                                       "3 Joh ", "Jud ", "Offb "]):
        return "Neues Testament"
    if any(term in text for term in ["Jes ", "Jer ", "Ez ", "Dan ", "Hos ", "Joel ", "Am ", "Obd ",
                                       "Jon ", "Mi ", "Nah ", "Hab ", "Zef ", "Hag ", "Sach ", "Mal "]):
        return "Propheten"
    # Default: Altes Testament (Pentateuch, Geschichtsbücher, Weisheitsliteratur)
    return "Altes Testament"


if __name__ == "__main__":
    data_dir = "data"
    all_results = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".html"):
            filepath = os.path.join(data_dir, filename)
            # Try UTF-8 first, fallback to Latin-1
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    html = f.read()
            except UnicodeDecodeError:
                with open(filepath, "r", encoding="latin-1") as f:
                    html = f.read()
            all_results.extend(parse_html(html))
    print(json.dumps(all_results, ensure_ascii=False, indent=2))