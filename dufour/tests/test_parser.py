import pytest
from scripts.parse_html import parse_html


def test_parse_html_returns_list():
    html = """
    <html><head></head><body>
    <h1>Glaube</h1>
    <p>Der Glaube ist ein Fundament (vgl. <a href="HEBR.html">Hebr 11,1</a>).</p>
    </body></html>
    """
    results = parse_html(html)
    assert isinstance(results, list)
    assert len(results) > 0


def test_parse_html_fields_not_empty():
    html = """
    <html><head></head><body>
    <h1>BAUM</h1>
    <p>Der Gerechte ist wie ein Baum (Ps 1,3).</p>
    <p>Jesus sagte: Ich bin der Weinstock (<a href="JOH.html">Joh 15,1</a>).</p>
    </body></html>
    """
    results = parse_html(html)
    for entry in results:
        assert entry["topic"] == "BAUM"
        assert entry["reference"] != ""
        assert entry["category"] != ""


def test_parse_html_empty_html():
    """Test with minimal HTML content."""
    html = "<html><head></head><body></body></html>"
    results = parse_html(html)
    assert results == []


def test_parse_html_multiple_references():
    """Test parsing multiple references in one paragraph."""
    html = """
    <html><head></head><body>
    <h1>GLAUBE</h1>
    <p>Wie Abraham (<a href="GEN.html">Gen 15,6</a>) und Mose (<a href="EX.html">Ex 14,31</a>).</p>
    </body></html>
    """
    results = parse_html(html)
    assert len(results) >= 2