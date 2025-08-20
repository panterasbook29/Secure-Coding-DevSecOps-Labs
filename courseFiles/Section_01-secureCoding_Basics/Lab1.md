## Goal
Get hands-on with two of the most common and dangerous vulnerabilities: SQL Injection and Cross-Site Scripting (XSS)

## Setup
```bash
sudo apt-get update
```
```bash
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
```bash
sudo docker run --rm -p 3000:3000 bkimminich/juice-shop
```

## Start
The app will start on ``http://localhost:3000``

<img width="1920" height="1121" alt="image" src="https://github.com/user-attachments/assets/45c2ac9c-ad83-42c2-8edc-651c63991337" />

## SQL Injection
- **What the bug looks like in code (vulnerable pattern)**
<pre>app.post('/login', async (req, res) => {
  const { email, password } = req.body;

  // Dangerous: string concatenation puts raw user input into SQL
  const sql = `
    SELECT id, email, role 
    FROM Users 
    WHERE email = '${email}' AND password = '${password}'
  `;

  try {
    const rows = await db.query(sql); // imagine db.query returns rows[]
    if (rows.length) {
      // logged in as whoever matches the first row (could be admin)
      req.session.user = rows[0];
      return res.redirect('/my-account');
    }
    return res.status(401).send('Invalid credentials');
  } catch (e) {
    return res.status(500).send('Server error');
  }
});</pre>

- **Why it’s bad:** Attacker-controlled ``'`` and SQL tokens (``OR``, ``--``) merge into the query and change its logic
- The query should be:
<pre>SELECT id, email, role FROM Users WHERE email = 'alice@shop.test' AND password = 'secret'</pre>

- And it becomes:
<pre>SELECT id, email, role FROM Users WHERE email = '' OR 1=1--' AND password = 'anything'</pre>

- The ``--`` comments out the rest, so the condition becomes true for all rows -> first user wins (often the admin)

- To reproduce go to the login page or to ``http://localhost:3000/#/login``
- Enter ``' OR 1=1--`` in the email field and any password

<img width="484" height="602" alt="image" src="https://github.com/user-attachments/assets/ff010af7-9cf0-4da4-92d6-121d2f1919d0" />

- This works because the backend is constructing SQL queries by **string concatenation**
- **Takeaway:** An attacker can bypass authentication and access sensitive data

### Patched code
- We’ll replace string concatenation with proper parameterization and fix adjacent issues (like plaintext passwords)

```
import bcrypt from 'bcrypt';

app.post('/login', async (req, res) => {
  const { email, password } = req.body;

  // Validate shape early (reject junk before touching the DB)
  if (typeof email !== 'string' || typeof password !== 'string') {
    return res.status(400).send('Bad input');
  }

  // Parameterized/Prepared query — user input is never concatenated into SQL text
  const sql = `
    SELECT id, email, role, password_hash
    FROM Users
    WHERE email = ?
    LIMIT 1
  `;

  try {
    const rows = await db.query(sql, [email]); // [email] binds to '?'
    if (!rows.length) return res.status(401).send('Invalid credentials');

    const user = rows[0];
    // Passwords are stored as hashes; compare safely
    const ok = await bcrypt.compare(password, user.password_hash);
    if (!ok) return res.status(401).send('Invalid credentials');

    // Minimal session, no secrets in cookies
    req.session.user = { id: user.id, email: user.email, role: user.role };
    return res.redirect('/my-account');
  } catch (e) {
    // Avoid leaking SQL errors
    return res.status(500).send('Server error');
  }
});
```

**What changed and why?**

- ``?`` placeholders: The database driver sends your SQL and the parameters separately, attack strings are treated as data, not executable SQL
- ``bcrypt.compare``: Never store or compare plaintext passwords, breaks password reuse risk and credential theft impact
- **Input shape check:** Quick sanity check before DB; reduces weird inputs and avoids accidental coercions
- **No error leakage:** We don’t echo SQL errors to the client

## Cross-Site Scripting (XSS)
- **What the bug looks like in code (vulnerable pattern)**

Two common flavors: reflected (in the response immediately) and stored (persisted, hits all viewers)

```
app.get('/search', (req, res) => {
  const q = req.query.q || '';
  // Directly injecting untrusted input into HTML (no encoding)
  const html = `<h1>Results for: ${q}</h1>`;
  res.send(html);
});
```

- If a user calls /search?q=<script>alert(1)</script>, the browser executes <script> inside the page

A stored variant might look like:

```
app.post('/comments', async (req, res) => {
  const { productId, text } = req.body;
  // text is saved as-is
  await db.query('INSERT INTO Comments(product_id, text) VALUES (?, ?)', [productId, text]);
  res.redirect(`/product/${productId}`);
});

app.get('/product/:id', async (req, res) => {
  const comments = await db.query('SELECT text FROM Comments WHERE product_id = ?', [req.params.id]);
  // danger: render raw, unescaped text inside HTML
  const list = comments.map(c => `<li>${c.text}</li>`).join('');
  res.send(`<ul>${list}</ul>`);
});
```

- To do it go to the **Search bar** on the home page
- Enter the following:
<pre><iframe src="javascript:alert('HACKED')"></pre>

<img width="1852" height="1051" alt="image" src="https://github.com/user-attachments/assets/bff18e38-159d-4693-a574-0eaf900e8a19" />

- **Why it works:** Browsers treat <script> and event attributes as executable code. If you place user input into HTML without encoding, the browser will run it

### Patched code

**Secure code (reflected search)**

```
import helmet from 'helmet';
import { escape } from 'lodash';

// Set security headers (including a Content Security Policy)
app.use(helmet({
  contentSecurityPolicy: {
    useDefaults: true,
    directives: {
      // only allow scripts we control (tighten for your app)
      "script-src": ["'self'"]
    }
  }
}));

app.get('/search', (req, res) => {
  const q = typeof req.query.q === 'string' ? req.query.q : '';

  // 1) **Context-aware output encoding** for HTML body context:
  const safe = escape(q); // converts < > & " ' into HTML entities

  // 2) Prefer server templating that auto-escapes OR send JSON to the client
  res.send(`<h1>Results for: ${safe}</h1>`);
});
```

**What changed and why?**
- ``escape()`` (or automatic escaping in a templating engine like Handlebars, Nunjucks, or JSX) transforms ``<`` into ``&lt;``, etc, the browser renders text instead of executing it
- **CSP** via **Helmet** blocks inline scripts and third-party script execution, it’s a second line of defense if someone slips an unescaped payload in
- **Type checks** avoid weird non-string values

<br><br>

**Secure code (stored comments)**
```
import { body, validationResult } from 'express-validator';
import sanitizeHtml from 'sanitize-html';

app.post('/comments',
  body('productId').isInt({ min: 1 }),
  body('text').isLength({ min: 1, max: 2000 }),  // limit size
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) return res.status(400).send('Bad input');

    // 1) **Server-side sanitization** if you truly allow limited HTML:
    const allowed = sanitizeHtml(req.body.text, {
      allowedTags: ['b','i','strong','em','ul','ol','li','p','br'],
      allowedAttributes: {}
    });

    await db.query(
      'INSERT INTO Comments(product_id, text) VALUES (?, ?)',
      [req.body.productId, allowed]
    );
    res.redirect(`/product/${req.body.productId}`);
  }
);

app.get('/product/:id', async (req, res) => {
  const comments = await db.query('SELECT text FROM Comments WHERE product_id = ?', [req.params.id]);

  // 2) **Encode on output** (if you store raw text) OR ensure only sanitized HTML is ever stored
  const list = comments.map(c => `<li>${c.text}</li>`).join(''); // c.text is sanitized above
  res.send(`<ul>${list}</ul>`);
});
```

**What changed and why?**

- **Validation:** reject nonsense values early (e.g., giant strings or non-integers)
- **Sanitization** (if you must allow HTML): sanitize-html strips dangerous tags/attributes. Consider storing raw markdown and rendering server-side with a safe renderer as an alternative
- **Encode on output** when rendering untrusted text into HTML contexts
- **CSP** still applies — treat it as containment if something slips through


**Golden rule: Prefer encoding on output and don’t store raw HTML. If business requires some formatting, sanitize to a minimal, safe subset**


---
[Back to the section](/courseFiles/Section_01-secureCoding_Basics/secureCoding_Basics.md)



  
