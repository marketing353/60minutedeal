# 60 Minute Car Deals

Static landing page with an 8-step vehicle-request wizard. Deployed on Vercel.

**Live:** https://60minutedeal.vercel.app

## How it works

No build step. Two files do the work:

- `index.html` — the page. Markup lives inside `<x-dc>`; the wizard logic lives in the
  `<script type="text/x-dc">` block at the bottom as `class Component extends DCLogic`.
- `support.js` — the "dc" runtime (generated; do not hand-edit). On load it pulls
  React 18.3.1 UMD from unpkg with SRI, parses `<x-dc>`, hoists the `<helmet>` block
  into `<head>`, and renders.

Templating: `{{ expr }}` bindings in the markup resolve against the object returned by
`Component.render()`. The `<helmet>` block holds the Google Fonts links and base CSS.

The wizard keeps answers in `localStorage` under `cmcd_request_v3`, so a visitor can
leave and come back. On the last step it POSTs to `/api/submit`, which emails the
request to marketing@ridegroup.com via the Resend REST API. `localStorage` is cleared
only after the send is confirmed, so a failed send never loses the visitor's answers.

## Email (`api/submit.js`)

A dependency-free Vercel function — it calls Resend over `fetch`, so there is still no
build step and no `node_modules`. Every submission sends **two** emails:

| To | Format | Purpose |
|---|---|---|
| `Sales@cjdrofsimivalley.edealerhub.com` | ADF/XML | Lead of record, ingested by CDK |
| `marketing@ridegroup.com` | HTML + text | Human-readable copy |

The CRM email carries the ADF as its **plain-text body** (ILM parsers read the body, and
an HTML part can break them) plus an `adf.xml` attachment for imports that prefer a file.
It deliberately has no `html` field.

Both are sent with `Promise.allSettled`. The visitor only sees an error if **both** fail —
if either landed, the lead is not lost and making them resubmit would duplicate it.

### ADF mapping

`vehicle` is free text, so `splitVehicle()` pulls a leading 4-digit year, then treats the
next token as make and the remainder as model ("2021 Ram 1500" → 2021 / Ram / 1500).
Anything it cannot split confidently stays in `<model>`, which CDK accepts.

- `purchase` = Lease → `interest="lease"`, otherwise `interest="buy"`
- `condition` = New → `status="new"`, Pre-owned → `status="used"`
- Everything with no dedicated ADF element (budget, down payment, timeline, employment,
  income, credit, trade-in) goes into `<comments>`
- `requestdate` is ISO 8601 with a real Pacific offset, not `Z`

**Required env var: `ResendAPIKEY`** (Vercel → Project → Settings → Environment
Variables). Never commit it. If the var is missing the endpoint returns 500 and the
visitor sees a retry message.

The function validates the nine required answers, sanity-checks the email, HTML-escapes
every value, caps each answer at 500 characters, and silently accepts anything with a
`company` field set (honeypot). `reply_to` is the visitor's address, so replying from
the inbox reaches them directly.

`FROM` is currently Resend's shared `onboarding@resend.dev`, which **only delivers to
the address that owns the Resend account**. Verify a domain in Resend and change `FROM`
to e.g. `requests@ridegroup.com` before taking real traffic.

## Conversion tracking

On a confirmed send, `index.html` writes a one-time token to `sessionStorage` and
redirects to **`/thank-you`**. That page consumes the token and only then fires the
conversion events, so a refresh, a bookmark, a shared link or a crawler reaching the URL
reports nothing. Without the guard every one of those would count as a lead.

`thank-you.html` is `noindex,nofollow`. The in-page confirmation in `index.html` is kept
as a fallback for the rare case where the redirect is blocked.

Tags are in `<head>` of both `index.html` and `thank-you.html`:

- Google Ads `AW-11410655364` and `AW-17527160007` (both configured; the conversion
  label `SlgWCPOkgKgcEMf5zKVB` belongs to the second account, so both are needed)
- Meta Pixel `572850585616970`

`/thank-you` fires `fbq('track','Lead')` and the gtag `conversion` event worth USD 1.00.
Neither fires on a failed submission or an unguarded visit.

**Meta data collection.** `autoConfig` is on (first-party `_fbp` cookie, automatic button
and form detection). Advanced Matching is wired: `index.html` stages email, phone, first
and last name, city, state and ZIP in `sessionStorage` immediately before redirecting, and
`thank-you.html` passes them to `fbq('init', ...)`, which SHA-256 hashes every value in the
browser before anything is sent. They travel in `sessionStorage`, never in the URL —
personal data must not ride in a query string. A shared `eventID` is generated so a future
Conversions API send can be de-duplicated against the browser event rather than
double-counted.

## Local development

    node dev-server.js        # http://localhost:3000

`dev-server.js` serves the static files and routes `/api/*` to `./api`, the same way
Vercel does. A plain static server (`npx serve .`) will serve the page but every form
submission will 404, because `/api/submit` needs a Node runtime.

Opening `index.html` via `file://` will not work — the runtime needs an HTTP origin
to fetch React.

To send real email locally, create `.env.local` (gitignored):

    ResendAPIKEY=re_your_key_here

## Editing the form

The 8 screens are declared in one array near the top of the `x-dc` script:

- `T(name, label, placeholder, type, required, inputmode, autocomplete)` — text field
- `C(name, label, [options])` — single-choice field
- `{ k: 'check', name, label }` — checkbox

Add or reorder entries in `SCREENS`; the step counter and progress bar derive from its
length automatically. Bump `KEY` when you change field names, or returning visitors
will restore stale answers.

## Deploy

Pushes to `main` deploy automatically via the Vercel GitHub integration.
`vercel.json` sets security headers and cache policy; there is no framework preset.

## Before launch

- [ ] Point `og:url`, `og:image`, `canonical` (in `index.html`), `robots.txt`, and
      `sitemap.xml` at the real custom domain once it is attached.
- [ ] Verify a sending domain in Resend and update `FROM` in `api/submit.js`.
- [ ] Confirm `ResendAPIKEY` is set in Vercel for Production, Preview and Development.
- [ ] Decide the consent position. There is no cookie banner, and Meta/Google tags load on
      first paint before any consent. Meta's Business Tools Terms put the notice-and-consent
      obligation on the advertiser, and CPRA treats ad-platform sharing as "sharing", which
      normally needs an opt-out link. Confirmed as a deliberate choice, recorded here.
- [ ] Confirm the CRM actually parses the ADF — send one live test to
      Sales@cjdrofsimivalley.edealerhub.com and check it lands in CDK as a prospect.
- [ ] Consider rate limiting `/api/submit`; there is currently nothing stopping repeat
      submissions beyond the honeypot.
