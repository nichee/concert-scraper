import httpx
from rapidfuzz import fuzz

SEARCH_URL = "https://peatix.com/search/events"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json, text/javascript, */*",
    "X-Requested-With": "XMLHttpRequest",
}
MATCH_THRESHOLD = 80  # minimum fuzzy match score (0-100)


def search(artist: str, country: str = "SG") -> list[dict]:
    """Search Peatix for events matching an artist name. Returns matched events."""
    try:
        r = httpx.get(
            SEARCH_URL,
            params={"q": artist, "l.country": country},
            headers=HEADERS,
            follow_redirects=True,
            timeout=10,
        )
        r.raise_for_status()
    except httpx.HTTPError as e:
        print(f"[peatix] HTTP error for '{artist}': {e}")
        return []

    events = r.json().get("json_data", {}).get("events", [])
    matched = []
    for event in events:
        name = event.get("name", "")
        score = fuzz.partial_ratio(artist.lower(), name.lower())
        if score >= MATCH_THRESHOLD:
            matched.append({
                "source": "peatix",
                "artist_query": artist,
                "match_score": score,
                "name": name,
                "date": event.get("datetime"),
                "venue": event.get("venue_name"),
                "url": f"https://peatix.com/event/{event['id']}",
            })
    return matched
