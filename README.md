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
build step and no `node_modules`.

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

## Analytics

Both tags are in `<head>` of `index.html`:

- Google Ads `AW-11410655364` and `AW-17527160007` (both configured; the conversion
  label `SlgWCPOkgKgcEMf5zKVB` belongs to the second account, so both are needed)
- Meta Pixel `572850585616970`

On a confirmed send only, the form fires `fbq('track','Lead')` and a gtag `conversion`
event worth USD 1.00. Neither fires on a failed submission.

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
- [ ] Add a cookie/consent banner if required — the page loads Meta and Google tags on
      first paint, before any consent is collected.
- [ ] Consider rate limiting `/api/submit`; there is currently nothing stopping repeat
      submissions beyond the honeypot.
