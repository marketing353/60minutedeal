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
leave and come back. On the last step it **downloads the request to the visitor's own
device** — nothing is transmitted to a server or dealership.

## Local development

    npx serve .          # or: python -m http.server 8000

Then open http://localhost:3000. Opening `index.html` via `file://` will not work —
the runtime needs an HTTP origin to fetch React.

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
- [ ] Replace the three Unsplash hero/category photos with real inventory photography.
- [ ] Decide whether the form should submit somewhere; today it is download-only.
