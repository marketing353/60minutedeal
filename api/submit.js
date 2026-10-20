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

// Sends from the verified domain, so mail reaches the CRM and the marketing
// inbox rather than only the Resend account owner.
const FROM = '60 Minute Car Deals <leads@usedcarssimivalley.com>';

const PROVIDER = '60 Minute Car Deals';

// Meta Conversions API. Server-side events survive ad blockers and ITP, which
// cost the browser pixel a large share of conversions. Both sides send the same
// event_id so Meta de-duplicates rather than double-counting.
const META_PIXEL_ID = '572850585616970';
const META_API_VERSION = 'v21.0';

const crypto = require('crypto');
const sha256 = (v) => crypto.createHash('sha256').update(String(v), 'utf8').digest('hex');

// Meta requires values normalised before hashing, or the match simply fails.
const norm = {
  em: (v) => String(v).trim().toLowerCase(),
  ph: (v) => {
    const d = String(v).replace(/\D/g, '');
    return d.length === 10 ? '1' + d : d;          // assume US when no country code
  },
  name: (v) => String(v).trim().toLowerCase().replace(/[^a-z]/g, ''),
  ct: (v) => String(v).trim().toLowerCase().replace(/[^a-z]/g, ''),
  st: (v) => String(v).trim().toLowerCase().replace(/[^a-z]/g, '').slice(0, 2),
  zp: (v) => String(v).replace(/\D/g, '').slice(0, 5),
};

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
  // A Spanish lead stores its answers as Spanish labels, so these must match
  // both languages — otherwise every /es lead files as interest="buy" with no
  // condition at all.
  const interest = /lease|arrendamiento/i.test(c.purchase) ? 'lease' : 'buy';
  let status = '';
  if (/^(new|nuevo)$/i.test(c.condition)) status = 'new';
  else if (/pre-owned|used|seminuevo|usado/i.test(c.condition)) status = 'used';

  // Lead the comments with the language so whoever picks this up in CDK knows
  // to call back in Spanish.
  const comments = (c.lang === 'es'
      ? ['IDIOMA / LANGUAGE: Spanish — customer submitted the Spanish form']
      : [])
    .concat(COMMENT_FIELDS
      .filter(([k]) => c[k])
      .map(([k, label]) => `${label}: ${c[k]}`))
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

async function sendMetaCapi(c, meta) {
  const token = process.env.MetaCAPIToken || process.env.METACAPITOKEN || process.env.META_CAPI_TOKEN;
  if (!token) { console.warn('MetaCAPIToken not set — skipping Conversions API'); return null; }

  const n = splitName(c.name);
  const user_data = {
    em: [sha256(norm.em(c.email))],
    ph: [sha256(norm.ph(c.phone))],
    fn: [sha256(norm.name(n.first))],
    ct: [sha256(norm.ct(c.city))],
    st: [sha256(norm.st(c.region))],
    zp: [sha256(norm.zp(c.postal))],
    country: [sha256('us')],
  };
  if (n.last) user_data.ln = [sha256(norm.name(n.last))];

  // Never hashed — Meta matches these as-is.
  if (meta.fbp) user_data.fbp = meta.fbp;
  if (meta.fbc) user_data.fbc = meta.fbc;
  if (meta.ip) user_data.client_ip_address = meta.ip;
  if (meta.ua) user_data.client_user_agent = meta.ua;

  const event = {
    event_name: 'Lead',
    event_time: Math.floor(Date.now() / 1000),
    action_source: 'website',
    user_data,
    custom_data: { value: 1.0, currency: 'USD', content_name: c.vehicle },
  };
  if (meta.eventId) event.event_id = meta.eventId;      // dedupe key vs the pixel
  if (meta.pageUrl) event.event_source_url = meta.pageUrl;

  const url = `https://graph.facebook.com/${META_API_VERSION}/${META_PIXEL_ID}/events`;
  const r = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data: [event], access_token: token }),
  });
  const out = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(`Meta CAPI ${r.status}: ${JSON.stringify(out)}`);
  return out;
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

  clean.lang = String(body.lang || 'en').slice(0, 5);
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
    subject: `ADF Lead${clean.lang === 'es' ? ' [ES]' : ''} - ${clean.name} - ${clean.vehicle}`,
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
    subject: `Vehicle request${clean.lang === 'es' ? ' [Spanish]' : ''} — ${clean.name} (${clean.vehicle})`,
    html,
    text,
  };

  const meta = {
    eventId: String(body.eventId || '').slice(0, 100),
    fbp: String(body.fbp || '').slice(0, 200),
    fbc: String(body.fbc || '').slice(0, 300),
    pageUrl: String(body.pageUrl || '').slice(0, 500),
    ip: String(req.headers['x-forwarded-for'] || '').split(',')[0].trim(),
    ua: String(req.headers['user-agent'] || '').slice(0, 500),
  };

  const [crm, notify, capi] = await Promise.allSettled([
    sendEmail(key, crmEmail),
    sendEmail(key, notifyEmail),
    sendMetaCapi(clean, meta),
  ]);

  if (capi.status === 'rejected') console.error('Meta CAPI failed:', capi.reason && capi.reason.message);

  if (crm.status === 'rejected') console.error('ADF send to CRM failed:', crm.reason && crm.reason.message);
  if (notify.status === 'rejected') console.error('Notification send failed:', notify.reason && notify.reason.message);

  // Only fail the visitor if the lead reached nobody at all. If one of the two
  // landed, the lead is not lost and asking them to resubmit would duplicate it.
  if (crm.status === 'rejected' && notify.status === 'rejected') {
    return res.status(502).json({ error: 'We could not send your request. Please try again.' });
  }

  // A CAPI failure never fails the lead — the lead is the email, not the pixel.
  return res.status(200).json({
    ok: true,
    crm: crm.status === 'fulfilled',
    notified: notify.status === 'fulfilled',
    capi: capi.status === 'fulfilled',
  });
};
