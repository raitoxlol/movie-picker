#!/usr/bin/env python3
"""Rebuild references/catalog.md from IMDb's free public datasets. Standard library only.

    python3 build_catalog.py              # top 300 (default)
    python3 build_catalog.py --top 1000   # any size you like

Ranking is IMDb's published weighted-rating formula over feature films with 25,000+ votes:

    WR = (v / (v + m)) * R + (m / (v + m)) * C      m = 25,000, C = mean vote of the pool

Downloads ~250 MB into ~/.cache/movie-picker the first time (reused afterwards; delete it any
time). Mood tags (tones, pace, subjects) already in the catalog are kept for films that stay in
the list; new films get "-" until tagged.

Information courtesy of IMDb (https://www.imdb.com). Used with permission.
IMDb datasets are for personal and non-commercial use.
"""

from __future__ import annotations

import argparse
import gzip
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

DATASETS = {
    "ratings": "https://datasets.imdbws.com/title.ratings.tsv.gz",
    "basics": "https://datasets.imdbws.com/title.basics.tsv.gz",
}
CACHE = Path.home() / ".cache" / "movie-picker"
CATALOG = Path(__file__).resolve().parent.parent / "references" / "catalog.md"
MIN_VOTES = M = 25_000
LINE = re.compile(r"^\d+\. .* · (tt\d+)$")


def fetch(url: str, path: Path) -> Path:
    if path.is_file() and path.stat().st_size > 0:
        print(f"cached   {path.name}")
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"download {url}")
    tmp = path.with_suffix(".part")
    request = urllib.request.Request(url, headers={"User-Agent": "movie-picker-catalog/1.0"})
    with urllib.request.urlopen(request, timeout=600) as response, tmp.open("wb") as out:
        while chunk := response.read(1 << 20):
            out.write(chunk)
    tmp.rename(path)
    return path


def rows(path: Path):
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as handle:
        header = handle.readline().rstrip("\n").split("\t")
        for line in handle:
            yield dict(zip(header, line.rstrip("\n").split("\t")))


def existing_tags() -> dict[str, tuple[str, str, str]]:
    """imdb_id -> (tones, pace, subjects) from the current catalog, so a rebuild keeps them."""
    tags: dict[str, tuple[str, str, str]] = {}
    if not CATALOG.is_file():
        return tags
    for line in CATALOG.read_text().splitlines():
        match = LINE.match(line)
        if match:
            parts = line.split(" · ")
            tags[match.group(1)] = (parts[4], parts[5], parts[6])
    return tags


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--top", type=int, default=300, help="how many films to keep (default 300)")
    args = parser.parse_args()

    ratings: dict[str, tuple[float, int]] = {}
    for row in rows(fetch(DATASETS["ratings"], CACHE / "title.ratings.tsv.gz")):
        try:
            votes, rating = int(row["numVotes"]), float(row["averageRating"])
        except (KeyError, ValueError):
            continue
        if votes >= MIN_VOTES:
            ratings[row["tconst"]] = (rating, votes)
    mean = sum(r for r, _ in ratings.values()) / len(ratings)

    this_year = date.today().year
    films = []
    for row in rows(fetch(DATASETS["basics"], CACHE / "title.basics.tsv.gz")):
        tconst = row["tconst"]
        if tconst not in ratings or row.get("titleType") != "movie" or row.get("isAdult") == "1":
            continue
        try:
            year, runtime = int(row["startYear"]), int(row["runtimeMinutes"])
        except (KeyError, ValueError):
            continue
        if not (1900 < year <= this_year and 40 <= runtime <= 260):
            continue
        rating, votes = ratings[tconst]
        weighted = (votes / (votes + M)) * rating + (M / (votes + M)) * mean
        genres = "" if row.get("genres") == r"\N" else row["genres"].replace(",", "/")
        films.append((weighted, row["primaryTitle"], year, runtime, rating, genres, tconst))

    films.sort(key=lambda f: (-f[0], f[1]))
    tags = existing_tags()
    lines = [
        f"# Ranked film catalog ({min(args.top, len(films))} films)",
        "",
        f"Rebuilt {date.today().isoformat()} by scripts/build_catalog.py from IMDb's public datasets,",
        "ranked by IMDb's weighted-rating formula (feature films, 25,000+ votes).",
        "Information courtesy of IMDb (https://www.imdb.com). Used with permission. Non-commercial use.",
        "",
        "Format: rank. Title (year) · runtime · IMDb rating · genres · tones · pace · subjects · IMDb id",
        "",
    ]
    for rank, (_, title, year, runtime, rating, genres, tconst) in enumerate(films[: args.top], start=1):
        tones, pace, subjects = tags.get(tconst, ("-", "-", "-"))
        lines.append(" · ".join([f"{rank}. {title} ({year})", f"{runtime}m", f"{rating}", genres or "-",
                                 tones, pace, subjects, tconst]))
    CATALOG.write_text("\n".join(lines) + "\n")
    kept = sum(1 for f in films[: args.top] if f[6] in tags)
    print(f"wrote {min(args.top, len(films))} films to {CATALOG} ({kept} kept their mood tags)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
