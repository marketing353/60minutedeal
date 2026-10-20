// Vercel serverless function (CommonJS — no build step, no dependencies).
// Receives a finished vehicle request and sends two emails via the Resend API:
//
//   1. ADF/XML to the CRM (CDK-compatible), which is the lead of record.
//   2. A human-readable copy to the marketing inbox.
//
// Required environment variable: ResendAPIKEY
// Set it in Vercel under Project > Settings > Environment Variables.
// It must never be committed to this repository.

// CDK ingests ADF/XML lead email. This address is the lead of record.
const CRM_TO = 'Sales@cjdrofsimivalley.edealerhub.com';

// Human-readable copy, so a person sees the lead even if the CRM import stalls.
const NOTIFY_TO = 'marketing@ridegroup.com';

// Resend's shared sender. Works for testing, but only delivers to the address
// that owns the Resend account — it will NOT reach the CRM. Verify a domain in
// Resend and switch this to e.g. 'leads@ridegroup.com' before taking traffic.
const FROM = '60 Minute Car Deals <onboarding@resend.dev>';

const PROVIDER = '60 Minute Car Deals';

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

// Qualifying detail that has no dedicated ADF element goes into <comments>.
const COMMENT_FIELDS = [
  ['alternative', 'Alternative vehicle'], ['trade', 'Trade-in'],
  ['budget', 'Target monthly payment'], ['down', 'Down payment'],
  ['purchase', 'Purchase method'], ['condition', 'Condition'],
  ['timeline', 'Timeline'], ['employment', 'Employment'],
  ['tenure', 'Time in situation'], ['income', 'Income range'],
  ['credit', 'Credit range'], ['experience', 'Financed before'],
];

const esc = (s) => String(s == null ? '' : s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;').replace(/'/g, '&#39;');

// ADF requires ISO 8601. CRMs are happier with a real local offset than with Z.
function isoWithOffset(date, tz) {
  const parts = {};
  const dtf = new Intl.DateTimeFormat('en-US', {
    timeZone: tz, hourCycle: 'h23', year: 'numeric', month: '2-digit',
    day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit',
  });
  for (const p of dtf.formatToParts(date)) parts[p.type] = p.value;
  const asUTC = Date.UTC(parts.year, parts.month - 1, parts.day, parts.hour, parts.minute, parts.second);
  const mins = Math.round((asUTC - date.getTime()) / 60000);
  const sign = mins >= 0 ? '+' : '-';
  const abs = Math.abs(mins);
  const hh = String(Math.floor(abs / 60)).padStart(2, '0');
  const mm = String(abs % 60).padStart(2, '0');
  return `${parts.year}-${parts.month}-${parts.day}T${parts.hour}:${parts.minute}:${parts.second}${sign}${hh}:${mm}`;
}

// "2021 Ram 1500" -> year/make/model. Free text, so this is a best effort:
// anything we cannot split confidently stays in <model>, which CDK accepts.
function splitVehicle(s) {
  const t = String(s || '').trim().split(/\s+/).filter(Boolean);
  const year = /^(19|20)\d{2}$/.test(t[0] || '') ? t.shift() : '';
  const make = t.shift() || '';
  return { year, make, model: t.join(' ') };
}

function splitName(s) {
  const t = String(s || '').trim().split(/\s+/).filter(Boolean);
  if (t.length === 0) return { first: '', last: '' };
  if (t.length === 1) return { first: t[0], last: '' };
  return { first: t[0], last: t.slice(1).join(' ') };
}

function buildAdf(c) {
  const now = new Date();
  const v = splitVehicle(c.vehicle);
  const n = splitName(c.name);

  // ADF vehicle attributes
  const interest = /lease/i.test(c.purchase) ? 'lease' : 'buy';
  let status = '';
  if (/^new$/i.test(c.condition)) status = 'new';
  else if (/pre-owned|used/i.test(c.condition)) status = 'used';

  const comments = COMMENT_FIELDS
    .filter(([k]) => c[k])
    .map(([k, label]) => `${label}: ${c[k]}`)
    .join('\n');

  const L = [];
  L.push('<?xml version="1.0" encoding="UTF-8"?>');
  L.push('<?adf version="1.0"?>');
  L.push('<adf>');
  L.push('  <prospect status="new">');
  L.push(`    <requestdate>${isoWithOffset(now, 'America/Los_Angeles')}</requestdate>`);
  L.push(`    <vehicle interest="${interest}"${status ? ` status="${status}"` : ''}>`);
  if (v.year) L.push(`      <year>${esc(v.year)}</year>`);
  if (v.make) L.push(`      <make>${esc(v.make)}</make>`);
  L.push(`      <model>${esc(v.model || v.make || c.vehicle)}</model>`);
  L.push('    </vehicle>');
  L.push('    <customer>');
  L.push('      <contact>');
  L.push(`        <name part="first">${esc(n.first)}</name>`);
  if (n.last) L.push(`        <name part="last">${esc(n.last)}</name>`);
  L.push(`        <email>${esc(c.email)}</email>`);
  L.push(`        <phone type="voice" time="nopreference">${esc(c.phone)}</phone>`);
  L.push('        <address type="home">');
  L.push(`          <city>${esc(c.city)}</city>`);
  L.push(`          <regioncode>${esc(c.region)}</regioncode>`);
  L.push(`          <postalcode>${esc(c.postal)}</postalcode>`);
  L.push('          <country>US</country>');
  L.push('        </address>');
  L.push('      </contact>');
  if (comments) L.push(`      <comments>${esc(comments)}</comments>`);
  L.push('    </customer>');
  L.push('    <provider>');
  L.push(`      <name part="full">${esc(PROVIDER)}</name>`);
  L.push('      <service>Vehicle Request</service>');
  L.push('    </provider>');
  L.push('  </prospect>');
  L.push('</adf>');
  return L.join('\n');
}

async function sendEmail(key, payload) {
  const r = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!r.ok) {
    const detail = await r.text();
    throw new Error(`Resend ${r.status}: ${detail}`);
  }
  return r.json().catch(() => ({}));
}

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

  const adf = buildAdf(clean);

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
    `<table style="border-collapse:collapse;font-size:14px;width:100%">${rows}</table>` +
    `<p style="margin:18px 0 0;color:#8a978e;font-size:12px">` +
    `An ADF/XML copy was sent to ${esc(CRM_TO)}.</p></div>`;

  const text = FIELDS.filter(([k]) => clean[k]).map(([k, l]) => `${l}: ${clean[k]}`).join('\n');

  // The CRM email carries the ADF as its plain-text body — ILM parsers read the
  // body, and an HTML part can break them — plus an .xml attachment for imports
  // that prefer a file. No html field here, deliberately.
  const crmEmail = {
    from: FROM,
    to: [CRM_TO],
    reply_to: email,
    subject: `ADF Lead - ${clean.name} - ${clean.vehicle}`,
    text: adf,
    attachments: [{
      filename: 'adf.xml',
      content: Buffer.from(adf, 'utf8').toString('base64'),
    }],
  };

  const notifyEmail = {
    from: FROM,
    to: [NOTIFY_TO],
    reply_to: email,
    subject: `Vehicle request — ${clean.name} (${clean.vehicle})`,
    html,
    text,
  };

  const [crm, notify] = await Promise.allSettled([
    sendEmail(key, crmEmail),
    sendEmail(key, notifyEmail),
  ]);

  if (crm.status === 'rejected') console.error('ADF send to CRM failed:', crm.reason && crm.reason.message);
  if (notify.status === 'rejected') console.error('Notification send failed:', notify.reason && notify.reason.message);

  // Only fail the visitor if the lead reached nobody at all. If one of the two
  // landed, the lead is not lost and asking them to resubmit would duplicate it.
  if (crm.status === 'rejected' && notify.status === 'rejected') {
    return res.status(502).json({ error: 'We could not send your request. Please try again.' });
  }

  return res.status(200).json({ ok: true, crm: crm.status === 'fulfilled', notified: notify.status === 'fulfilled' });
};
