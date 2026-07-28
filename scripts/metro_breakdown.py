"""Assign contractors to the nearest major metro (within 50 mi) and report
which metro pages clear the 3-contractor launch floor."""
import json
import math
import pathlib
from collections import Counter, defaultdict

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"

METROS = {
    # state: [(metro name, lat, lng)]
    "california": [
        ("Los Angeles", 34.05, -118.24), ("San Francisco Bay Area", 37.63, -122.10),
        ("San Diego", 32.72, -117.16), ("Sacramento", 38.58, -121.49),
        ("Fresno", 36.74, -119.79), ("Inland Empire", 34.05, -117.30),
    ],
    "texas": [
        ("Houston", 29.76, -95.37), ("Dallas-Fort Worth", 32.78, -96.90),
        ("Austin", 30.27, -97.74), ("San Antonio", 29.42, -98.49),
        ("El Paso", 31.76, -106.49),
    ],
    "new-york": [
        ("New York City", 40.71, -74.01), ("Long Island", 40.79, -73.13),
        ("Albany", 42.65, -73.75), ("Buffalo", 42.89, -78.88),
        ("Rochester", 43.16, -77.61), ("Syracuse", 43.05, -76.15),
    ],
    "new-jersey": [
        ("North Jersey", 40.74, -74.17), ("Central Jersey", 40.35, -74.42),
        ("South Jersey", 39.93, -75.03),
    ],
    "illinois": [
        ("Chicago", 41.88, -87.63), ("Springfield", 39.78, -89.65),
        ("Peoria", 40.69, -89.59), ("Rockford", 42.27, -89.09),
    ],
    "washington": [
        ("Seattle-Tacoma", 47.51, -122.27), ("Spokane", 47.66, -117.43),
        ("Vancouver WA", 45.64, -122.66), ("Tri-Cities", 46.23, -119.22),
    ],
    "massachusetts": [
        ("Boston", 42.36, -71.06), ("Worcester", 42.26, -71.80),
        ("Springfield MA", 42.10, -72.59),
    ],
    "colorado": [
        ("Denver", 39.74, -104.99), ("Colorado Springs", 38.83, -104.82),
        ("Fort Collins", 40.59, -105.08),
    ],
    "michigan": [
        ("Detroit", 42.33, -83.05), ("Grand Rapids", 42.96, -85.66),
        ("Lansing", 42.73, -84.56), ("Flint-Saginaw", 43.20, -83.80),
    ],
    "pennsylvania": [
        ("Philadelphia", 39.95, -75.17), ("Pittsburgh", 40.44, -80.00),
        ("Harrisburg", 40.27, -76.88), ("Allentown", 40.60, -75.47),
        ("Scranton", 41.41, -75.66),
    ],
    "arizona": [("Phoenix", 33.45, -112.07), ("Tucson", 32.22, -110.97)],
    "florida": [
        ("Miami-Fort Lauderdale", 26.01, -80.23), ("Orlando", 28.54, -81.38),
        ("Tampa", 27.95, -82.46), ("Jacksonville", 30.33, -81.66),
    ],
    "georgia": [("Atlanta", 33.75, -84.39), ("Savannah", 32.08, -81.09)],
    "north-carolina": [
        ("Charlotte", 35.23, -80.84), ("Raleigh-Durham", 35.85, -78.70),
        ("Greensboro", 36.07, -79.79),
    ],
    "ohio": [
        ("Columbus", 39.96, -83.00), ("Cleveland", 41.50, -81.69),
        ("Cincinnati", 39.10, -84.51), ("Dayton", 39.76, -84.19),
        ("Toledo", 41.65, -83.54),
    ],
    "oregon": [("Portland", 45.52, -122.68), ("Eugene", 44.05, -123.09)],
    "nevada": [("Las Vegas", 36.17, -115.14), ("Reno", 39.53, -119.81)],
    "minnesota": [("Minneapolis-St. Paul", 44.96, -93.20)],
    "maryland": [("Baltimore", 39.29, -76.61), ("DC Suburbs MD", 39.00, -77.10)],
    "virginia": [
        ("Northern Virginia", 38.85, -77.30), ("Richmond", 37.54, -77.44),
        ("Hampton Roads", 36.85, -76.29),
    ],
    "washington-dc": [("Washington, DC", 38.91, -77.04)],
    "connecticut": [("Hartford", 41.76, -72.68), ("New Haven-Bridgeport", 41.24, -73.06)],
    "rhode-island": [("Providence", 41.82, -71.41)],
    "new-hampshire": [("Manchester-Nashua", 42.94, -71.48)],
    "tennessee": [
        ("Nashville", 36.16, -86.78), ("Memphis", 35.15, -90.05),
        ("Knoxville", 35.96, -83.92), ("Chattanooga", 35.05, -85.31),
    ],
    "missouri": [("St. Louis", 38.63, -90.20), ("Kansas City", 39.10, -94.58)],
    "wisconsin": [("Milwaukee", 43.04, -87.91), ("Madison", 43.07, -89.40)],
    "indiana": [("Indianapolis", 39.77, -86.16)],
    "kentucky": [("Louisville", 38.25, -85.76), ("Lexington", 38.04, -84.50)],
    "louisiana": [("New Orleans", 29.95, -90.07), ("Baton Rouge", 30.45, -91.15)],
    "oklahoma": [("Oklahoma City", 35.47, -97.52), ("Tulsa", 36.15, -95.99)],
    "utah": [("Salt Lake City", 40.76, -111.89)],
    "new-mexico": [("Albuquerque", 35.08, -106.65)],
    "iowa": [("Des Moines", 41.59, -93.62), ("Cedar Rapids", 41.98, -91.67)],
    "kansas": [("Wichita", 37.69, -97.34), ("Kansas City KS", 39.11, -94.63)],
    "alabama": [("Birmingham", 33.52, -86.80), ("Huntsville", 34.73, -86.59)],
    "south-carolina": [
        ("Charleston", 32.78, -79.93), ("Columbia", 34.00, -81.03),
        ("Greenville", 34.85, -82.40),
    ],
    "arkansas": [("Little Rock", 34.75, -92.29)],
    "nebraska": [("Omaha", 41.26, -95.93)],
    "idaho": [("Boise", 43.62, -116.21)],
    "mississippi": [("Jackson", 32.30, -90.18)],
    "maine": [("Portland ME", 43.66, -70.26)],
    "vermont": [("Burlington", 44.48, -73.21)],
    "montana": [("Billings", 45.78, -108.50)],
    "north-dakota": [("Fargo", 46.88, -96.79)],
    "south-dakota": [("Sioux Falls", 43.55, -96.73)],
    "west-virginia": [("Charleston WV", 38.35, -81.63)],
    "wyoming": [("Cheyenne", 41.14, -104.82)],
    "delaware": [("Wilmington", 39.75, -75.55)],
    "alaska": [("Anchorage", 61.22, -149.90)],
    "hawaii": [("Honolulu", 21.31, -157.86)],
}

RADIUS_MI = 50


def haversine(lat1, lng1, lat2, lng2):
    r = 3958.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def main():
    rows = json.loads((DATA / "contractors.json").read_text())
    aliases = {"newyork": "new-york", "newjersey": "new-jersey"}
    for r in rows:
        r["state"] = aliases.get(r["state"], r["state"])
    counts = defaultdict(Counter)
    no_coords = Counter()
    for r in rows:
        state = r["state"]
        if r.get("lat") is None:
            no_coords[state] += 1
            counts[state]["(no coords)"] += 1
            continue
        best, best_d = None, None
        for name, mlat, mlng in METROS.get(state, []):
            d = haversine(r["lat"], r["lng"], mlat, mlng)
            if best_d is None or d < best_d:
                best, best_d = name, d
        metro = best if best_d is not None and best_d <= RADIUS_MI else "(outside metros)"
        counts[state][metro] += 1
        r["metro"] = metro

    (DATA / "contractors.json").write_text(json.dumps(rows, indent=2))

    viable, thin = [], []
    for state in METROS:
        print(f"\n{state.upper()} ({sum(counts[state].values())})")
        for metro, n in counts[state].most_common():
            flag = "OK " if n >= 3 and not metro.startswith("(") else "   "
            print(f"  {flag}{metro}: {n}")
            if not metro.startswith("("):
                (viable if n >= 3 else thin).append((state, metro, n))
    print(f"\nViable metro pages (>=3 contractors): {len(viable)}")
    print(f"Thin metros (defer): {len(thin)}")


if __name__ == "__main__":
    main()
