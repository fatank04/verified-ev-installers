"""Build a prioritized sell-side outreach list from the contractor data.

Produces data/outreach.csv, sorted so the highest-value contacts are contacted first:
metro contractors in the wedge states before rural ones, named contacts before
generic inboxes. Nothing is sent - this only prepares the list.
"""
import csv
import json
import pathlib
import re
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# Wave 1 = states where EVITP is referenced in funded programs, or where our
# SERP checks were weakest. These get contacted first.
WAVE1 = {"california", "new-york", "illinois", "washington", "pennsylvania",
         "texas", "ohio", "new-jersey", "massachusetts", "colorado", "michigan"}

GENERIC = re.compile(r"^(info|office|sales|admin|contact|estimating|service)@", re.I)


def main():
    rows = json.loads((DATA / "contractors.json").read_text())
    out = []
    for r in rows:
        email = (r.get("email") or "").strip()
        if not email or "@" not in email:
            continue
        # slug is derived at build time, not stored - mirror build.py's rule
        slug = r["evitp_listing_url"].rstrip("/").rsplit("/", 1)[-1]
        metro = r.get("metro") or ""
        in_metro = bool(metro) and not str(metro).startswith("(")
        named = bool(r.get("contact_person")) and not GENERIC.match(email)
        # Priority 1 = best: wave-1 state, in a metro we have a page for, named contact.
        score = (0 if r["state"] in WAVE1 else 1) + (0 if in_metro else 1) + (0 if named else 1)
        out.append({
            "priority": score + 1,
            "company": r["name"],
            "contact_person": r.get("contact_person", ""),
            "email": email,
            "phone": r.get("phone", ""),
            "state": r["state"],
            "metro": metro if in_metro else "",
            "listing_url": f"/contractor/{r['state']}/{slug}/",
            "website": r.get("website", ""),
        })

    out.sort(key=lambda x: (x["priority"], x["state"], x["company"].lower()))
    with open(DATA / "outreach.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)

    buckets = Counter(r["priority"] for r in out)
    print(f"{len(out)} contactable of {len(rows)} contractors "
          f"({len(out) * 100 // len(rows)}% have email)")
    for p in sorted(buckets):
        print(f"  priority {p}: {buckets[p]}")
    print(f"-> {DATA / 'outreach.csv'}")


if __name__ == "__main__":
    main()
