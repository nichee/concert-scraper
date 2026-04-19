# Concert Scraper — Project Plan

## Problem

I follow a lot of artists on Spotify, including niche ones. Spotify's concert discovery is incomplete — small acts often don't upload their shows there, and many events are listed on smaller platforms like Eventbrite or Peatix rather than big ticketers (e.g. LiveNation, Ticketmaster). I want a tool that aggregates concert listings across sources and alerts me when artists I follow are playing nearby.

## Goal

Build a scraper that:
1. Takes a list of artists derived from Spotify (followed + top + liked songs)
2. Fans out across multiple concert/ticketing platforms
3. Deduplicates results
4. Filters for Singapore / SEA events
5. Surfaces matches in a useful format (TBD: Telegram bot, email digest, or web UI)

---

## Artist List Strategy

Artists are sourced from Spotify in tiers, saved to `data/artists.json` (Tier 1+2) and `data/artists_tier3.json` (noise):

| Tier | Sources | Signal |
|---|---|---|
| **1** | Followed artists, top artists short term | Explicit intent + recent listening |
| **2** | Top artists medium/long term, liked songs (3+ tracks) | Consistent history |
| **3** | Liked songs (1-2 tracks), playlist artists | Too noisy — saved separately |

---

## Data Sources

### Priority 1 — Build these first

| Source | Method | Notes |
|---|---|---|
| **Bandsintown** | API or scrape artist pages | Artists self-submit — best niche coverage. Try `rest.bandsintown.com/artists/{name}/events` first. |
| **DICE.fm** | Scrape (Playwright) | Where SG indie/alternative promoters list shows. No public API. JS-rendered. |
| **Resident Advisor** | Scrape | Good for electronic/experimental. Covers SG well. |

### Priority 2 — Add after Priority 1

| Source | Method | Notes |
|---|---|---|
| **Eventbrite** | Scrape search page | API killed in 2020. Still worth scraping for mid-size acts. |
| **Songkick** | Scrape artist pages | API locked for hobbyists. Public artist pages are scrapable. |
| **Venue websites** | Scrape upcoming pages | The Projector, Esplanade, Timbre, Decline Effect, Eat At Seven. Scan for artist name matches. |

### Deprioritised

| Source | Reason |
|---|---|
| **Peatix** | Heavily Japan-biased search results. `l.country=SG` param does nothing. Very few SG results for niche Western acts. Low ROI. |
| **Facebook / Instagram** | Aggressive bot detection, login walls. Not worth it. |

---

## Architecture

```
Spotify OAuth → Tier 1+2 artist list (data/artists.json)
        ↓
Fan out per artist to all scrapers (with delay to avoid rate limiting)
        ↓
Filter: Singapore / SEA only (timezone + lat/lng bounding box)
        ↓
Fuzzy match artist name against event title (rapidfuzz, threshold 80)
        ↓
Deduplicate across sources
        ↓
Save to results/YYYY-MM-DD_HH-MM-SS.json
        ↓
Notify (TBD: Telegram bot or email digest)
```

---

## Stack

- **Language:** Python
- **HTTP:** `httpx`
- **Parsing:** `BeautifulSoup` for static HTML, `Playwright` for JS-heavy sites (DICE)
- **Fuzzy matching:** `rapidfuzz` (`partial_ratio`, threshold 80)
- **Rate limiting:** 0.5s delay between requests per artist, jitter if needed
- **Scheduling:** cron job, daily or weekly
- **Notifications:** Telegram bot or email digest — TBD

---

## Phases

### Phase 1 — Scaffold + Peatix scraper ✅
- [x] Set up project structure (venv, dependencies)
- [x] Spotify OAuth → pull artist list by tier into `data/artists.json`
- [x] Peatix scraper (hits JSON API, SG filter via timezone + lat/lng)
- [x] Save results to `results/` as timestamped JSON

### Phase 2 — Better sources
- [ ] Bandsintown scraper (most important — try API first, fall back to scraping)
- [ ] DICE.fm scraper (Playwright)
- [ ] Resident Advisor scraper
- [ ] Eventbrite scraper

### Phase 3 — Intelligence layer
- [ ] Deduplication (same event from multiple sources)
- [ ] Optional: LLM pass for digest generation or extracting structured data from messy descriptions

### Phase 4 — Automation & notification
- [ ] Cron job or scheduler
- [ ] Telegram bot or email digest

### Phase 5 — Venue-level scraping
- [ ] Maintain SG venue list
- [ ] Scrape venue "upcoming" pages, match against artist list

---

## Notes

- **Peatix lesson:** Don't assume a platform is useful without testing. `l.country=SG` param did nothing — all results were Japanese events. SG filtering had to be done client-side via `timezone_id` and lat/lng bounding box.
- **LLM as judge:** Not needed for relevance filtering — fuzzy matching handles that. More useful for deduplication across sources and generating readable digests. Defer to Phase 3.
- **Bandsintown public API:** `rest.bandsintown.com/artists/{name}/events?app_id=YOUR_ID` — loosely enforced for personal projects. Worth trying before scraping their HTML pages.
- **Fuzzy matching is critical.** Artist names appear differently across platforms. `rapidfuzz.partial_ratio` at threshold 80 works well.
