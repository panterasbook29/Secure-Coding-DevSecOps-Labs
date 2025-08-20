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
- What the bug looks like in code (vulnerable pattern)
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

<pre>import bcrypt from 'bcrypt';

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
});</pre>

**What changed and why?**

- ``?`` placeholders: The database driver sends your SQL and the parameters separately, attack strings are treated as data, not executable SQL
- ``bcrypt.compare``: Never store or compare plaintext passwords, breaks password reuse risk and credential theft impact
- **Input shape check:** Quick sanity check before DB; reduces weird inputs and avoids accidental coercions
- **No error leakage:** We don’t echo SQL errors to the client

## Cross-Site Scripting (XSS)
- Go to the **Search bar** on the home page
- Enter the following:
<pre><iframe src="javascript:alert('HACKED')"></pre>

<img width="1852" height="1051" alt="image" src="https://github.com/user-attachments/assets/bff18e38-159d-4693-a574-0eaf900e8a19" />
