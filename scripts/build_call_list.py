"""Pick 20 validation calls: priority-1 contractors, spread across states so one
regional quirk cannot skew the answer. Writes data/call_list.csv with blank
answer columns to fill during the call.
"""
import csv
import json
import pathlib
import re
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
TARGET = 20
PER_STATE_CAP = 3

ANSWER_COLUMNS = [
    "reached",            # y / n / voicemail
    "q1_where_work_comes_from",
    "q2_pay_250_commercial",   # yes / no / maybe + any number they counter with
    "q3_hosts_unsure_feasibility",  # never / sometimes / often
    "q4_lost_job_to_feasibility",   # y / n + detail
    "q5_join_waitlist",   # y / n
    "notes",
]


def fmt_phone(p):
    d = re.sub(r"\D", "", p or "")
    if len(d) == 11 and d.startswith("1"):
        d = d[1:]
    return f"({d[:3]}) {d[3:6]}-{d[6:]}" if len(d) == 10 else (p or "")


def main():
    rows = json.loads((DATA / "contractors.json").read_text())
    by_state = defaultdict(list)
    for r in rows:
        metro = r.get("metro") or ""
        if not r.get("phone") or not r.get("contact_person"):
            continue
        if not metro or str(metro).startswith("("):
            continue
        by_state[r["state"]].append(r)

    # Round-robin across states, biggest markets first, capped per state.
    order = sorted(by_state, key=lambda s: -len(by_state[s]))
    picked, seen = [], defaultdict(int)
    while len(picked) < TARGET:
        added = False
        for s in order:
            if len(picked) >= TARGET or seen[s] >= PER_STATE_CAP:
                continue
            pool = by_state[s]
            if seen[s] < len(pool):
                picked.append(pool[seen[s]])
                seen[s] += 1
                added = True
        if not added:
            break

    out = []
    for r in picked:
        out.append({
            "company": r["name"],
            "contact": r.get("contact_person", ""),
            "phone": fmt_phone(r.get("phone", "")),
            "state": r["state"],
            "metro": r.get("metro", ""),
            **{c: "" for c in ANSWER_COLUMNS},
        })

    with open(DATA / "call_list.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    states = sorted({r["state"] for r in out})
    print(f"{len(out)} calls across {len(states)} states: {', '.join(states)}")
    print(f"-> {DATA / 'call_list.csv'}")


if __name__ == "__main__":
    main()
