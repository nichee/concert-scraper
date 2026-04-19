import httpx
from rapidfuzz import fuzz

SEARCH_URL = "https://peatix.com/search/events"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json, text/javascript, */*",
    "X-Requested-With": "XMLHttpRequest",
}
MATCH_THRESHOLD = 80

# Singapore bounding box
SG_LAT = (1.15, 1.48)
SG_LNG = (103.6, 104.1)


def _is_singapore(event: dict) -> bool:
    if event.get("timezone_id") == "Asia/Singapore":
        return True
    latlng = event.get("latlng", "")
    if latlng:
        try:
            lat, lng = map(float, latlng.split(","))
            return SG_LAT[0] <= lat <= SG_LAT[1] and SG_LNG[0] <= lng <= SG_LNG[1]
        except ValueError:
            pass
    return False


def search(artist: str) -> list[dict]:
    """Search Peatix for Singapore events matching an artist name."""
    try:
        r = httpx.get(
            SEARCH_URL,
            params={"q": artist},
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
        if not _is_singapore(event):
            continue
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
