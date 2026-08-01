# 20 validation calls — script and scoring

Two afternoons. Tests both theses at once: will contractors pay for leads (directory
revenue), and do site hosts arrive unable to answer feasibility (SiteLitmus funnel).

List: `data/call_list.csv` — 20 priority-1 contractors, one per state, named contact and
direct phone. Fill the answer columns during the call.

## Opening (say it fast, they are on a job site)

> Hi {contact}, this is Ankur — I'm not selling anything. I built a directory of
> EVITP-certified installers and {company} is already listed, free. I'm calling five minutes'
> worth of questions to make sure I build the right thing. Got a minute?

If no: *"No problem — is there a better time?"* Log and move on. Expect 6-9 pickups out of 20.

## The five questions

**Q1. Where does your commercial EV charging work come from today?**
*Listening for:* GCs, existing electrical clients, Qmerit, CPOs, word of mouth, inbound search.
This is the single most informative answer on the call. If nobody says search or directories,
the SEO thesis is weak regardless of what they say about paying.

**Q2. If I sent you a commercial lead — site type, port count, timeline, verified
decision-maker, exclusive to you — would $250 be worth it?**
*Listening for:* a number, not a yes. "Yes" is polite. "I'd pay $150" is real. "I don't buy
leads" is the most valuable answer you can get.

**Q3. When a property owner calls you about charging, how often do they already know their
panel capacity, utility situation, and rough cost?**
*Listening for:* never / sometimes / often. "Never" is the SiteLitmus signal.

**Q4. Do you ever lose or walk away from projects because the owner hadn't done that
homework first?**
*Listening for:* a story. If they describe wasted site visits on projects that died, that is
SiteLitmus's exact value proposition, told to you by the customer.

**Q5. Want me to put you on the list for leads in {metro}? Free, and the first ones are free
so you can judge them.**
*This is the close.* Signups here count toward the Phase 0 gate.

## Scoring — decide from the data, not the vibe

Tally after all 20 (or after the ~8 who actually pick up):

| Signal | Threshold | Means |
|---|---|---|
| Q1 mentions search/directories | 3+ of 8 | SEO thesis alive |
| Q2 yes at $150+ | 4+ of 8 | Lead sales viable |
| Q3 answers "never/rarely" | 5+ of 8 | SiteLitmus funnel confirmed |
| Q4 gives a concrete lost-job story | 3+ of 8 | SiteLitmus funnel strongly confirmed |
| Q5 waitlist signups | 4+ of 8 | Contractors want leads enough to engage |

**Read the combinations:**
- Q2 strong + Q1 mentions search → build the directory as a standalone lead business.
- Q2 weak but Q3/Q4 strong → the directory is a SiteLitmus funnel, not a revenue line.
  Stop investing in lead-sale mechanics and point everything at SiteLitmus. **This is the
  outcome I expect.**
- Q2 weak and Q3/Q4 weak → shelve it. The domain cost $12 and you learned in two afternoons
  instead of six months.

## Rules

- Do not pitch SiteLitmus on these calls. You are gathering evidence, and pitching contaminates
  the answers to Q3 and Q4.
- Write down verbatim phrasing for Q1 and Q4. Their words become the site's copy later.
- If someone asks to be removed from the directory, remove them. It costs nothing and the
  offer is what makes the call honest.
