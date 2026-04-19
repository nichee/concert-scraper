# Concert Scraper — Progress Log

## Phase 1: Scaffold + Peatix scraper

### Status: In Progress

### Session: 2026-04-20

#### Done
- Initialized git repo
- Created `PLAN.md` with full architecture, data source tiers, and phased roadmap

#### In Progress
- Phase 2 scrapers: Eventbrite, DICE, Bandsintown, Songkick

#### Decisions
- Scraping everything rather than using APIs — API access is either dead (Eventbrite), locked (Songkick), or loosely enforced (Bandsintown). Scraping is more reliable for niche coverage.
- Peatix is NOT server-rendered as assumed — results load via AJAX from `https://peatix.com/search/events`. This endpoint returns clean JSON, which is even better than scraping HTML.
- Python stack: `httpx` for requests, `rapidfuzz` for fuzzy artist matching. BeautifulSoup not needed for Peatix.
- Output for Phase 1: print to stdout.
- Fuzzy match threshold set to 80 (partial_ratio). The country filter (`l.country=SG`) works correctly — verified against known queries.

#### Done
- [x] Set up venv, installed `httpx`, `beautifulsoup4`, `rapidfuzz`
- [x] Hardcoded artist list in `main.py` (10 artists)
- [x] `scrapers/peatix.py` — hits JSON search API, fuzzy matches results, returns structured dicts
- [x] `main.py` — fans out to Peatix per artist, prints matches
- Verified: scraper works correctly, test artists have 0 Peatix SG listings (expected for niche acts)

#### Pending
- [ ] Phase 2: Eventbrite, DICE, Bandsintown, Songkick scrapers
- [ ] Phase 3: Fuzzy matching, deduplication, location filtering, optional LLM summarizer
- [ ] Phase 4: Spotify OAuth to replace hardcoded artist list, notifications (Telegram or email)
- [ ] Phase 5: Venue-level scraping (The Projector, Esplanade, Timbre, etc.)
