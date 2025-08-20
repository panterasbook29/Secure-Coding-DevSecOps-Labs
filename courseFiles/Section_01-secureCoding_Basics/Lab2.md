## Goal
Strengthen your input validation & sanitization skills by exploiting two classic flaws and then fixing them properly:
1. Mass Assignment / Over-posting -> escalate a normal user to admin
2. Path Traversal -> read files outside the intended directory

You’ll use ``curl`` to exploit and then patch small, focused Node/Express endpoints. The point is to see the bug clearly and practice the right kinds of validation, allowlisting, and safe file handling

## Setup
```bash
sudo apt-get update
```
```bash
sudo apt-get install -y nodejs npm
```
```bash
mkdir -p ~/lab2 && cd ~/lab2
```
```bash
npm init -y
```
```bash
npm i express express-validator helmet
```
```bash
cat > app.js <<'EOF'
const express = require('express');
const { body, validationResult } = require('express-validator');
const path = require('path');
const fs = require('fs');

const app = express();
app.use(express.json());

// ----------------------------------------------------
// In-memory "database" for demo purposes
// ----------------------------------------------------
let user = {
  id: 1,
  email: 'user@example.com',
  displayName: 'Casey',
  role: 'user' // <-- attacker will try to escalate this
};

// ----------------------------------------------------
// VULNERABLE #1: Mass Assignment / Over-posting
// ----------------------------------------------------
// VULNERABLE: blindly merge req.body into our user object
app.post('/profile/update', (req, res) => {
  Object.assign(user, req.body); // merges *all* keys, including 'role'
  return res.json({ ok: true, user });
});

// ----------------------------------------------------
// VULNERABLE #2: Path Traversal in file reader
// ----------------------------------------------------
// Serve files from a "safe" folder
const SAFE_DIR = path.join(__dirname, 'files');

// VULNERABLE: trust a 'filename' query param and join it directly
app.get('/files', (req, res) => {
  const filename = req.query.filename || 'welcome.txt';
  const full = path.join(SAFE_DIR, filename); // attacker can smuggle ../
  fs.readFile(full, 'utf8', (err, data) => {
    if (err) return res.status(404).send('Not found');
    res.type('text/plain').send(data);
  });
});

app.listen(4000, () => {
  console.log('Lab2 running on http://localhost:4000');
});
EOF
```
```bash
mkdir -p files
```
```bash
echo "Hello from the safe directory." > files/welcome.txt
```
```bash
node app.js
```

Now the App is live at: ``http://localhost:4000``

## Start

## Mass Assignment / Over-posting
- What the bug looks like in code (vulnerable pattern)
```
// unvalidated merge lets clients set anything, including 'role'
app.post('/profile/update', (req, res) => {
  Object.assign(user, req.body);
  return res.json({ ok: true, user });
});
```

- **Why it’s bad:** The server assumes clients only send “legit” fields. Attackers can over-post sensitive fields (like ``role``, ``isAdmin``, ``balance``, ``status``) and overwrite them

### Exploit
- Check current profile:
```bash
curl -s http://localhost:4000/profile/update \
  -H 'Content-Type: application/json' \
  -d '{}' | jq .
```

- You should see this

<img width="647" height="250" alt="image" src="https://github.com/user-attachments/assets/50ceedbd-72d1-41d6-88d1-485bfaf6f400" />

- Overpost ``role`` to become admin:
```bash
curl -s http://localhost:4000/profile/update \
  -H 'Content-Type: application/json' \
  -d '{"displayName":"Owned","role":"admin"}' | jq .
```

<img width="640" height="244" alt="image" src="https://github.com/user-attachments/assets/f8cb5722-78be-4a5f-94d6-c2516f141324" />


- **Result:** your role flips to "admin". That’s a silent privilege escalation caused by missing allowlist validation

### Patched code
- Replace the vulnerable handler with a safe allowlist + validation. Edit ``app.js`` and **add this secure variant below the vulnerable one** (or replace it entirely when you’re done testing):
```
// SECURE: explicit allowlist + server-side validation
app.post(
  '/profile/update/secure',
  [
    body('displayName').optional().isString().isLength({ min: 1, max: 80 }),
    body('email').optional().isEmail().isLength({ max: 120 }),
    // NOTE: we DO NOT accept 'role' from clients — that’s the whole point.
    // No validator for 'role' means clients can’t change it here.
  ],
  (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) return res.status(400).json({ ok: false, errors: errors.array() });

    // Allowlist: only update fields we explicitly permit
    const updates = {};
    if (typeof req.body.displayName === 'string') updates.displayName = req.body.displayName;
    if (typeof req.body.email === 'string') updates.email = req.body.email;

    Object.assign(user, updates);
    return res.json({ ok: true, user });
  }
);
```

**What changed and why?**
- **Allowlist (positive validation):** We only accept ``displayName`` and ``email``, no ``role``, no ``isAdmin``, no sensitive fields
- **Shape + type checks:** Using ``express-validator`` to enforce expected types/lengths
- **Least privilege at the API boundary:** Clients don’t control authorization fields, ever

Try to escalate again against the secure route (should fail silently to change role)


---
[Back to the section](/courseFiles/Section_01-secureCoding_Basics/secureCoding_Basics.md)
