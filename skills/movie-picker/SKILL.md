---
name: movie-picker
description: Pick tonight's movie. Asks a few quick questions (mood, who's watching, time, era), picks one film from the top N of a ranked IMDb catalog (default top 200, changeable), skips everything already watched, checks where it's streaming — your subscriptions, free legal options, rent/buy — and keeps a running watched list with ratings. Use whenever the user asks what to watch, wants a movie recommendation, says "pick a movie", "movie night", "what should I watch tonight", "something like X", asks where a film is streaming, or reports having watched, liked, or hated a film (so the watched list gets updated). Not for TV series, film trivia, or building movie apps.
---

# Movie Picker

The user wants the agent to do the deciding: ask a few questions, pick **one** film they haven't
watched, tell them exactly where they can watch it, and keep their watched list current. The list
is what makes this better over time — it stops repeats and teaches the picks their taste.

## Files

- **Catalog:** `references/catalog.md` (this skill folder) — IMDb-ranked films with rank, runtime,
  rating, genres, tones, pace, subjects. The only pool to pick from. Read it every time.
- **Free services guide:** `references/where-to-watch.md` — legal free options by country.
- **Watched list:** `~/.movie-picker/watchlist.md`. If it doesn't exist, create it by copying
  `assets/watchlist-template.md`. It may be a symlink (e.g. into a notes vault) — follow it and
  edit the target.

## 1. Load context

Read the catalog and the watched list. From the list's **Settings**, note pool size, country,
services, and preferences. Anything under **Watched** or **Up next** is off the table unless the
user asks for a rewatch. **Loved**, **Disliked**, and **Avoid** steer the pick.

**First run** (Country or Services blank): before anything else, ask in one line — "Quick one-time
setup: which country are you in, and which streaming services do you have?" — and save the answer
to Settings. This is what makes the where-to-watch step useful.

## 2. Ask the questions

Always ask before picking — that's the experience. Ask them together in one round, not one at a
time. Use the `AskUserQuestion` tool when available (tapping a choice beats typing); otherwise ask
in one short message.

Skip any question the request already answers:

1. **Mood** — Gripping/tense · Funny/light · Emotional · Mind-bending · Big epic
2. **Who's watching** — Solo · Partner · Friends · Family with kids
3. **Time** — Under 2 hours · Up to 2.5 hours · Doesn't matter
4. **Era** — Classic (pre-1980) · 1980–2005 · Modern (2005+) · Any

Freeform answers ("like Interstellar", "nothing too sad", "free tonight only") outrank the menu.
If the request already covers everything — or says "just pick" — skip straight to choosing.

## 3. Pick from the pool

**Pool size** = the `Pool size` setting (default 200): only films ranked at or above it are
eligible. It changes two ways:
- **For tonight** — "top 50", "from the top 100": use it for this pick, leave the setting alone.
- **From now on** — "make it top 100": update the setting.

The catalog may hold fewer films than asked for. If so, say how many it has and offer to rebuild
it bigger with `python3 scripts/build_catalog.py --top <N>` (downloads ~250 MB of IMDb's public
data the first time; confirm before running).

Filter: drop watched films, anything over the time limit, anything clashing with **Avoid**, and —
with kids watching — anything unsuitable (many top-ranked films are R-rated and violent; check).
Then shortlist the 3–4 best fits for the mood and pick one. Prefer:
- Films resembling **Loved** picks and unlike **Disliked** ones.
- A less obvious film over the top-10 default, unless the top-10 film genuinely fits best.
- If `Free or on my services only` is `yes`, check availability for the shortlist (step 4) and
  pick the best one that's actually watchable at no extra cost.

If nothing in the pool fits, say so and name the constraint to loosen (a bigger pool is usually
easiest). Don't pick from outside the pool without asking.

## 4. Find where to watch

Streaming catalogs change every month and differ by country, so never state availability from
memory as fact. If web search or fetch is available, look it up for the user's country:

1. Search for the film on JustWatch (`justwatch.com/<country code>/search?q=<title>`, or search
   `"<Title> <year>" where to watch JustWatch <country>`). Cross-check with one more source
   (Reelgood, the service's own page) if results look stale or thin.
2. Sort what you find into:
   - **On your services** — subscriptions the user listed in Settings
   - **Free** — legal free options: ad-supported services, public broadcasters, library services
     like Kanopy and Hoopla. See `references/where-to-watch.md`.
   - **Other subscriptions** — services the user doesn't have
   - **Rent / buy** — with the price when shown

Only point to licensed, legal sources. Never suggest piracy sites, torrents, or unofficial
streams — if asked, say plainly that this skill sticks to legal options, and show the best free
or cheapest legal way instead. Plenty of great films are free legally; finding those is the win.

If you can't look anything up, give the JustWatch search link and say availability wasn't checked.

## 5. Deliver

Keep it tight:

```
🎬 **Tonight: <Title> (<year>)** — <runtime> · #<rank> · IMDb <rating>

<2–3 sentences on why it fits their answers. Reference a Loved film if relevant.
No spoilers past the first act.>

📺 Where to watch (<country>, checked <date>)
- ✅ Your services: <service> | none
- 🆓 Free: <service (with ads / library card)> | none found
- 💵 Rent/buy: <store ~price> | —

If that's not it:
- <Backup 1 (year)> — <one line: how it's different — lighter, shorter, older…> · <where, if known>
- <Backup 2 (year)> — <one line> · <where, if known>
```

Leave out lines that are empty, and leave out the 📺 block if nothing could be checked (put the
JustWatch link instead). Backups come from the pool and pull in different directions. End with:
"Tell me when you've watched it and how it was."

## 6. Keep the watched list

Edit `~/.movie-picker/watchlist.md` in place after every interaction:

- **After a pick:** add it to **Up next** as `- Title (year) — picked YYYY-MM-DD — <mood>`.
- **When the user watched something:** move it from Up next (or add it fresh) to **Watched** as
  `- YYYY-MM-DD — Title (year) — <rating>/5 — <a few words on why>`. No rating given? Ask for a
  quick 1–5. Ratings 4–5 also go under **Loved**, 1–2 under **Disliked**, with the reason — the
  reason is what improves the next pick.
- **Films seen in the past:** add to **Watched** with `seen before` as the date. When the user
  wants to bulk-mark, offer to walk the pool in chunks of 25 ("which of these have you seen?").
- **Skipped or rejected picks:** remove them from Up next.
- **Settings changes** (pool size, country, services, free-only): update the Settings lines.

Use today's real date. Keep edits small; don't rewrite or reorder the rest of the file.
