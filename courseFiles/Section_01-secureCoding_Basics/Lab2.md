![image](https://github.com/user-attachments/assets/068fae26-6e8f-402f-ad69-63a4e6a1f59e)

# Input Validation And Sanitization

## Goal
Strengthen your input validation & sanitization skills by exploiting two classic flaws and then fixing them properly:
1. Mass Assignment / Over-posting -> escalate a normal user to admin
2. Path Traversal -> read files outside the intended directory

You’ll use ``curl`` to exploit and then patch small, focused Node/Express endpoints. The point is to see the bug clearly and practice the right kinds of validation, allowlisting, and safe file handling

## Setup
```bash
cd ~/Secure_Coding/lab1-2/
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

<img width="711" height="201" alt="curl_update" src="https://github.com/user-attachments/assets/7e06a721-c6e8-4dc8-9d5a-a00da3bd11e0" />


- Overpost ``role`` to become admin:
```bash
curl -s http://localhost:4000/profile/update \
  -H 'Content-Type: application/json' \
  -d '{"displayName":"Owned","role":"admin"}' | jq .
```

<img width="708" height="200" alt="curl_update_admin" src="https://github.com/user-attachments/assets/a0728380-2132-4a56-9769-b992d6abb4aa" />


- **Result:** your role flips to "admin". That’s a silent privilege escalation caused by missing allowlist validation

### Patched code
- Replace the vulnerable handler with a safe allowlist + validation. Edit ``app.js`` and **add this secure variant below the vulnerable one**:
```
// SECURE: allowlist + validation + forbidden fields
app.post(
  '/profile/update/secure',
  forbidFields(['role', 'isAdmin', 'accountStatus']),
  [
    body('displayName').optional().isString().isLength({ min: 1, max: 80 }),
    body('email').optional().isEmail().isLength({ max: 120 })
  ],
  (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty())
      return res.status(400).json({ ok: false, errors: errors.array() });

    const updates = {};
    if (typeof req.body.displayName === 'string')
      updates.displayName = req.body.displayName;
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

Try to escalate again against the secure route (should fail silently to change role):

```
curl -s http://localhost:4000/profile/update/secure \
  -H 'Content-Type: application/json' \
  -d '{"displayName":"Still Owned","role":"admin"}' | jq .
```


## Path Traversal
- What the bug looks like in code (vulnerable pattern)
```
// VULNERABLE: path.join(SAFE_DIR, userInput) without validation
app.get('/files', (req, res) => {
  const filename = req.query.filename || 'welcome.txt';
  const full = path.join(SAFE_DIR, filename);
  fs.readFile(full, 'utf8', (err, data) => {
    if (err) return res.status(404).send('Not found');
    res.type('text/plain').send(data);
  });
});
```

**Why it’s bad:** ``..`` segments (or encoded forms) can escape SAFE_DIR. Attackers can attempt to read sensitive files

### Exploit
- Try a normal request:
```bash
curl -s 'http://localhost:4000/files?filename=welcome.txt'
```

- Attempt traversal (Linux):
```bash
curl -s 'http://localhost:4000/files?filename=../app.js'
```

- You should see your script, otherwise unaccesable

### Patched code
- Add below the vulnerable route, this has a validation + normalization + “stay inside base” check:
```
// SECURE: normalize, validate, and enforce base directory
app.get('/files/secure', (req, res) => {
  const raw = String(req.query.filename || '');

  // 1) Basic filename policy: allow only simple names (no slashes)
  // Adjust as needed, but tight by default:
  if (!/^[a-zA-Z0-9._-]{1,100}$/.test(raw)) {
    return res.status(400).send('Bad filename');
  }

  // 2) Resolve and ensure path stays within SAFE_DIR
  const full = path.join(SAFE_DIR, raw);
  const normalizedBase = path.resolve(SAFE_DIR);
  const normalizedFull = path.resolve(full);
  if (!normalizedFull.startsWith(normalizedBase + path.sep) && normalizedFull !== normalizedBase) {
    return res.status(400).send('Invalid path');
  }

  fs.readFile(normalizedFull, 'utf8', (err, data) => {
    if (err) return res.status(404).send('Not found');
    res.type('text/plain').send(data);
  });
});
```

**What changed and why?**
- **Strict filename policy:** We only accept a constrained set of characters (no ``/`` or ``\``)
- **Normalize + compare:** ``path.resolve`` and a base-dir prefix check ensure the final path still lives inside ``SAFE_DIR``
- **Fail closed:** Anything that doesn’t meet policy returns a 4xx

Verify the fix

Normal use still works:
```bash
curl -s 'http://localhost:4000/files/secure?filename=welcome.txt'
```

Traversal is blocked:
```bash
curl -i 'http://localhost:4000/files/secure?filename=../../etc/hostname'
```

<img width="908" height="221" alt="patched_path_traversal" src="https://github.com/user-attachments/assets/41b6a532-d164-4594-a0bc-6a37046c1a92" />



---
[Back to the section](/courseFiles/Section_01-secureCoding_Basics/secureCoding_Basics.md)
