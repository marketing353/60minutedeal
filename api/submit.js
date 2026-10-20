// Vercel serverless function (CommonJS — no build step, no dependencies).
// Receives a finished vehicle request and emails it via the Resend REST API.
//
// Required environment variable: ResendAPIKEY
// Set it in Vercel under Project > Settings > Environment Variables.
// It must never be committed to this repository.

const TO = 'marketing@ridegroup.com';

// Resend's shared sender. Works for testing, but only delivers to the address
// that owns the Resend account. Verify a domain and switch this to something
// like 'requests@ridegroup.com' before taking real traffic.
const FROM = '60 Minute Car Deals <onboarding@resend.dev>';

const FIELDS = [
  ['vehicle', 'Preferred vehicle'], ['alternative', 'Alternative vehicle'],
  ['trade', 'Trade-in'], ['budget', 'Target monthly payment'],
  ['purchase', 'Purchase method'], ['condition', 'Condition'],
  ['down', 'Down payment'], ['timeline', 'Timeline'],
  ['employment', 'Employment'], ['tenure', 'Time in situation'],
  ['income', 'Income range'], ['credit', 'Credit range'],
  ['experience', 'Financed before'], ['city', 'City'],
  ['region', 'State / province'], ['postal', 'ZIP / postal code'],
  ['name', 'Name'], ['email', 'Email'], ['phone', 'Phone'],
];

const esc = (s) => String(s == null ? '' : s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;').replace(/'/g, '&#39;');

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const key = process.env.ResendAPIKEY;
  if (!key) {
    console.error('ResendAPIKEY is not set');
    return res.status(500).json({ error: 'Email is not configured on this deployment.' });
  }

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (e) { return res.status(400).json({ error: 'Malformed request.' }); }
  }
  if (!body || typeof body !== 'object') return res.status(400).json({ error: 'Malformed request.' });

  // Bots fill hidden fields; humans leave them empty. Accept silently so the
  // bot sees success and does not retry.
  if (body.company) return res.status(200).json({ ok: true });

  const required = ['vehicle', 'budget', 'down', 'city', 'region', 'postal', 'name', 'email', 'phone'];
  const missing = required.filter((f) => !String(body[f] || '').trim());
  if (missing.length) return res.status(400).json({ error: 'Some answers are missing.', missing });

  const email = String(body.email).trim();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
    return res.status(400).json({ error: 'That email address does not look right.' });
  }

  // Cap any single answer so an oversized payload cannot bloat the email.
  const clean = {};
  for (const [k] of FIELDS) clean[k] = String(body[k] == null ? '' : body[k]).slice(0, 500).trim();

  const rows = FIELDS
    .filter(([k]) => clean[k])
    .map(([k, label]) =>
      `<tr><td style="padding:7px 14px 7px 0;color:#5c6b61;white-space:nowrap">${esc(label)}</td>` +
      `<td style="padding:7px 0;font-weight:600;color:#0d1a13">${esc(clean[k])}</td></tr>`)
    .join('');

  const html =
    `<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:600px">` +
    `<h2 style="margin:0 0 4px;color:#0d1a13">New vehicle request</h2>` +
    `<p style="margin:0 0 18px;color:#5c6b61;font-size:14px">` +
    `${esc(clean.name)} &middot; ${esc(clean.city)}, ${esc(clean.region)} &middot; ` +
    `${esc(new Date().toLocaleString('en-US', { timeZone: 'America/Los_Angeles' }))} PT</p>` +
    `<table style="border-collapse:collapse;font-size:14px;width:100%">${rows}</table></div>`;

  const text = FIELDS.filter(([k]) => clean[k]).map(([k, l]) => `${l}: ${clean[k]}`).join('\n');

  try {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: FROM,
        to: [TO],
        reply_to: email,
        subject: `Vehicle request — ${clean.name} (${clean.vehicle})`,
        html,
        text,
      }),
    });

    if (!r.ok) {
      const detail = await r.text();
      console.error('Resend rejected the send:', r.status, detail);
      return res.status(502).json({ error: 'We could not send your request. Please try again.' });
    }

    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error('Resend request failed:', err);
    return res.status(502).json({ error: 'We could not send your request. Please try again.' });
  }
};
