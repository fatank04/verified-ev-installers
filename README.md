# Verified EV Installers

Static directory of EVITP-approved EV charger installation contractors, plus a tiny Flask
server for lead capture. 993 pages generated from `data/contractors.json`.

## Run locally

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
python3 build.py
.venv/bin/python server.py   # http://localhost:8018
```

## Deploy to Render

1. Push this folder to a GitHub repo.
2. Render dashboard → New → Blueprint → pick the repo. `render.yaml` does the rest
   (build = `pip install + python build.py`, start = `gunicorn server:app`, free plan).
3. Add the custom domain in Render settings once registered.

## Leads

Every submission is written to Render logs (`LEAD {...}` lines) and `leads.jsonl`.
To also get email, set env vars in the Render dashboard:
`LEAD_EMAIL_TO`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`
(a Google Workspace app password works). Note: `leads.jsonl` is ephemeral on the free
plan - Render logs are the durable record until email is configured.

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
