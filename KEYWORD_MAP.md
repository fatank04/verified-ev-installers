# EVITP Installer Directory — Keyword Map & Page Architecture

Wedge: the only directory of *verified* EVITP-certified EV charger installers, organized state → metro → contractor, with commercial capability flags. Do not fight residential "near me" head terms (Yelp/Angi/Qmerit own them). Win on certification-qualified and commercial long-tail.

All SERP-weakness calls below come from live checks (2026-07-26): "evitp certified electrician texas" ranks evitp.org's static page plus two thin solo directories; "commercial ev charger installation companies" ranks zero directories; autocomplete confirms the query tree.

## Keyword map

### Tier 1 — Wedge (build first; weakest SERPs, buyer intent)

| Keyword pattern | Target page |
|---|---|
| evitp certified electrician [state] | /installers/[state] |
| evitp approved contractors [state] | /installers/[state] |
| evitp certified electrician near me | /installers (geo-detect) |
| evitp certified installer | home / /installers |
| ev charger installer [metro] | /installers/[state]/[metro] |
| ev charger installation electrician [metro] | /installers/[state]/[metro] |

### Tier 2 — Commercial B2B (the money leads; no directory ranks today)

| Keyword pattern | Target page |
|---|---|
| commercial ev charger installation companies | /commercial |
| commercial ev charger installation [state/metro] | /commercial/[state] |
| ev charging station contractors (near me) | /commercial |
| ev charger installation for business | /commercial |
| ev charging station companies | /commercial |
| apartment / condo / multifamily ev charger installation | /commercial/multifamily |

### Tier 3 — O&M / repair (phase 2; autocomplete-confirmed, near-zero competition)

| Keyword pattern | Target page |
|---|---|
| ev charging station maintenance companies | /maintenance |
| ev charger repair service near me | /maintenance/[state] |
| ev charging station service providers | /maintenance |
| ev charging station maintenance cost / checklist | /guides/charger-maintenance |

### Tier 4 — Supporting content (informational; feeds internal links + E-E-A-T)

| Keyword pattern | Target page |
|---|---|
| evitp certification requirements / cost / lookup | /guides/evitp-certification |
| does [state] require evitp | /guides/evitp-requirements-by-state |
| ev charger installation cost (home / commercial) | /guides/installation-cost |
| ev charger installation requirements / permit | /guides/installation-requirements |
| ev charger rebate [state] | incentive module ON state pages, not standalone (AmpUp/EnergySage own the head terms) |

### Explicit do-not-target
- "ev charger installers near me", "ev charger installation cost" head terms (Angi/Yelp/Home Depot/Lowe's/Qmerit).
- Standalone rebate/incentive hub (crowded; use as page enrichment only).
- India/UK/PH variants polluting autocomplete — US-only, hreflang not needed, just ignore.

## Page architecture

```
/
├── /installers/                      # national index + geo-detect
│   ├── /installers/[state]/          # 50 pages. EVITP-approved contractors, license-verify
│   │   └── /installers/[state]/[metro]/   # launch metros only (see rollout)
│   ├── /contractor/[slug]            # profile: EVITP status + verified date, state license #,
│   │                                 # service area, commercial|residential|both, NEVI/DCFC
│   │                                 # project experience, lead form
├── /commercial/                      # hub: list + how-to-choose editorial
│   ├── /commercial/[state]
│   └── /commercial/multifamily
├── /maintenance/                     # phase 2 (O&M vendors — same audience, reuse data model)
│   └── /maintenance/[state]
├── /guides/
│   ├── evitp-certification           # requirements, cost, renewal, lookup how-to
│   ├── evitp-requirements-by-state   # which states/programs mandate EVITP
│   ├── installation-cost
│   ├── installation-requirements
│   └── charger-maintenance
└── /for-installers                   # claim your listing / get verified (monetization)
```

## Data model (the moat)

Per contractor: name, slug, EVITP-approved status + verification date, state electrical license # (verified against state board), service states/metros, commercial/residential flag, DCFC/NEVI project experience (from award lists + L3 station deployment data), chargers brands worked with, contact, claimed y/n.

Sources: evitp.org state contractor lists (they publish; unusably formatted — structure is the value-add), state license board lookups, NEVI award announcements, AFDC station data + the National L3 scraper for who actually deployed what, Google Places for NAP enrichment.

## Google-safety guardrails
- No metro page ships with <3 verified contractors (thin-page rule).
- Every page shows verification dates + methodology link (first-party editorial oversight = the site-reputation-abuse defense).
- Schema: ItemList + LocalBusiness on lists, Organization on profiles.
- State pages get unique data blocks: EVITP mandate status, active incentives, contractor count, median quoted cost when known.

## Monetization ladder
1. Free listing (seeded from public data) → claim flow.
2. Verified/featured tier: monthly fee, badge, top placement.
3. Commercial lead routing: quote-request form on /commercial pages, sold per-lead.
4. Later: O&M vendor tier (phase 2 pages).

## Rollout order
1. 10 wedge states first: CA (EVITP mandated for state-funded projects), NY, NJ, IL, WA, MA, CO, MI, PA, TX. Mandate states convert best; PA/TX have the weakest SERPs checked.
2. Guides ship with wave 1 (E-E-A-T base).
3. Metros only after their state page ranks and ≥3 contractors verified.
4. /commercial hub in wave 1 — it is the revenue page.
5. /maintenance after first installer revenue.
