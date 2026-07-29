# Verified EV Installers

Static directory of EVITP-approved EV charger installation contractors, plus a tiny Flask
server for lead capture. 993 pages generated from `data/contractors.json`.

## Run locally

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
python3 build.py
.venv/bin/python server.py   # http://localhost:8018
```

## Deploy to Render (static site)

Deployed as a Render **static site**, not a web service. Static sites are free and do
not consume the workspace's free instance hours (web services do - that limit is what
blocked the original blueprint).

1. Render dashboard → New → Static Site → pick this repo.
2. Build command `python3 build.py`, publish directory `public`.
3. Set `FORM_ENDPOINT` (below) under Environment.

## Leads

The quote/report forms POST directly to whatever `FORM_ENDPOINT` is set to at build
time - no backend, nothing to keep running. FormSubmit needs no account:

```
FORM_ENDPOINT=https://formsubmit.co/ajax/you@example.com
```

Confirm the address once via the link in FormSubmit's first email, then submissions
arrive as email. Formspree, Web3Forms, or a Cloudflare Worker work the same way.

If `FORM_ENDPOINT` is unset, forms are replaced by the contractor's own phone/website
rather than silently dropping submissions.

`server.py` still exists for local preview and keeps the old `/api/lead` logging path,
but is not used by the Render static deploy.

## Staying current

**Automated (zero-cost):** `.github/workflows/refresh.yml` runs every Monday on GitHub
Actions. It re-scrapes all EVITP state lists, diffs against current data, and commits
only if something changed - which triggers Render's auto-deploy, so the site rebuilds
itself. New contractors appear; contractors that dropped off the EVITP list are removed.
A guard keeps a state's previous data if a scrape looks blocked/partial (new count <50%
of previous), so a WAF hiccup can never mass-delete listings. Every change is logged to
`data/changelog.md`. The "checked {month}" label across the site derives automatically
from the newest `scraped_at` in the data.

**User feedback:** every profile has "Report a change" (feeds the lead endpoint with
project type "Listing correction or closure report") and a claim flow at
`/for-installers/`. Reports arrive alongside leads in Render logs/email - act on them by
editing `data/contractors.json` or waiting for the next weekly diff to confirm.

**Manual run:**

```bash
python3 scripts/refresh.py           # scrape + guard + diff + changelog + metro reassign
python3 build.py                     # regenerate site
```

Change the domain in one place: `SITE_URL` in `build.py`.

## Files

- `build.py` - static site generator (stdlib only)
- `server.py` - serves `public/` + `POST /api/lead`
- `scripts/` - scraper + metro assignment
- `data/contractors.json` - 936 contractors, 10 states, with lat/lng + metro
- `KEYWORD_MAP.md` - SEO plan this build implements
