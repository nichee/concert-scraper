"""
Fetches artists from Spotify and saves them in tiers:

Tier 1 (high signal):
  - Followed artists
  - Top artists short term

Tier 2 (medium signal):
  - Top artists medium + long term
  - Liked songs artists with 3+ liked tracks

Tier 3 (noisy, saved separately, not used for scraping):
  - Playlist artists
  - Liked songs artists with 1-2 tracks
"""
import json
import os
import urllib.parse
import webbrowser
from collections import Counter
from http.server import BaseHTTPRequestHandler, HTTPServer

import httpx
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "user-follow-read user-library-read user-top-read playlist-read-private"

auth_code = None


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        auth_code = params.get("code", [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Got it! You can close this tab.")

    def log_message(self, *args):
        pass


def get_auth_code():
    params = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
    })
    url = f"https://accounts.spotify.com/authorize?{params}"
    print(f"Opening Spotify login...\n{url}\n")
    webbrowser.open(url)
    server = HTTPServer(("127.0.0.1", 8888), CallbackHandler)
    server.handle_request()
    return auth_code


def get_access_token(code):
    r = httpx.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
        },
        auth=(CLIENT_ID, CLIENT_SECRET),
    )
    if r.status_code != 200:
        print(f"Token error: {r.status_code} {r.text}")
        r.raise_for_status()
    return r.json()["access_token"]


def paginate(token, url, params=None):
    headers = {"Authorization": f"Bearer {token}"}
    while url:
        r = httpx.get(url, headers=headers, params=params)
        r.raise_for_status()
        data = r.json()
        yield data
        params = None
        url = data.get("next")


def fetch_followed(token):
    artists = set()
    url = "https://api.spotify.com/v1/me/following"
    params = {"type": "artist", "limit": 50}
    headers = {"Authorization": f"Bearer {token}"}
    while url:
        r = httpx.get(url, headers=headers, params=params)
        r.raise_for_status()
        data = r.json()["artists"]
        artists.update(a["name"] for a in data["items"])
        url = data.get("next")
        params = {}
    print(f"  Followed artists:         {len(artists)}")
    return artists


def fetch_top(token, time_range):
    artists = set()
    for page in paginate(token, "https://api.spotify.com/v1/me/top/artists", {"limit": 50, "time_range": time_range}):
        artists.update(a["name"] for a in page.get("items", []))
        if not page.get("next"):
            break
    return artists


def fetch_liked_songs_by_count(token):
    """Returns a Counter of artist -> number of liked tracks."""
    counts: Counter = Counter()
    for page in paginate(token, "https://api.spotify.com/v1/me/tracks", {"limit": 50}):
        for item in page.get("items", []):
            if item.get("track"):
                for artist in item["track"]["artists"]:
                    counts[artist["name"]] += 1
        if not page.get("next"):
            break
    return counts


def fetch_playlist_artists(token):
    artists = set()
    playlist_ids = []
    for page in paginate(token, "https://api.spotify.com/v1/me/playlists", {"limit": 50}):
        playlist_ids.extend(p["id"] for p in page.get("items", []))
        if not page.get("next"):
            break
    for pid in playlist_ids:
        try:
            for page in paginate(token, f"https://api.spotify.com/v1/playlists/{pid}/tracks", {"limit": 50}):
                for item in page.get("items", []):
                    if item.get("track"):
                        for artist in item["track"]["artists"]:
                            artists.add(artist["name"])
                if not page.get("next"):
                    break
        except httpx.HTTPStatusError:
            pass
    return artists


if __name__ == "__main__":
    code = get_auth_code()
    token = get_access_token(code)

    print("\nFetching artists from all sources...")

    followed = fetch_followed(token)

    top_short = fetch_top(token, "short_term")
    top_medium = fetch_top(token, "medium_term")
    top_long = fetch_top(token, "long_term")
    print(f"  Top artists (short):      {len(top_short)}")
    print(f"  Top artists (med+long):   {len(top_medium | top_long)}")

    liked_counts = fetch_liked_songs_by_count(token)
    liked_high = {a for a, c in liked_counts.items() if c >= 3}
    liked_low = {a for a, c in liked_counts.items() if c < 3}
    print(f"  Liked songs (3+ tracks):  {len(liked_high)}")
    print(f"  Liked songs (1-2 tracks): {len(liked_low)}")

    playlist_artists = fetch_playlist_artists(token)
    print(f"  Playlist artists:         {len(playlist_artists)}")

    tier1 = followed | top_short
    tier2 = (top_medium | top_long | liked_high) - tier1
    tier3 = (liked_low | playlist_artists) - tier1 - tier2

    print(f"\nTier 1 (scrape these):  {len(tier1)}")
    print(f"Tier 2 (scrape these):  {len(tier2)}")
    print(f"Tier 3 (noisy, saved separately): {len(tier3)}")

    os.makedirs("data", exist_ok=True)
    with open("data/artists.json", "w") as f:
        json.dump(sorted(tier1 | tier2), f, indent=2)
    print(f"\nSaved {len(tier1 | tier2)} artists to data/artists.json")

    with open("data/artists_tier3.json", "w") as f:
        json.dump(sorted(tier3), f, indent=2)
    print(f"Saved {len(tier3)} noisy artists to data/artists_tier3.json")
