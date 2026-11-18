# 🎬 movie-picker

**Stop scrolling. Start watching.**

A [Claude Code](https://claude.com/claude-code) skill that ends movie-night paralysis. It asks you
four quick questions, picks **one** film from the IMDb top 200 that you haven't seen, tells you
where to watch it — your subscriptions, **free legal options**, or rent/buy — and keeps a
watched list that makes every pick smarter than the last.

```
> pick me a movie for tonight. just me, something mind-bending, under 2.5 hours
```

```
🎬 Tonight: Eternal Sunshine of the Spotless Mind (2004) — 108m · #85 · IMDb 8.3

Mind-bending in a different register from Inception — the puzzle is a love story told
through erased memories, running backwards and folding in on itself. It's emotional
sci-fi like Interstellar, which you loved…

📺 Where to watch (US, checked 2026-11-18)
- ⚠️ Your services: Max — JustWatch lists it, another guide says no. Check Max first.
- 🆓 Free: YouTube (free with ads) — one source, unconfirmed
- 💵 Rent/buy: Amazon, Apple TV, Google Play
Confirm: justwatch.com/us/movie/eternal-sunshine-of-the-spotless-mind

If that's not it:
- Memento (2000) — 113m. A harder puzzle box, closest to Inception's logic · free on Roku Channel, Pluto TV
- The Prestige (2006) — 130m. Twisty rivalry thriller with a misdirection payoff

Tell me when you've watched it and how it was.
```

<sub>Real output from a test run, trimmed. Availability is looked up live each time and varies by country.</sub>

## Why it's good

- **It decides.** One pick plus two backups that each go a different direction. No listicles.
- **It asks first.** Mood · who's watching · time · era — one tap each. Already said it? It skips the question.
- **It never repeats.** Everything you've watched is tracked, with your 1–5 rating and why.
- **It learns you.** 4–5★ films become "Loved", 1–2★ become "Disliked", and both steer future picks.
- **It finds where to stream it.** Checks JustWatch live for your country and sorts results into *your
  services*, *free* (Tubi, Pluto TV, Roku Channel, Plex, Kanopy, library cards…), and *rent/buy*.
- **"Free only" mode.** Flip one setting and it only picks what you can watch right now without paying.
- **The pool is yours to change.** Top 200 by default. "Top 50 tonight" or "make it top 100" both
  work, and one script rebuilds the catalog at any size from IMDb's public data.

## Install

**As a Claude Code plugin**

```
/plugin marketplace add raitoxlol/movie-picker
/plugin install movie-picker@movie-picker
```

**Or as a plain skill** (works with any agent that reads `SKILL.md` skills)

```bash
git clone https://github.com/raitoxlol/movie-picker
cp -R movie-picker/skills/movie-picker ~/.claude/skills/
```

Then say **"pick a movie"**. The first time, it asks your country and which services you have.

## Use it

| Say | What happens |
|---|---|
| `pick a movie` / `movie night` | 4 quick questions → one pick + where to watch |
| `something like Arrival, nothing too sad` | Freeform beats the menu |
| `pick from the top 50 tonight` | Smaller pool, just this once |
| `make it top 100 from now on` | Changes the default pool |
| `free stuff only from now on` | Only picks what's on your services or free |
| `watched it, 4/5, ending wrecked me` | Logs it, files it under Loved |
| `I've seen The Godfather, Heat and Alien` | Marks them watched so they're never picked |
| `help me mark what I've seen` | Walks the list 25 at a time |

## Your watched list

Plain Markdown at `~/.movie-picker/watchlist.md`. Edit it by hand any time, or symlink it into your
notes app (Obsidian, etc.) to keep it with everything else.

```markdown
## Settings
- Pool size: 200
- Country: US
- Services: Netflix, Max
- Free or on my services only: no

## Watched
- 2026-11-18 — Eternal Sunshine of the Spotless Mind (2004) — 5/5 — gutted me in the best way
```

## Rebuild or resize the catalog

The skill ships with the top 300, each tagged with tone, pace and subject. To go bigger or refresh it:

```bash
python3 ~/.claude/skills/movie-picker/scripts/build_catalog.py --top 1000
```

Standard library only. It downloads IMDb's public datasets (~250 MB, cached in
`~/.cache/movie-picker`) and ranks feature films with IMDb's weighted-rating formula:
`WR = v/(v+m)·R + m/(v+m)·C` with m = 25,000 votes. Mood tags carry over for films that stay on the list.

## Legal streaming only

It looks for legal sources only: subscriptions, free ad-supported services, public
broadcasters, and library apps like Kanopy and Hoopla. It won't point to piracy sites or torrents.
A lot of great films are free legally if you know where to look, and finding them is the point.

## Layout

```
.claude-plugin/          plugin + marketplace manifests
skills/movie-picker/
  SKILL.md               the skill
  references/catalog.md  ranked films with mood tags
  references/where-to-watch.md   free legal services by country
  scripts/build_catalog.py       rebuild the catalog at any size
  assets/watchlist-template.md   starting watched list
```

## Credits

Information courtesy of IMDb (https://www.imdb.com). Used with permission. The catalog is built from
IMDb's datasets, which are for personal and non-commercial use. Streaming availability comes
from live lookups (JustWatch and others) at pick time.

MIT licensed. See [LICENSE](LICENSE).
