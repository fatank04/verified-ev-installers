"""Weekly refresh: re-scrape EVITP lists, diff against current data, guard against
transient scrape failures, and log changes.

- New contractors are added.
- Contractors that dropped off the EVITP list are removed (they no longer verify).
- Guard: if a state's new count falls below 50% of its previous count, the old rows
  for that state are kept and the state is flagged - a partial/blocked scrape must
  never mass-delete listings.
- Appends a dated summary to data/changelog.md.

Run: python3 scripts/refresh.py   (from repo root; exits 0 always, prints CHANGED=yes/no)
"""
import json
import pathlib
import subprocess
import sys
import time
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contractors.json"
CHANGELOG = ROOT / "data" / "changelog.md"
GUARD_RATIO = 0.5


def by_key(rows):
    return {r["evitp_listing_url"]: r for r in rows}


def main():
    old_rows = json.loads(DATA.read_text()) if DATA.exists() else []
    old_by_state = Counter(r["state"] for r in old_rows)

    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "scrape_evitp.py")])
    if r.returncode != 0:
        print("Scrape failed entirely; keeping existing data. CHANGED=no")
        return
    new_rows = json.loads(DATA.read_text())
    new_by_state = Counter(r["state"] for r in new_rows)

    # Guard: restore any state that shrank suspiciously (blocked/partial scrape).
    flagged = [s for s in old_by_state
               if new_by_state.get(s, 0) < old_by_state[s] * GUARD_RATIO]
    if flagged:
        keep = [r for r in old_rows if r["state"] in flagged]
        new_rows = [r for r in new_rows if r["state"] not in flagged] + keep
        print(f"GUARD: kept previous data for {flagged} (suspicious shrink)")

    old_keys, new_keys = by_key(old_rows), by_key(new_rows)
    added = [new_keys[k]["name"] + f" ({new_keys[k]['state']})" for k in new_keys.keys() - old_keys.keys()]
    removed = [old_keys[k]["name"] + f" ({old_keys[k]['state']})" for k in old_keys.keys() - new_keys.keys()]

    DATA.write_text(json.dumps(new_rows, indent=2))
    subprocess.run([sys.executable, str(ROOT / "scripts" / "metro_breakdown.py")], check=True)

    changed = bool(added or removed)
    if changed or flagged:
        date = time.strftime("%Y-%m-%d")
        entry = [f"\n## {date}", f"- Total: {len(new_rows)} contractors"]
        if added:
            entry.append(f"- Added ({len(added)}): " + "; ".join(sorted(added)))
        if removed:
            entry.append(f"- Removed - no longer on EVITP list ({len(removed)}): " + "; ".join(sorted(removed)))
        if flagged:
            entry.append(f"- GUARD kept previous data for: {', '.join(flagged)}")
        header = "" if CHANGELOG.exists() else "# Data changelog\n"
        with open(CHANGELOG, "a") as f:
            f.write(header + "\n".join(entry) + "\n")
    print(f"Added {len(added)}, removed {len(removed)}. CHANGED={'yes' if changed else 'no'}")


if __name__ == "__main__":
    main()
