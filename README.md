# Password Attack & Defense Lab

A portfolio-grade cybersecurity lab that demonstrates both attack simulation and defensive controls in one project.

## Features

- Attack modules: dictionary, brute force, hybrid, and hash cracking (MD5/SHA256)
- Defense modules: account lockout and request rate limiting
- Analytics: JSONL event logging and Flask dashboard
- Password intelligence: entropy-based strength scoring and custom wordlist generation

## Project Structure

```text
password_lab/
|-- app.py
|-- main.py
|-- attacks/
|   |-- brute.py
|   |-- dictionary.py
|   |-- hash_cracker.py
|   `-- hybrid.py
|-- defense/
|   |-- lockout.py
|   `-- rate_limit.py
|-- utils/
|   |-- logger.py
|   |-- strength.py
|   `-- wordlist_gen.py
|-- templates/
|   `-- dashboard.html
|-- wordlists/
|   `-- common.txt
|-- reports/
|   `-- log.jsonl
`-- requirements.txt
```

## Setup

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## Run Commands

```powershell
# 1) Strength analysis
python .\main.py strength --password MyPass@123

# 2) Dictionary attack
python .\main.py dictionary --target admin123 --wordlist .\wordlists\common.txt

# 3) Hybrid attack
python .\main.py hybrid --target admin123 --wordlist .\wordlists\common.txt --max-suffix 500

# 4) Brute-force simulation
python .\main.py brute --target a1 --max-len 3 --workers 8

# 5) Hash cracking (MD5 example for "admin123")
python .\main.py hash --algorithm md5 --hash 0192023a7bbd73250516f069df18b500 --wordlist .\wordlists\common.txt

# 6) Personalized wordlist generator
python .\main.py wordlist --name student --dob 2003-07-21 --extras student007 cyber123

# 7) Defense simulation (lockout + rate limiting)
python .\main.py login-demo --user demo_user --real-password admin7 --attempts 10

# 8) Dashboard
python .\app.py
```

Open `http://127.0.0.1:5000` in your browser.

## GitHub Publishing Notes

- Keep local artifacts out of Git (`__pycache__/`, `reports/log.jsonl`, generated wordlists).
- Do not commit real secrets. If you add any token or API key in future code, store it in environment variables and use placeholder value `[insert your own]` in docs/examples.
- Dashboard debug mode is controlled by `FLASK_DEBUG` (off by default).

## Suggested Next Improvements

1. Add unit tests + CI pipeline (GitHub Actions)
2. Add REST API endpoints for running modules remotely
3. Add Docker support for one-command setup
