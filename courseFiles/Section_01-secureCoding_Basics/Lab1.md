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

## Exploitation
The app will start on ``http://localhost:3000``

<img width="1920" height="1121" alt="image" src="https://github.com/user-attachments/assets/45c2ac9c-ad83-42c2-8edc-651c63991337" />

### SQL Injection

- Go to the login page or to ``http://localhost:3000/#/login``
- Enter ``' OR 1=1--`` in the email field and any password

<img width="484" height="602" alt="image" src="https://github.com/user-attachments/assets/ff010af7-9cf0-4da4-92d6-121d2f1919d0" />

- This works because the backend is constructing SQL queries by **string concatenation**
- **Takeaway:** An attacker can bypass authentication and access sensitive data

### Cross-Site Scripting (XSS)
- Go to the **Search bar** on the home page
- Enter the following:
<pre><script>alert("pwned!")</script></pre>
