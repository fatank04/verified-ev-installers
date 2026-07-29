# Sell-side outreach — the Phase 0 waitlist push

Goal: 20+ contractors on the lead waitlist before any traffic exists. That number is the
go/no-go gate from MONETIZATION.md - under 20 from 200 contacts means contractors do not want
leads badly enough to pay for them, and the whole model is wrong.

## The list

`data/outreach.csv`, rebuilt any time with `python3 scripts/build_outreach.py`.
2,115 of 2,197 contractors have a usable email (96%).

| Priority | Count | Who |
|---|---|---|
| 1 | 661 | Wave-1 state + in a metro we have a page for + a named contact |
| 2 | 879 | Two of the three |
| 3 | 513 | One of the three |
| 4 | 62 | Generic inbox, rural, non-wave-1 |

Start at priority 1. Send 40-50/day, not 661 at once - volume from a cold domain lands in spam
and burns the sending address.

## Send this only after the domain is live

Every link below points at the contractor's own listing page. On the onrender.com URL those
links break the moment you move to verifiedevinstallers.com, and the email cannot be un-sent.
Buy the domain, point Render at it, then send.

## The email

Subject: `Your EVITP listing on Verified EV Installers`

> Hi {contact_person},
>
> I built a directory of contractors that employ EVITP-certified electricians, pulled from
> EVITP's own public state lists. {company} is in it:
>
> {listing_url}
>
> The listing is free and I am not selling placement - the order is by data, not by payment.
> Two things you can do with it:
>
> 1. Correct anything wrong. Service area, phone, whether you take commercial work.
> 2. Join the lead waitlist. When a property owner in {metro} asks for quotes, I route it to
>    waitlist contractors first. The first leads are free so you can judge them yourself.
>
> Both take about a minute: {site}/for-installers/
>
> If you would rather not be listed at all, reply and I will remove you on the next refresh.
>
> Ankur
> Foresight Solutions Group

Why it is shaped this way:
- The listing already exists, so the first line is a fact, not a pitch.
- "I am not selling placement" pre-empts the assumption that this is another pay-to-play
  directory, which is what every contractor assumes on sight.
- Free-first removes the risk objection before it is raised.
- The opt-out is real and stated plainly. It is also required for cold email compliance.

## Compliance

Business-to-business cold email to a published business address is generally permitted in the
US under CAN-SPAM, but the rules still apply: real physical address in the footer, working
opt-out, honest subject line, opt-outs honored within 10 days. Add the Foresight Solutions
Group address to the footer before sending. Not legal advice - worth 20 minutes of reading
CAN-SPAM's actual text before the first batch.

## Measuring it

Track replies and waitlist form submissions, not opens. The waitlist form stamps `lead_id`,
`source_url`, and `submitted_at`, and installer submissions carry `company` and
`service_states`, so waitlist signups are distinguishable from buyer leads in the inbox.

Decision point at 200 sent: 20+ signups means proceed to Phase 1. Under 20 means stop and
re-examine the premise before building anything else.
