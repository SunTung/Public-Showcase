"""Bounded Gutenberg book discovery using Gutendex metadata; no content classification.

Only a discovery layer. The existing OPS harvester still validates each raw TXT
and keeps local candidate counts separate from globally verified CELL text.
"""
import json
import urllib.parse
import urllib.request

CATALOG_URL = "https://gutendex.com/books/"
MAX_PAGE = 10000
ALLOWED_CONTENT_HOSTS = {"www.gutenberg.org", "gutenberg.org", "www.gutenberg.net", "gutenberg.net"}


def eligible_plain_text_url(formats):
    """Return a direct Gutenberg text URL, never a PDF/HTML/foreign host."""
    if not isinstance(formats, dict):
        return None
    for mime, url in formats.items():
        if not isinstance(mime, str) or not mime.lower().startswith("text/plain"):
            continue
        if not isinstance(url, str):
            continue
        parts = urllib.parse.urlsplit(url)
        if parts.scheme != "https" or parts.hostname not in ALLOWED_CONTENT_HOSTS:
            continue
        if parts.username or parts.password:
            continue
        if any(x in parts.path.lower() for x in (".pdf", ".html", ".htm")):
            continue
        return url
    return None


def discover_page(page, timeout=18, topic=None, sort="popular", search=None):
    """Return (source tuples, has_next) for an English-only catalog page."""
    page = int(page)
    if not 1 <= page <= MAX_PAGE:
        raise ValueError("CATALOG_PAGE_OUT_OF_RANGE")
    if sort not in ("popular", "ascending", "descending"):
        raise ValueError("CATALOG_SORT_INVALID")
    if topic is not None and (not isinstance(topic, str) or not topic or len(topic) > 70):
        raise ValueError("CATALOG_TOPIC_INVALID")
    if search is not None and (not isinstance(search, str) or not search.strip() or len(search) > 70):
        raise ValueError("CATALOG_SEARCH_INVALID")
    query = {"languages": "en", "page": page, "sort": sort}
    if topic is not None:
        query["topic"] = topic
    if search is not None:
        query["search"] = search.strip()
    request = urllib.request.Request(
        CATALOG_URL + "?" + urllib.parse.urlencode(query),
        headers={"User-Agent": "OPS-F01-Corpus-Harvester/0.2", "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read(1_000_001)
        if len(raw) > 1_000_000:
            raise ValueError("CATALOG_JSON_TOO_LARGE")
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("results"), list):
        raise ValueError("CATALOG_FORMAT_INVALID")
    out = []
    for entry in data["results"]:
        if not isinstance(entry, dict) or "en" not in entry.get("languages", []):
            continue
        book_id = entry.get("id")
        if not isinstance(book_id, int) or book_id <= 0:
            continue
        url = eligible_plain_text_url(entry.get("formats", {}))
        if url:
            out.append(("gutendex-" + str(book_id), url, "txt"))
    return out, bool(data.get("next"))
