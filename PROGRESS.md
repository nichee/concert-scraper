# Concert Scraper — Progress Log

## Phase 1: Scaffold + Peatix scraper ✅

### Session: 2026-04-20

#### Done
- [x] Initialized git repo, pushed to GitHub (nichee/concert-scraper)
- [x] Created `PLAN.md` and `PROGRESS.md` as persistent planning docs
- [x] Set up venv, installed `httpx`, `beautifulsoup4`, `rapidfuzz`, `python-dotenv`
- [x] `get_artists.py` — Spotify OAuth flow, pulls artists from followed + top + liked songs + playlists, saves by tier to `data/artists.json` and `data/artists_tier3.json`
- [x] `scrapers/peatix.py` — hits Peatix JSON API, SG filter via `timezone_id` + lat/lng bounding box, fuzzy matches results
- [x] `main.py` — loads `data/artists.json`, fans out to scrapers with 0.5s delay, saves results to `results/YYYY-MM-DD_HH-MM-SS.json`

#### Key Findings
- **Peatix is a weak source for niche Western acts in SG.** The `l.country=SG` API param does nothing — returns Japanese events regardless. SG filtering must be done client-side via `timezone_id == "Asia/Singapore"` or lat/lng bounding box (1.15–1.48, 103.6–104.1).
- **Peatix search is Japan-biased** — even broad queries like "concert" return only Tokyo events. Very few SG listings surface for niche Western artists. Low ROI; deprioritised.
- **Past events are invisible** — Peatix drops finished events from search immediately. Confirmed: Weatherday's finished SG event returned 0 results.
- **Artist list strategy works well** — Spotify OAuth pulling Tier 1+2 (~200-300 artists) gives a good signal list. Tier 3 (playlists, 1-2 liked tracks) is too noisy.

---

## Phase 2: Better sources

### Status: Starting next

#### Priority order
1. **Bandsintown** — artists self-submit, best niche coverage, try public API first
2. **DICE.fm** — where SG indie promoters actually post, needs Playwright
3. **Resident Advisor** — good for electronic/experimental
4. **Eventbrite** — scrape search page (API dead since 2020)
