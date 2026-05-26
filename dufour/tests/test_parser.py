import pytest
from scripts.parse_html import parse_html


def test_parse_html():
    html = """
    <html>
        <h1>Genesis</h1>
        <div class="reference">Gen 1,1</div>
        <div class="category">Altes Testament</div>
    </html>
    """
    result = parse_html(html)
    assert result["topic"] == "Genesis"
    assert result["reference"] == "Gen 1,1"
    assert result["category"] == "Altes Testament"
