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

```
```bash

```
```bash

```






---
[Back to the section](/courseFiles/Section_01-secureCoding_Basics/secureCoding_Basics.md)
