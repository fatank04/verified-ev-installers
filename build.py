"""Generate the static site into public/ from data/contractors.json.

Stdlib only. Run: python3 build.py
"""
import html
import json
import pathlib
import re
import shutil
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent
PUB = ROOT / "public"
import os

# Priority: explicit SITE_URL env -> Render's own URL (set automatically at build
# time on Render) -> local fallback. When a custom domain is added later, set
# SITE_URL in the Render dashboard and redeploy.
SITE_URL = (os.environ.get("SITE_URL")
            or os.environ.get("RENDER_EXTERNAL_URL")
            or "https://verified-ev-installers.onrender.com").rstrip("/")
SITE_NAME = "Verified EV Installers"


def _checked_label():
    """Derive the 'checked' label from the newest scraped_at in the data."""
    import datetime
    rows = json.loads((pathlib.Path(__file__).resolve().parent / "data" / "contractors.json").read_text())
    newest = max(r.get("scraped_at", "") for r in rows)
    try:
        return datetime.date.fromisoformat(newest).strftime("%B %Y")
    except ValueError:
        return newest


CHECKED = _checked_label()

# Where lead/quote requests are POSTed. Set as a build-time env var in Render so
# the address never lands in this public repo. FormSubmit needs no account:
#   FORM_ENDPOINT=https://formsubmit.co/ajax/you@example.com
# Any endpoint accepting a POST of form fields works (Formspree, Web3Forms, a Worker).
# When unset, forms fall back to showing the contractor's own contact details.
FORM_ENDPOINT = os.environ.get("FORM_ENDPOINT", "").strip()

_STATES = [
    ("alabama", "Alabama", "AL"), ("alaska", "Alaska", "AK"), ("arizona", "Arizona", "AZ"),
    ("arkansas", "Arkansas", "AR"), ("california", "California", "CA"),
    ("colorado", "Colorado", "CO"), ("connecticut", "Connecticut", "CT"),
    ("delaware", "Delaware", "DE"), ("florida", "Florida", "FL"), ("georgia", "Georgia", "GA"),
    ("hawaii", "Hawaii", "HI"), ("idaho", "Idaho", "ID"), ("illinois", "Illinois", "IL"),
    ("indiana", "Indiana", "IN"), ("iowa", "Iowa", "IA"), ("kansas", "Kansas", "KS"),
    ("kentucky", "Kentucky", "KY"), ("louisiana", "Louisiana", "LA"), ("maine", "Maine", "ME"),
    ("maryland", "Maryland", "MD"), ("massachusetts", "Massachusetts", "MA"),
    ("michigan", "Michigan", "MI"), ("minnesota", "Minnesota", "MN"),
    ("mississippi", "Mississippi", "MS"), ("missouri", "Missouri", "MO"),
    ("montana", "Montana", "MT"), ("nebraska", "Nebraska", "NE"), ("nevada", "Nevada", "NV"),
    ("new-hampshire", "New Hampshire", "NH"), ("new-jersey", "New Jersey", "NJ"),
    ("new-mexico", "New Mexico", "NM"), ("new-york", "New York", "NY"),
    ("north-carolina", "North Carolina", "NC"), ("north-dakota", "North Dakota", "ND"),
    ("ohio", "Ohio", "OH"), ("oklahoma", "Oklahoma", "OK"), ("oregon", "Oregon", "OR"),
    ("pennsylvania", "Pennsylvania", "PA"), ("rhode-island", "Rhode Island", "RI"),
    ("south-carolina", "South Carolina", "SC"), ("south-dakota", "South Dakota", "SD"),
    ("tennessee", "Tennessee", "TN"), ("texas", "Texas", "TX"), ("utah", "Utah", "UT"),
    ("vermont", "Vermont", "VT"), ("virginia", "Virginia", "VA"),
    ("washington", "Washington", "WA"), ("west-virginia", "West Virginia", "WV"),
    ("wisconsin", "Wisconsin", "WI"), ("wyoming", "Wyoming", "WY"),
    ("washington-dc", "Washington, DC", "DC"),
]
STATE_NAMES = {s: n for s, n, _ in _STATES}
STATE_ABBR = {s: a for s, _, a in _STATES}
# EVITP program notes per state. Factual, conservative wording only.
STATE_NOTES = {
    "california": "California requires EVITP certification on many state-funded charging projects (e.g. CALeVIP).",
    "new-york": "New York utility and state programs frequently reference EVITP training in funding requirements.",
    "illinois": "Illinois's Climate and Equitable Jobs Act references EVITP certification for publicly funded charger installs.",
    "washington": "Washington references EVITP certification in several publicly funded charging programs.",
}
NEVI_NOTE = ("Federal NEVI-funded charging projects require electricians to be EVITP-certified "
             "under the FHWA minimum standards (23 CFR 680.106).")

MIN_METRO = 3


def esc(s):
    return html.escape(str(s or ""), quote=True)


def slugify(s):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def load():
    rows = json.loads((ROOT / "data" / "contractors.json").read_text())
    aliases = {"newyork": "new-york", "newjersey": "new-jersey"}
    for r in rows:
        r["state"] = aliases.get(r["state"], r["state"])
        r["slug"] = r["evitp_listing_url"].rstrip("/").rsplit("/", 1)[-1]
    return rows


def page(title, desc, body, canonical, extra_head=""):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE_URL}{canonical}">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
{extra_head}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top">
  <a class="brand" href="/">Verified <span>EV</span> Installers</a>
  <nav>
    <a href="/installers/">Browse states</a>
    <a href="/commercial/">Commercial</a>
    <a href="/guides/">Guides</a>
    <a class="cta" href="/for-installers/">For installers</a>
  </nav>
</header>
<main id="main">
{body}
</main>
<footer>
  <div>
    <strong>{SITE_NAME}</strong>
    <p>Directory of contractors employing EVITP-certified electricians. Listings sourced from the
    public EVITP contractor lists, last checked {CHECKED}. We are not affiliated with EVITP.</p>
  </div>
  <div>
    <a href="/guides/methodology/">How we verify</a>
    <a href="/guides/evitp-certification/">What is EVITP?</a>
    <a href="/for-installers/">Claim your listing</a>
  </div>
</footer>
</body>
</html>"""


def fmt_phone(p):
    d = re.sub(r"\D", "", p or "")
    if len(d) == 11 and d.startswith("1"):
        d = d[1:]
    if len(d) == 10:
        return f"({d[:3]}) {d[3:6]}-{d[6:]}"
    return p or ""


def badge():
    return f'<span class="badge" title="Listed on the public EVITP contractor list, checked {CHECKED}">EVITP-Approved</span>'


def card(r, state_slug):
    loc = r["address"].replace(", USA", "")
    site = f'<a href="{esc(r["website"])}" rel="nofollow noopener" target="_blank">Website</a>' if r["website"] else ""
    phone_digits = re.sub(r"\D", "", r["phone"])
    phone = f'<a href="tel:{phone_digits}">{esc(fmt_phone(r["phone"]))}</a>' if r["phone"] else ""
    return f"""<article class="card">
  <div class="card-main">
    <h2 class="card-title"><a href="/contractor/{state_slug}/{esc(r['slug'])}/">{esc(r['name'])}</a></h2>
    <p class="loc">{esc(loc)}</p>
    <p class="badges">{badge()}{'<span class="metro-tag">' + esc(r.get('metro','')) + '</span>' if r.get('metro') and not str(r.get('metro')).startswith('(') else ''}</p>
  </div>
  <div class="card-side">
    {phone}
    {site}
    <a class="btn" href="/contractor/{state_slug}/{esc(r['slug'])}/#quote">Request a quote</a>
  </div>
</article>"""


def lead_form(subject, note="", fallback=""):
    if not FORM_ENDPOINT:
        # No form backend configured: never show a form that silently drops leads.
        return f"""<section class="lead" id="quote">
  <h2>Request a quote</h2>
  <p>{fallback or 'Contact the contractor directly using the details on this page.'}</p>
  <p class="fine">Online quote requests are being switched on shortly.</p>
</section>"""
    return f"""<form class="lead" id="quote" method="post" action="{esc(FORM_ENDPOINT)}" data-subject="{esc(subject)}">
  <h2>Request a quote</h2>
  {f'<p class="form-note">{esc(note)}</p>' if note else ''}
  <input type="hidden" name="subject" value="{esc(subject)}">
  <input type="hidden" name="_subject" value="Lead: {esc(subject)}">
  <input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off" aria-hidden="true">
  <label>Name <input name="name" required></label>
  <label>Email <input name="email" type="email" required></label>
  <label>Phone <input name="phone"></label>
  <label>ZIP code <input name="zip" required pattern="[0-9]{{5}}"></label>
  <label>Project type
    <select name="project_type">
      <option>Home Level 2 charger</option>
      <option>Commercial / workplace charging</option>
      <option>Multifamily / apartment</option>
      <option>DC fast charging</option>
      <option>Fleet</option>
      <option>Repair or maintenance</option>
      <option>Listing correction or closure report</option>
    </select>
  </label>
  <label>Details <textarea name="details" rows="4"></textarea></label>
  <button class="btn" type="submit">Send request</button>
  <p class="fine">We route your request to matching EVITP-approved contractors. No spam, no account needed.</p>
  <p class="sent" aria-live="polite" hidden>Request sent. A contractor will reach out shortly.</p>
</form>
<script>
document.querySelectorAll('form.lead').forEach(f => f.addEventListener('submit', async e => {{
  e.preventDefault();
  const btn = f.querySelector('button'); btn.disabled = true; btn.textContent = 'Sending…';
  try {{
    const res = await fetch(f.action, {{
      method: 'POST', body: new FormData(f), headers: {{'Accept': 'application/json'}}
    }});
    if (!res.ok) throw new Error();
    f.querySelectorAll('label,button').forEach(el => el.hidden = true);
    f.querySelector('.sent').hidden = false;
  }} catch {{ btn.disabled = false; btn.textContent = 'Send request'; alert('Could not send - please try again.'); }}
}}));
</script>"""


def faq_jsonld(qas):
    items = [{"@type": "Question", "name": q,
              "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qas]
    data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": items}
    return f'<script type="application/ld+json">{json.dumps(data)}</script>'


def write(path, content):
    out = PUB / path.lstrip("/")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content)


SEARCH_JS = """<div class="finder" role="search">
  <label for="finder-input" class="finder-label">Search by company, city, state, or ZIP</label>
  <input id="finder-input" type="search" placeholder="Try &quot;Columbus&quot;, &quot;90210&quot;, or a company name" autocomplete="off">
  <ul id="finder-results" hidden></ul>
</div>
<script>
(function () {
  var input = document.getElementById('finder-input');
  var list = document.getElementById('finder-results');
  var index = null;
  function load() {
    if (index) return Promise.resolve(index);
    return fetch('/search-index.json').then(function (r) { return r.json(); })
      .then(function (d) { index = d; return d; });
  }
  function render(items) {
    list.innerHTML = items.map(function (i) {
      return '<li><a href="' + i.u + '"><strong>' + i.n + '</strong><span>' + i.l + '</span></a></li>';
    }).join('');
    list.hidden = items.length === 0;
  }
  input.addEventListener('focus', load);
  input.addEventListener('input', function () {
    var q = input.value.trim().toLowerCase();
    if (q.length < 2) { list.hidden = true; return; }
    load().then(function (d) {
      var hits = [];
      for (var i = 0; i < d.length && hits.length < 8; i++) {
        if (d[i].n.toLowerCase().indexOf(q) !== -1 || d[i].l.toLowerCase().indexOf(q) !== -1) hits.push(d[i]);
      }
      render(hits);
    });
  });
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.finder')) list.hidden = true;
  });
})();
</script>"""


def build_search_index(rows, by_state):
    items = []
    for s in sorted(by_state):
        items.append({"n": f"{STATE_NAMES[s]} - all contractors", "l": f"{len(by_state[s])} listed", "u": f"/installers/{s}/"})
    metros = defaultdict(list)
    for r in rows:
        m = r.get("metro")
        if m and not str(m).startswith("("):
            metros[(r["state"], m)].append(r)
    for (s, m), v in sorted(metros.items()):
        if len(v) >= MIN_METRO:
            items.append({"n": f"{m}, {STATE_ABBR[s]}", "l": f"{len(v)} contractors", "u": f"/installers/{s}/{slugify(m)}/"})
    for r in rows:
        loc = r["address"].replace(", USA", "")
        items.append({"n": r["name"], "l": loc, "u": f"/contractor/{r['state']}/{r['slug']}/"})
    write("search-index.json", json.dumps(items, separators=(",", ":")))


def build_home(rows, by_state):
    states = "".join(
        f'<a class="state-tile" href="/installers/{s}/"><strong>{STATE_NAMES[s]}</strong>'
        f'<span>{len(by_state[s])} contractors</span></a>'
        for s in sorted(by_state, key=lambda s: -len(by_state[s]))
    )
    body = f"""
<section class="hero">
  <h1>Find EVITP-certified EV charger installers</h1>
  <p>{sum(len(v) for v in by_state.values())} contractors employing EVITP-certified electricians,
  across {len(by_state)} states. Sourced from the public EVITP contractor lists and re-checked
  every re-crawl - not a pay-to-play listing.</p>
  {SEARCH_JS}
  <div class="state-grid">{states}</div>
</section>
<section class="proof">
  <h2>Why certification matters</h2>
  <div class="cols">
    <div><h3>EVITP is the industry standard</h3><p>20 hours of training plus an exam, open only to
    state-licensed electricians. {NEVI_NOTE}</p></div>
    <div><h3>Listings are sourced, not sold</h3><p>Every contractor here appears on the public EVITP
    contractor list (checked {CHECKED}). Placement is never paid.</p></div>
    <div><h3>Commercial-grade coverage</h3><p>From home Level 2 installs to workplace, multifamily,
    and DC fast charging projects. <a href="/commercial/">Commercial? Start here.</a></p></div>
  </div>
</section>
<section class="band">
  <h2>Planning a commercial or multifamily project?</h2>
  <p>Tell us about it and we'll route it to qualified contractors in your state.</p>
  <a class="btn" href="/commercial/#quote">Request commercial quotes</a>
</section>"""
    write("index.html", page(
        f"{SITE_NAME} - Find EVITP-Certified EV Charger Installers",
        "Directory of contractors employing EVITP-certified electricians for EV charger installation. Browse by state and metro. Listings sourced from public EVITP lists.",
        body, "/"))


def build_state_index(by_state):
    lis = "".join(
        f'<a class="state-tile" href="/installers/{s}/"><strong>{STATE_NAMES[s]}</strong>'
        f'<span>{len(by_state[s])} contractors</span></a>'
        for s in sorted(by_state))
    body = f'<h1>Browse EVITP-approved contractors by state</h1>{SEARCH_JS}<div class="state-grid">{lis}</div>'
    write("installers/index.html", page(
        "Browse EV Charger Installers by State",
        "EVITP-approved EV charger installation contractors, organized by state and metro area.",
        body, "/installers/"))


def build_state(state, rows):
    name, abbr = STATE_NAMES[state], STATE_ABBR[state]
    metros = defaultdict(list)
    for r in rows:
        m = r.get("metro") or "(outside metros)"
        metros[m].append(r)
    viable = {m: v for m, v in metros.items() if not m.startswith("(") and len(v) >= MIN_METRO}
    chips = "".join(
        f'<a class="chip" href="/installers/{state}/{slugify(m)}/">{esc(m)} ({len(v)})</a>'
        for m, v in sorted(viable.items(), key=lambda kv: -len(kv[1])))
    note = STATE_NOTES.get(state, "")
    cards = "".join(card(r, state) for r in sorted(rows, key=lambda r: r["name"].lower()))
    qas = [
        (f"Do EV charger installers in {name} need EVITP certification?",
         (note + " " if note else "") + NEVI_NOTE + " For private residential work, requirements vary; EVITP is the recognized industry credential."),
        (f"How many EVITP-approved contractors are in {name}?",
         f"{len(rows)} contractors in {name} appear on the public EVITP contractor list as of {CHECKED}."),
        ("Are these listings paid placements?",
         "No. Every listing is sourced from the public EVITP contractor list. Placement cannot be bought."),
    ]
    faq_html = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in qas)
    body = f"""
<nav class="crumbs"><a href="/">Home</a> / <a href="/installers/">States</a> / {name}</nav>
<h1>EVITP-Certified EV Charger Installers in {name}</h1>
<p class="stats-line">{len(rows)} contractors · {len(viable)} metro areas · source list checked {CHECKED}</p>
{f'<p class="note">{esc(note)}</p>' if note else ''}
{f'<div class="chips">{chips}</div>' if chips else ''}
<div class="list">{cards}</div>
<section class="faq"><h2>Frequently asked questions</h2>{faq_html}</section>
{faq_jsonld(qas)}"""
    write(f"installers/{state}/index.html", page(
        f"EVITP-Certified EV Charger Installers in {name} ({len(rows)} Contractors)",
        f"Browse {len(rows)} EVITP-approved EV charger installation contractors in {name} ({abbr}), organized by metro. Sourced from public EVITP lists, checked {CHECKED}.",
        body, f"/installers/{state}/"))
    for m, v in viable.items():
        build_metro(state, m, v)


def build_metro(state, metro, rows):
    name = STATE_NAMES[state]
    mslug = slugify(metro)
    cards = "".join(card(r, state) for r in sorted(rows, key=lambda r: r["name"].lower()))
    body = f"""
<nav class="crumbs"><a href="/">Home</a> / <a href="/installers/{state}/">{name}</a> / {esc(metro)}</nav>
<h1>EV Charger Installers in {esc(metro)}, {STATE_ABBR[state]}</h1>
<p class="stats-line">{len(rows)} EVITP-approved contractors serving the {esc(metro)} area · checked {CHECKED}</p>
<div class="list">{cards}</div>
<p><a href="/installers/{state}/">See all {name} contractors →</a></p>"""
    write(f"installers/{state}/{mslug}/index.html", page(
        f"EV Charger Installers in {metro}, {STATE_ABBR[state]} - EVITP-Certified",
        f"{len(rows)} EVITP-approved EV charger installation contractors serving {metro}, {name}. Verified against public EVITP lists.",
        body, f"/installers/{state}/{mslug}/"))


def build_profile(r):
    state = r["state"]
    name = STATE_NAMES[state]
    loc = r["address"].replace(", USA", "")
    metro = r.get("metro") if r.get("metro") and not str(r.get("metro")).startswith("(") else None
    phone_digits = re.sub(r"\D", "", r["phone"])
    rows_html = "".join(
        f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in [
            ("Location", esc(loc)),
            ("Phone", f'<a href="tel:{phone_digits}">{esc(fmt_phone(r["phone"]))}</a>' if r["phone"] else "-"),
            ("Website", f'<a href="{esc(r["website"])}" rel="nofollow noopener" target="_blank">{esc(r["website"])}</a>' if r["website"] else "-"),
            ("Contact", esc(r["contact_person"]) or "-"),
            ("EVITP status", f"Listed on the public EVITP contractor list for {name} (checked {CHECKED})"),
            ("Service area", esc(metro + " and surrounding areas" if metro else f"{name} - contact for coverage")),
        ])
    ld = {"@context": "https://schema.org", "@type": "Electrician", "name": r["name"],
          "address": loc, "telephone": r["phone"] or None, "url": r["website"] or None}
    body = f"""
<nav class="crumbs"><a href="/">Home</a> / <a href="/installers/{state}/">{name}</a> / {esc(r['name'])}</nav>
<div class="profile">
  <div class="profile-main">
    <h1>{esc(r['name'])}</h1>
    <p class="badges">{badge()}{f'<span class="metro-tag">{esc(metro)}</span>' if metro else ''}</p>
    <table class="detail">{rows_html}</table>
    <p class="fine">Listing data sourced from the public EVITP contractor list. Is this your company?
    <a href="/for-installers/">Claim and verify this listing.</a>
    Out of date or closed? <a href="#quote" onclick="document.querySelector('[name=project_type]').value='Listing correction or closure report'">Report a change</a>.</p>
  </div>
  <aside class="profile-side">
    {lead_form(
        f"{r['name']} ({STATE_ABBR[state]})",
        fallback=(f'Call <a href="tel:{phone_digits}">{esc(fmt_phone(r["phone"]))}</a>'
                  if r["phone"] else "") +
                 (f' or visit their <a href="{esc(r["website"])}" rel="nofollow noopener" target="_blank">website</a>.'
                  if r["website"] else "."))}
  </aside>
</div>
<script type="application/ld+json">{json.dumps({k: v for k, v in ld.items() if v})}</script>"""
    write(f"contractor/{state}/{r['slug']}/index.html", page(
        f"{r['name']} - EVITP-Approved EV Charger Installer, {name}",
        f"{r['name']} is an EVITP-approved EV charger installation contractor in {loc}. Contact details and quote requests.",
        body, f"/contractor/{state}/{r['slug']}/"))


def build_commercial(by_state):
    links = "".join(f'<a class="chip" href="/installers/{s}/">{STATE_NAMES[s]}</a>' for s in sorted(by_state))
    body = f"""
<h1>Commercial EV Charger Installation Companies</h1>
<p>Workplace charging, multifamily retrofits, retail, fleet depots, and DC fast charging all
require licensed electrical contractors - and on federally funded (NEVI) projects, EVITP-certified
electricians are mandatory. Every contractor in this directory appears on the public EVITP
contractor list.</p>
<div class="cols">
  <div><h3>Scoped quotes, not cold calls</h3><p>Describe the project once. We route it to
  EVITP-approved contractors in your state.</p></div>
  <div><h3>Multifamily &amp; workplace</h3><p>Load calculations, panel upgrades, networked Level 2 -
  the work where certification and insurance actually get checked.</p></div>
  <div><h3>DC fast charging</h3><p>For DCFC and fleet projects, ask contractors about utility
  coordination and switchgear experience - and confirm EVITP certification of the crew.</p></div>
</div>
{lead_form("Commercial project", "Commercial requests are routed with priority.")}
<h2>Or browse contractors by state</h2>
<div class="chips">{links}</div>"""
    write("commercial/index.html", page(
        "Commercial EV Charger Installation Companies - Get Quotes",
        "Request quotes from EVITP-approved commercial EV charging contractors: workplace, multifamily, fleet, and DC fast charging projects.",
        body, "/commercial/"))


GUIDES = {
    "evitp-certification": (
        "EVITP Certification: Requirements, Cost, and How to Verify",
        "What EVITP certification is, what it costs, how long it lasts, and how to verify an electrician's certification.",
        """<h1>EVITP Certification: Requirements, Cost, and Verification</h1>
<p>The Electric Vehicle Infrastructure Training Program (EVITP) is the industry-standard
certification for electricians installing EV supply equipment.</p>
<h2>Requirements</h2>
<ul>
<li>Open only to state-licensed or certified electricians</li>
<li>20 hours of training plus a proctored exam</li>
<li>Course and exam cost: $275</li>
<li>Certification expires every 3 years; recertification required</li>
</ul>
<h2>Why it matters on funded projects</h2>
<p>Federal NEVI minimum standards (23 CFR 680.106) require EVITP certification for electricians
installing, operating, or maintaining NEVI-funded chargers. Several states reference EVITP in
their own funded programs, including California (CALeVIP) and Illinois (CEJA).</p>
<h2>How to verify</h2>
<p>EVITP operates a certification check on evitp.org for individual electricians, and publishes
per-state lists of contractors that employ certified electricians. This directory is built from
those public contractor lists and re-checked on every crawl.</p>"""),
    "evitp-requirements-by-state": (
        "Which States Require EVITP Certification?",
        "State-by-state overview of where EVITP certification is required or referenced for EV charger installation.",
        f"""<h1>Which States Require EVITP Certification?</h1>
<p>{NEVI_NOTE} That makes EVITP effectively required on NEVI corridor projects in every state.
Beyond NEVI, requirements vary:</p>
<ul>
<li><strong>California</strong> - EVITP required on many state-funded projects (e.g. CALeVIP).</li>
<li><strong>Illinois</strong> - The Climate and Equitable Jobs Act references EVITP for publicly funded installs.</li>
<li><strong>New York / Washington</strong> - EVITP training referenced in several utility and state funding programs.</li>
<li><strong>Texas, Florida, Georgia</strong> - No state mandate; EVITP remains the credential major
charging networks look for when hiring installation partners.</li>
</ul>
<p>For private residential installs, a state-licensed electrician is the baseline everywhere;
EVITP is the specialization signal.</p>"""),
    "installation-cost": (
        "EV Charger Installation Cost (Home and Commercial)",
        "Typical cost ranges for home Level 2 and commercial EV charger installation, and what drives them.",
        """<h1>EV Charger Installation Cost</h1>
<h2>Home Level 2</h2>
<p>National installer networks quote roughly $750-$2,000 installed for a typical Level 2 home
charger, driven by panel capacity, wire run length, and permitting. A panel upgrade adds
$1,500-$4,000+.</p>
<h2>Commercial</h2>
<p>Networked Level 2 stations typically run $2,500-$8,000+ per port installed depending on
switchgear, trenching, and make-ready work. DC fast charging is a different class of project -
$40,000-$150,000+ per stall including utility coordination.</p>
<h2>How to keep costs down</h2>
<ul>
<li>Get 2-3 quotes from certified contractors (that is what this directory is for)</li>
<li>Check utility make-ready and rebate programs before scoping</li>
<li>For commercial: right-size conduit and capacity for future ports now</li>
</ul>"""),
    "installation-requirements": (
        "EV Charger Installation Requirements and Permits",
        "Permits, electrical requirements, and code considerations for installing EV chargers.",
        """<h1>EV Charger Installation Requirements</h1>
<ul>
<li><strong>Permits:</strong> Level 2 installs generally require an electrical permit; most
jurisdictions require a licensed electrician to pull it.</li>
<li><strong>Circuit:</strong> A typical Level 2 charger needs a dedicated 40-60A 240V circuit
with capacity confirmed by load calculation (NEC Article 625 governs EVSE).</li>
<li><strong>Inspection:</strong> Permitted work is inspected before energization.</li>
<li><strong>Commercial:</strong> Adds ADA stall requirements, utility service review, and often
networked-charger requirements tied to incentive programs.</li>
</ul>
<p>An EVITP-certified electrician has been trained specifically on EVSE load calculation,
vehicle compatibility, and safety requirements.</p>"""),
    "methodology": (
        "How We Verify Listings",
        "Where this directory's data comes from and what the badges mean.",
        f"""<h1>How We Verify Listings</h1>
<p><strong>Source.</strong> Every listing comes from the public EVITP contractor lists published
at evitp.org, which reference contractors employing EVITP-certified electricians. Last full
check: {CHECKED}.</p>
<p><strong>What the badge means.</strong> "EVITP-Approved" means the contractor appeared on the
EVITP contractor list for its state on the check date. It is not a review score and cannot be
purchased.</p>
<p><strong>What we do not do.</strong> We do not accept payment for inclusion or placement.
Featured placement, if introduced, will be labeled.</p>
<p><strong>Roadmap.</strong> State electrical license cross-checks are in progress and will be
shown per listing with their own verification date.</p>
<p>We are an independent directory and are not affiliated with or endorsed by EVITP.</p>"""),
}


def build_guides():
    for slug, (title, desc, content) in GUIDES.items():
        body = f'<nav class="crumbs"><a href="/">Home</a> / <a href="/guides/">Guides</a> / {esc(title)}</nav><article class="guide">{content}</article>'
        write(f"guides/{slug}/index.html", page(title, desc, body, f"/guides/{slug}/"))
    lis = "".join(f'<li><a href="/guides/{s}/">{esc(t[0])}</a><p>{esc(t[1])}</p></li>' for s, t in GUIDES.items())
    write("guides/index.html", page(
        "Guides - EV Charger Installation and EVITP Certification",
        "Guides on EVITP certification, installation costs, permits, and how this directory verifies listings.",
        f'<h1>Guides</h1><ul class="guide-list">{lis}</ul>', "/guides/"))


def build_for_installers():
    body = f"""
<h1>For Installers: Claim Your Listing</h1>
<p>If your company appears in this directory, the listing was built from the public EVITP
contractor list. Claiming is free and lets you correct details, add service areas, and receive
quote requests directly.</p>
{lead_form("Installer claim request", "Use your company email so we can match you to the listing.")}
<p class="fine">Not listed but EVITP-approved? Send a note above - we re-check the source lists
on every crawl.</p>"""
    write("for-installers/index.html", page(
        "Claim Your Listing - For EV Charger Installers",
        "EVITP-approved contractors: claim your free listing, correct details, and receive quote requests.",
        body, "/for-installers/"))


def build_sitemap(paths):
    urls = "".join(f"<url><loc>{SITE_URL}{p}</loc></url>" for p in paths)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")


def main():
    if PUB.exists():
        shutil.rmtree(PUB)
    PUB.mkdir()
    shutil.copy(ROOT / "static" / "style.css", PUB / "style.css")
    rows = load()
    by_state = defaultdict(list)
    for r in rows:
        by_state[r["state"]].append(r)

    paths = ["/", "/installers/", "/commercial/", "/for-installers/", "/guides/"]
    build_search_index(rows, by_state)
    build_home(rows, by_state)
    build_state_index(by_state)
    for s, v in by_state.items():
        build_state(s, v)
        paths.append(f"/installers/{s}/")
        metros = defaultdict(list)
        for r in v:
            m = r.get("metro") or ""
            if m and not m.startswith("("):
                metros[m].append(r)
        paths += [f"/installers/{s}/{slugify(m)}/" for m, mv in metros.items() if len(mv) >= MIN_METRO]
    for r in rows:
        build_profile(r)
        paths.append(f"/contractor/{r['state']}/{r['slug']}/")
    build_commercial(by_state)
    build_guides()
    paths += [f"/guides/{s}/" for s in GUIDES]
    build_for_installers()
    build_sitemap(sorted(set(paths)))
    n_pages = sum(1 for _ in PUB.rglob("index.html"))
    print(f"Built {n_pages} pages -> {PUB}")


if __name__ == "__main__":
    main()
