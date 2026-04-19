# Concert Scraper — Project Plan

## Problem

I follow a lot of artists on Spotify, including niche ones. Spotify's concert discovery is incomplete — small acts often don't upload their shows there, and many events are listed on smaller platforms like Eventbrite or Peatix rather than big ticketers (e.g. LiveNation, Ticketmaster). I want a tool that aggregates concert listings across sources and alerts me when artists I follow are playing nearby.

## Goal

Build a scraper that:
1. Takes a list of artist names (hardcoded to start, Spotify API later)
2. Fans out across multiple concert/ticketing platforms
3. Deduplicates results
4. Filters for Singapore / SEA events
5. Surfaces matches in a useful format (TBD: Telegram bot, email digest, or web UI)

---

## Data Sources

### Tier 1 — High value, relatively easy to scrape

| Source | Notes |
|---|---|
| **Peatix** | Server-rendered HTML. Search: `peatix.com/search?q={artist}`. Popular in SG/SEA for indie gigs. |
| **Eventbrite** | Search API deprecated in 2020 — scrape the search page (`eventbrite.sg`). Catches mid-size indie acts. |
| **DICE.fm** | No public API. Popular for indie/alternative in SG. Client-side rendered — needs Playwright. |

### Tier 2 — Worth it, slightly harder

| Source | Notes |
|---|---|
| **Bandsintown** | Artist pages are public (`bandsintown.com/{artist}`). API access is locked for hobbyists, but scraping the public pages works. Artists self-submit — good niche coverage. |
| **Songkick** | Same situation — API requires partnership agreement. Scrape artist pages instead. |
| **Venue websites** | Maintain a list of SG venues (The Projector, Esplanade, Timbre, Decline Effect, Eat At Seven) and scan their upcoming event pages for artist name matches. |

### Tier 3 — Very hard, skip for now

| Source | Notes |
|---|---|
| Facebook Events / Instagram | Where promoters actually post, but aggressive bot detection and login walls. Not worth it early on. |

---

## Architecture

```
Hardcoded artist list (→ Spotify API later)
        ↓
Fan out in parallel to all scrapers
        ↓
Fuzzy match artist names (rapidfuzz) against event listings
        ↓
Deduplicate (same event from multiple sources)
        ↓
Filter: Singapore / SEA only
        ↓
Output / notify (TBD)
```

---

## Stack

- **Language:** Python
- **HTTP:** `httpx` (async) or `requests`
- **Parsing:** `BeautifulSoup` for static HTML, `Playwright` for JS-heavy sites (DICE)
- **Fuzzy matching:** `rapidfuzz` — handles "Black Country New Road" vs "Black Country New Road w/ support act"
- **Scheduling:** cron job, daily or weekly
- **Notifications:** Telegram bot (zero frontend work) or email digest — TBD

---

## Phases

### Phase 1 — Scaffold + first scraper
- [ ] Set up project structure (venv, dependencies)
- [ ] Hardcode a test artist list (10–15 artists you follow)
- [ ] Build Peatix scraper (easiest, server-rendered)
- [ ] Print matched events to stdout

### Phase 2 — More sources
- [ ] Add Eventbrite scraper
- [ ] Add DICE.fm scraper (Playwright)
- [ ] Add Bandsintown scraper
- [ ] Add Songkick scraper

### Phase 3 — Intelligence layer
- [ ] Fuzzy matching with `rapidfuzz`
- [ ] Deduplication logic
- [ ] Location filtering (SG / SEA)
- [ ] Optional: LLM pass to summarize/clean up event descriptions

### Phase 4 — Automation & notification
- [ ] Cron job or scheduler
- [ ] Telegram bot or email digest
- [ ] Spotify OAuth → replace hardcoded artist list with followed artists

### Phase 5 — Venue-level scraping
- [ ] Maintain SG venue list
- [ ] Scrape venue "upcoming" pages
- [ ] Match against artist list

---

## Notes

- **Fuzzy matching is critical.** Artist names appear differently across platforms. Use `rapidfuzz` with a threshold (e.g. 85% similarity).
- **LLM as summarizer:** Could use Claude API to clean up scraped event blurbs, extract structured data (date, venue, price), or generate a readable digest. Good addition in Phase 3+.
- **Spotify API:** `GET /v1/me/following?type=artist` gives your full followed artist list. OAuth flow needed. Add in Phase 4 once the core scraping works.
- **Bandsintown:** The public API (`rest.bandsintown.com/artists/{name}/events`) is loosely enforced — may be worth trying before scraping their pages.
