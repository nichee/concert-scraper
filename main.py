import json
import os
import time
from datetime import datetime
from scrapers import peatix

DELAY = 0.5  # seconds between requests


def load_artists():
    with open("data/artists.json") as f:
        return json.load(f)


def main():
    artists = load_artists()
    print(f"Searching for {len(artists)} artists...\n")
    all_results = []

    for artist in artists:
        results = peatix.search(artist)  # filters to SG internally
        if results:
            all_results.extend(results)
            for r in results:
                print(f"[{r['source']}] {r['name']}")
                print(f"  Artist : {r['artist_query']} (score: {r['match_score']})")
                print(f"  Date   : {r['date']}")
                print(f"  Venue  : {r['venue']}")
                print(f"  URL    : {r['url']}")
                print()
        else:
            print(f"  No results: {artist}")
        time.sleep(DELAY)

    print(f"\nTotal matches: {len(all_results)}")

    os.makedirs("results", exist_ok=True)
    filename = f"results/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    with open(filename, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"Saved to {filename}")


if __name__ == "__main__":
    main()
