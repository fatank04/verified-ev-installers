"""Scrape EVITP-approved contractor listings from evitp.org state pages.

Public data; one request per state with a polite delay. Output: data/contractors.json
and data/contractors.csv keyed by state.
"""
import csv
import html as htmlmod
import json
import pathlib
import re
import sys
import time
import urllib.request

# evitp.org slug -> canonical state key used across the project
STATES = {
    "alabama": "alabama", "alaska": "alaska", "arizona": "arizona",
    "arkansas": "arkansas", "california": "california", "colorado": "colorado",
    "connecticut": "connecticut", "delaware": "delaware", "florida": "florida",
    "georgia": "georgia", "hawaii": "hawaii", "idaho": "idaho",
    "illinois": "illinois", "indiana": "indiana", "iowa": "iowa",
    "kansas": "kansas", "kentucky": "kentucky", "louisiana": "louisiana",
    "maine": "maine", "maryland": "maryland", "massachusetts": "massachusetts",
    "michigan": "michigan", "minnesota": "minnesota", "mississippi": "mississippi",
    "missouri": "missouri", "montana": "montana", "nebraska": "nebraska",
    "nevada": "nevada", "newhampshire": "new-hampshire", "newjersey": "new-jersey",
    "newmexico": "new-mexico", "newyork": "new-york",
    "northcarolina": "north-carolina", "northdakota": "north-dakota",
    "ohio": "ohio", "oklahoma": "oklahoma", "oregon": "oregon",
    "pennsylvania": "pennsylvania", "rhodeisland": "rhode-island",
    "southcarolina": "south-carolina", "southdakota": "south-dakota",
    "tennessee": "tennessee", "texas": "texas", "utah": "utah",
    "vermont": "vermont", "virginia": "virginia", "washington": "washington",
    "westvirginia": "west-virginia", "wisconsin": "wisconsin",
    "wyoming": "wyoming", "washingtondc": "washington-dc",
}

PACE_SECONDS = 3      # evitp.org WAF blocks request bursts
RETRIES = 3
BACKOFF_SECONDS = 45

OUT_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"

PHONE_RE = re.compile(r"tel:([\d\-\+\(\) \.]+)")
MAIL_RE = re.compile(r"mailto:([^\"'?]+)")
URL_RE = re.compile(
    r'class="sabai-directory-contact-website"[^>]*>.*?<a href="([^"]+)"', re.S
)
ADDR_RE = re.compile(r'class="sabai-directory-location[^"]*"[^>]*>(.*?)</div>', re.S)
CONTACT_RE = re.compile(r"Contact:\s*([^<]+)")
TITLE_RE = re.compile(
    r'<a href="(https://evitp\.org/[^"]+/listing/[^"]+)"[^>]*class="[^"]*sabai-entity-permalink[^"]*"[^>]*>(.*?)</a>',
    re.S,
)


def fetch(url):
    last = None
    for attempt in range(RETRIES):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            last = e
            if e.code == 404:
                raise
            # 406/429/5xx: WAF or rate limit - back off and retry
            time.sleep(BACKOFF_SECONDS * (attempt + 1))
    raise last


def strip_tags(s):
    return htmlmod.unescape(re.sub(r"<[^>]+>", " ", s)).strip()


COORD_RE = re.compile(
    r'\{"lat":([\d.\-]+),"lng":([\d.\-]+),"trigger":"#sabai-entity-content-(\d+)'
)


def parse_state(page, state):
    coords = {eid: (float(lat), float(lng)) for lat, lng, eid in COORD_RE.findall(page)}
    # Listings live in the list container; split on entity content blocks,
    # keeping each block's entity id so we can join map coordinates.
    parts = re.split(r'<div id="sabai-entity-content-(\d+)"', page)
    blocks = [(parts[i], parts[i + 1]) for i in range(1, len(parts) - 1, 2)]
    seen = {}
    for eid, block in blocks:
        m = TITLE_RE.search(block)
        if not m:
            continue
        permalink, raw_name = m.group(1), strip_tags(m.group(2))
        if not raw_name or permalink in seen:
            continue
        addr_m = ADDR_RE.search(block)
        phone_m = PHONE_RE.search(block)
        mail_m = MAIL_RE.search(block)
        url_m = URL_RE.search(block)
        contact_m = CONTACT_RE.search(strip_tags(block))
        lat, lng = coords.get(eid, (None, None))
        seen[permalink] = {
            "lat": lat,
            "lng": lng,
            "state": state,
            "name": raw_name,
            "address": strip_tags(addr_m.group(1)) if addr_m else "",
            "phone": phone_m.group(1).strip() if phone_m else "",
            "email": htmlmod.unescape(mail_m.group(1)).strip() if mail_m else "",
            "website": url_m.group(1).strip() if url_m else "",
            "contact_person": contact_m.group(1).strip() if contact_m else "",
            "evitp_listing_url": permalink,
            "source": "evitp.org",
            "scraped_at": time.strftime("%Y-%m-%d"),
        }
    return list(seen.values())


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    all_rows = []
    for slug, state in STATES.items():
        url = f"https://evitp.org/{slug}"
        try:
            page = fetch(url)
        except Exception as e:
            print(f"[{state}] FAILED {url}: {e}", file=sys.stderr)
            continue
        rows = parse_state(page, state)
        print(f"[{state}] {len(rows)} contractors", flush=True)
        all_rows.extend(rows)
        time.sleep(PACE_SECONDS)

    (OUT_DIR / "contractors.json").write_text(json.dumps(all_rows, indent=2))
    with open(OUT_DIR / "contractors.csv", "w", newline="") as f:
        if all_rows:
            w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
            w.writeheader()
            w.writerows(all_rows)
    print(f"TOTAL: {len(all_rows)} contractors -> {OUT_DIR}")


if __name__ == "__main__":
    main()
