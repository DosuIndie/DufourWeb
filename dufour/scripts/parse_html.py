import json
from bs4 import BeautifulSoup


def parse_html(html_content):
    """Extract topic, reference, and category from HTML."""
    soup = BeautifulSoup(html_content, "html.parser")
    
    topic = soup.h1.get_text(strip=True) if soup.h1 else ""
    reference = soup.find(class_="reference")
    reference = reference.get_text(strip=True) if reference else ""
    category = soup.find(class_="category")
    category = category.get_text(strip=True) if category else ""
    
    return {
        "topic": topic,
        "reference": reference,
        "category": category,
    }


if __name__ == "__main__":
    # Read from data/ folder
    try:
        with open("data/example.html", "r", encoding="utf-8") as f:
            html = f.read()
        result = parse_html(html)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except FileNotFoundError:
        print("No HTML file found in data/")
