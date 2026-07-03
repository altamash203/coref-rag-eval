"""
fetch_article.py — Test 6

Fetch a Wikipedia article via the MediaWiki API (explaintext), clean it up,
and truncate to ~5,000 words. Mirrors the role of the fetch/clean step used
for Test 4 (Apollo 11) and Test 5 (World War II).

Usage:
    python fetch_article.py
"""

import json
import re
import urllib.parse
import urllib.request

ARTICLE_TITLE = "French Revolution"
OUTPUT_PATH = "test-6-data/french_revolution_wikipedia.txt"
TARGET_WORDS = 5000

API_URL = "https://en.wikipedia.org/w/api.php"


def fetch_article(title: str) -> str:
    """Fetch plain-text article content via the Wikipedia API (explaintext)."""
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": "1",
        "titles": title,
        "format": "json",
        "redirects": "1",
    }
    url = API_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "coref-rag-test/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)

    pages = data["query"]["pages"]
    page = next(iter(pages.values()))
    if "extract" not in page:
        raise RuntimeError(f"No extract found for title: {title!r}")
    return page["extract"]


def clean_text(raw: str) -> str:
    """Strip markup/citation artifacts and normalize whitespace."""
    text = raw

    # Drop section headers like "== See also ==" but keep the following text
    # (we still want section boundaries visually clear, so keep on own line).
    text = re.sub(r"={2,}\s*(.+?)\s*={2,}", r"\1.", text)

    # Strip bracketed citation markers e.g. [1], [citation needed]
    text = re.sub(r"\[\d+\]", "", text)
    text = re.sub(r"\[citation needed\]", "", text, flags=re.IGNORECASE)

    # Remove leftover parenthetical pronunciation guides / IPA (best-effort)
    text = re.sub(r"\(/[^)]*/\)", "", text)

    # Drop tail sections that are just link lists, not prose
    for stop in ["See also.", "References.", "Further reading.", "External links.", "Bibliography.", "Notes."]:
        idx = text.find(stop)
        if idx != -1:
            text = text[:idx]

    # Normalize whitespace: collapse multiple blank lines / spaces
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    return text


def truncate_to_words(text: str, n_words: int) -> str:
    words = text.split()
    if len(words) <= n_words:
        return text
    truncated = " ".join(words[:n_words])
    # end at the last sentence boundary before the cut for a clean stop
    last_period = truncated.rfind(". ")
    if last_period != -1:
        truncated = truncated[: last_period + 1]
    return truncated


def main():
    raw = fetch_article(ARTICLE_TITLE)
    cleaned = clean_text(raw)
    final = truncate_to_words(cleaned, TARGET_WORDS)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(final)

    word_count = len(final.split())
    print(f"Saved {word_count} words to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
