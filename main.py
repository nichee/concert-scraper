from scrapers import peatix

ARTISTS = [
    "Black Country New Road",
    "Arooj Aftab",
    "Mdou Moctar",
    "Irreversible Entanglements",
    "Floating Points",
    "Kamasi Washington",
    "Squid",
    "Dry Cleaning",
    "black midi",
    "Yussef Dayes",
]


def main():
    print(f"Searching for {len(ARTISTS)} artists...\n")
    all_results = []

    for artist in ARTISTS:
        results = peatix.search(artist)
        if results:
            all_results.extend(results)
            for r in results:
                print(f"[{r['source']}] {r['name']}")
                print(f"  Artist query : {r['artist_query']} (score: {r['match_score']})")
                print(f"  Date         : {r['date']}")
                print(f"  Venue        : {r['venue']}")
                print(f"  URL          : {r['url']}")
                print()
        else:
            print(f"  No results for: {artist}")

    print(f"\nTotal matches: {len(all_results)}")


if __name__ == "__main__":
    main()
