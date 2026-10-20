// Local development server. Serves the static files and routes /api/* to the
// matching function in ./api, mirroring how Vercel runs this project.
//
//   node dev-server.js            (then open http://localhost:3000)
//
// Reads ResendAPIKEY from the environment, or from a .env.local file if present
// (.env.local is gitignored — never commit a key).

const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const PORT = process.env.PORT || 3000;

try {
  for (const line of fs.readFileSync(path.join(ROOT, '.env.local'), 'utf8').split('\n')) {
    const m = line.match(/^\s*([\w.-]+)\s*=\s*(.*)\s*$/);
    if (m && !process.env[m[1]]) process.env[m[1]] = m[2].replace(/^["']|["']$/g, '');
  }
  console.log('loaded .env.local');
} catch (e) { /* no .env.local — fine */ }

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json', '.webp': 'image/webp', '.svg': 'image/svg+xml',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.xml': 'application/xml',
  '.txt': 'text/plain; charset=utf-8',
};

function sendJson(res, code, obj) {
  const b = JSON.stringify(obj);
  res.writeHead(code, { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(b) });
  res.end(b);
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  let pathname = decodeURIComponent(url.pathname);

  if (pathname.startsWith('/api/')) {
    const file = path.join(ROOT, pathname.replace(/\/+$/, '') + '.js');
    if (!fs.existsSync(file)) return sendJson(res, 404, { error: 'No such function' });

    const chunks = [];
    for await (const c of req) chunks.push(c);
    const raw = Buffer.concat(chunks).toString('utf8');
    let body = raw;
    if ((req.headers['content-type'] || '').includes('application/json')) {
      try { body = JSON.parse(raw || '{}'); } catch (e) { body = {}; }
    }
    req.body = body;

    // Vercel's response helpers
    res.status = (c) => { res.statusCode = c; return res; };
    res.json = (o) => { sendJson(res, res.statusCode || 200, o); return res; };

    delete require.cache[require.resolve(file)];
    try {
      await require(file)(req, res);
    } catch (err) {
      console.error(err);
      if (!res.headersSent) sendJson(res, 500, { error: 'Function threw' });
    }
    return;
  }

  if (pathname === '/') pathname = '/index.html';
  let file = path.join(ROOT, pathname);
  // cleanUrls: /thank-you -> thank-you.html, matching vercel.json
  if (!fs.existsSync(file) && fs.existsSync(file + '.html')) file += '.html';
  if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    return res.end('Not found');
  }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' });
  fs.createReadStream(file).pipe(res);
});

server.listen(PORT, () => {
  console.log(`dev server on http://localhost:${PORT}`);
  console.log(`ResendAPIKEY: ${process.env.ResendAPIKEY ? 'set' : 'NOT set — /api/submit will return 500'}`);
});
