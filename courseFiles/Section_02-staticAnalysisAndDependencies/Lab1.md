## Goal
Use **Semgrep** to find real issues in a tiny Node/Express app (SQL injection, XSS, insecure cookies, and a sketchy command runner)

Then patch the code and make the scan fail the build when risky patterns show up

## Setup
You should have the required packages installed from the prvious section

```bash
mkdir -p ~/section02-lab1 && cd ~/section02-lab1
```
```bash
npm init -y
```
```bash
npm i express helmet
```
```bash
cat > app.js <<'EOF'
const express = require('express');
const helmet = require('helmet');
const { exec } = require('child_process');

const app = express();
app.use(express.json());
app.use(helmet({ contentSecurityPolicy: { useDefaults: true } }));

// --- VULN 1: Reflected XSS in search ---
app.get('/search', (req, res) => {
  const q = req.query.q || '';
  // untrusted input injected into HTML without encoding
  res.send(`<h1>Results for ${q}</h1>`);
});

// --- VULN 2: Insecure cookie flags ---
app.get('/session', (req, res) => {
  const token = (Math.random() + 1).toString(36).substring(2);
  // no httpOnly/secure/sameSite flags
  res.cookie('sid', token);
  res.json({ ok: true });
});

// --- VULN 3: Command execution with user input ---
app.post('/run', (req, res) => {
  const { cmd } = req.body || {};
  // never pass untrusted strings to a shell
  exec(cmd, (err, stdout, stderr) => {
    if (err) return res.status(500).send('error');
    res.type('text/plain').send(stdout || stderr || 'done');
  });
});

app.listen(5000, () => console.log('Vulnerable app on http://localhost:5000'));
EOF
```
```bash
node app.js
```


## Start
- Run this command to check for vulerabilities using the registry pack
```bash
semgrep --config p/owasp-top-ten .
```

<img width="1155" height="752" alt="image" src="https://github.com/user-attachments/assets/38fe7860-f13a-471d-a01a-b5f85f4e841d" />

- We can clearly see all the vulnerabilities, let's patch them!

## Patching

### Fix 1 - Reflected XSS in /search
- Semgrep flagged:
1. ``javascript.express.security.audit.xss.direct-response-write.direct-response-write``
2. ``javascript.express.security.injection.raw-html-format.raw-html-format``

- **Meaning:** You’re writing user input directly into an HTML response. No escaping. The browser will happily execute it as code

**vulnerable code**
```
app.get('/search', (req, res) => {
  const q = req.query.q || '';
  // Injects untrusted input into HTML
  res.send(`<h1>Results for ${q}</h1>`);
});
```

**Why this is risky:**
1. ``q`` comes from the URL. An attacker can set ``q=<script>...</script>`` or use an event handler like ``"><img src=x onerror=alert(1)>``
2. When you drop that into a template string, the browser executes it as JavaScript. That’s XSS

**secure code**
```
app.get('/search', (req, res) => {
  const q = String(req.query.q || '');
  // No HTML sink. Browser treats this as data.
  res.json({ resultsFor: q });
});
```

**Why this works**
1. ``String(req.query.q || '')`` prevents weird types from sneaking in
2. ``res.json(...)`` sets ``Content-Type: application/json``, the browser doesn’t parse JSON as HTML, so tags don’t execute

**Test it**
```bash
curl -s "http://localhost:5000/search?q=<script>alert(1)</script>"
```


### Fix 2 - Cookie missing security flags in /session
- Semgrep flagged:
1. ``js-cookie-missing-flags``
- **Meaning:** You’re setting a cookie without ``httpOnly``, ``secure``, and ``sameSite``, that’s risky for session cookies

**vulnerable code**
```
app.get('/session', (req, res) => {
  const token = (Math.random() + 1).toString(36).substring(2);
  // No security flags
  res.cookie('sid', token);
  res.json({ ok: true });
});
```

**Why this is risky:**
1. Without ``httpOnly``, JavaScript can read the cookie → easier session theft via XSS
2. Without ``secure``, the cookie can leak over HTTP if anything ever hits non-TLS
3. Without ``sameSite``, CSRF gets much easier

**secure code**
```
app.get('/session', (req, res) => {
  const token = (Math.random() + 1).toString(36).substring(2);
  // Lock it down
  res.cookie('sid', token, { httpOnly: true, secure: true, sameSite: 'lax' });
  res.json({ ok: true });
});
```

**Why this works**
1. ``httpOnly: true`` - browser JS can’t read the cookie (``document.cookie`` won’t show it)
2. ``secure: true`` - only sent over HTTPS
3. ``sameSite: 'lax'`` - stops most CSRF while still usable for typical app flows, use ``'strict'`` for extra caution; use ``'none'`` only if you need cross-site cookies and you’re on HTTPS

**Test it**
```bash
curl -i "http://localhost:5000/session" | grep -i set-cookie
```



### Fix 3 — Command Injection in /run

- Semgrep flagged:
1. ``javascript.express.express-child-process.express-child-process``
- **Meaning:** You pass user-controlled strings to a shell (``exec``), so an attacker can run arbitrary commands

**vulnerable code**
```
const { exec } = require('child_process');

app.post('/run', (req, res) => {
  const { cmd } = req.body || {};
  // Runs whatever the client sends
  exec(cmd, (err, stdout, stderr) => {
    if (err) return res.status(500).send('error');
    res.type('text/plain').send(stdout || stderr || 'done');
  });
});
```

**Why this is risky:**
1. ``cmd`` could be ``ls; cat /etc/passwd``, backticks, subshells, you name it
2. This is full remote code execution, game over

**secure code** - remove the shell; use an allowlist and ``spawn``
```
const { spawn } = require('child_process');

const ALLOWED = {
  date:   { cmd: 'date',   args: [] },
  uptime: { cmd: 'uptime', args: [] }
};

app.post('/run', (req, res) => {
  const key = String((req.body || {}).cmd || '');
  const entry = ALLOWED[key];
  if (!entry) return res.status(400).json({ error: 'not allowed' });

  // Runs a fixed program with fixed args — no user strings enter the shell
  const child = spawn(entry.cmd, entry.args, { stdio: 'pipe' });
  let out = '';
  child.stdout.on('data', d => out += d.toString());
  child.stderr.on('data', d => out += d.toString());
  child.on('close', () => res.type('text/plain').send(out || 'done'));
});
```

**Why this works**
1. **No shell:** ``spawn`` runs a binary directly; it doesn’t interpret ``;``, ``&&``, backticks, etc
2. **Allowlist:** users choose from known-safe commands you define. They can’t pass arbitrary programs or arguments
3. **Constant args:** keep ``args`` fixed wherever possible. If you ever need user input, validate strictly (regex/enum/ranges) and pass as separate args, never as one string

**Test it**
```bash
curl -s -X POST http://localhost:5000/run -H 'Content-Type: application/json' -d '{"cmd":"date"}'
```
```bash
curl -s -X POST http://localhost:5000/run -H 'Content-Type: application/json' -d '{"cmd":"ls; cat /etc/passwd"}'
```



---
[Back to the section](/courseFiles/Section_02-staticAnalysisAndDependencies/staticAnalysis.md)



