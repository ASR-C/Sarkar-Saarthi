# Sarkari Saathi (सरकारी साथी)
### Government Form Guidance Platform

> An independent, multilingual citizen education platform showing people step-by-step how to fill official government forms at home without paying middlemen or cyber cafes.

---

## 1. Vision & Core Principles

- **No Form Submission**: We guide; we never submit a form on behalf of a user and never touch government portal credentials.
- **Zero Credential Collection**: We never ask for, accept, or store Aadhaar numbers, PAN, bank passwords, or government OTPs.
- **Strict Allowlist**: All outbound links are verified `.gov.in` and `.nic.in` domains with fake-site warnings.
- **Freshness Guarantee**: Every guide displays its last-verified date and a prominent warning if older than 30 days.
- **Honesty Rule**: Every guide clearly states its execution mode: **Fully Online**, **Partly Online (Visit Needed)**, or **In Person**.

---

## 2. Tech Stack

- **Backend**: Python 3.12 / 3.14 with Django 5.1.x
- **Languages**: 3 Core Primary Languages: **English (`en`)**, **Hindi (`hi`)**, and **Marwadi (`mwr` / मारवाड़ी)** with automatic translation fallback (Marwadi -> Hindi -> English)
- **Database**: TiDB Cloud (MySQL-compatible, TLS port 4000, `utf8mb4` for Indian scripts) with seamless SQLite fallback for local development
- **Authentication**: Custom User model (`accounts.User`), Argon2 password hashing (`argon2-cffi`), session authentication
- **Email OTP**: Brevo Transactional Email API (with automatic local console fallback for offline/dev environments)
- **Design System**: Option A: Paper and Stamp (Warm cream `#F6F3EC`, dark ink-blue `#131E29`, postal-red stamp accents `#BA1A1A`, Erode / Fraunces serif + Noto Sans typography)
- **Frontend Standards**: Fully audited against `design-taste-frontend` (zero banned gradients, zero fake cards, >=48px mobile touch targets, responsive down to 360px)

---

## 3. Project Structure

```text
SARKAAR SAATHI/
├── accounts/               # Custom User, Argon2 auth, HMAC-hashed Signup OTPs, Brevo integration
├── config/                 # Django settings, URL routing, WSGI/ASGI, TiDB TLS config
├── core/                   # Context processors, homepage, about & DPDP Act privacy views
├── guides/                 # Categories, OfficialLink allowlist, Guides, Translations, Steps, Documents
├── wizard/                 # Yes/No decision tree wizard models and session navigation
├── templates/              # Server-rendered HTML templates with design-taste-frontend compliance
├── static/
│   ├── css/theme.css       # Paper & Stamp CSS tokens, typography, ruled form lines, responsive styles
│   └── img/                # High-resolution CC0/public domain archival delivery & stamp plates
├── requirements.txt        # Pinned dependencies
├── manage.py
├── .env.example            # Environment variables blueprint
└── README.md
```

---

## 4. Quickstart & Local Setup

### Step 1: Create and Activate Virtual Environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Fill in your configuration:
- `SECRET_KEY`: Django secret key
- `DEBUG`: `True` for development, `False` for production
- `ALLOWED_HOSTS`: `localhost,127.0.0.1`
- `TIDB_HOST`, `TIDB_PORT`, `TIDB_USER`, `TIDB_PASSWORD`, `TIDB_DATABASE`: TiDB Cloud connection details (leave `TIDB_HOST` blank for local SQLite mode)
- `BREVO_API_KEY`, `BREVO_SENDER_EMAIL`, `BREVO_SENDER_NAME`: For transactional email OTPs (falls back to console if unset)

### Step 4: Run Migrations
```bash
python manage.py migrate
```

### Step 5: Seed Phase 1 Verified National Data
This command populates the database with 8+ real national guides, 10 official allowlisted portals, 7 categories, and wizard questions:
```bash
python manage.py seed_phase1_data
```

### Step 6: Start Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 5. Seeded National Guides (Phase 1)

1. **Indian Passport Application** (Normal & Tatkaal) - Passport Seva Kendra (PSK)
2. **Instant e-PAN Card Application** - Income Tax e-Filing Portal
3. **Learner's Licence (LL) Application** - Parivahan Sarathi
4. **New Voter Registration (Form 6)** - Election Commission of India (ECI)
5. **Aadhaar Card Online Address Update** - myAadhaar (UIDAI)
6. **National Scholarship Portal Registration** - NSP (Ministry of Education)
7. **PM Ujjwala Yojana Free Gas Connection** - MoPNG
8. **DigiLocker Account & Document Fetch** - MeitY

---

## 6. Testing & Quality Gates

### Running Django Test Suite
```bash
python manage.py test
```
*Current test suite: 18 tests covering signup OTP generation, HMAC hashing, 10-minute expiry, lockout after 5 attempts, 60s cooldown resend rules, password login without OTP, official domain allowlist validator, decision tree wizard branching, Marwadi language switcher, and guide translation fallback.*

### Running Frontend Taste Linter
```bash
node .agents/skills/design-taste-frontend/scripts/lint.mjs templates static
```
*Result: 0 FAIL, 0 WARN.*

### Running Frontend Browser Inspector (Playwright)
```bash
node .agents/skills/design-taste-frontend/scripts/inspect.mjs http://127.0.0.1:8000/
node .agents/skills/design-taste-frontend/scripts/inspect.mjs http://127.0.0.1:8000/guides/passport-application-normal-tatkaal/
node .agents/skills/design-taste-frontend/scripts/inspect.mjs http://127.0.0.1:8000/guides/official-links/
node .agents/skills/design-taste-frontend/scripts/inspect.mjs http://127.0.0.1:8000/wizard/
```
*All key Phase 1 landing pages pass with **0 FAIL** across desktop (1440px), tablet (768px), and mobile (390px).*

---

## 7. TiDB Cloud Production Configuration

TiDB Cloud Serverless speaks MySQL protocol over TLS on port 4000:
- Use `pymysql` or `mysqlclient` with `ssl={'ca': TIDB_CA_PATH}`
- Always use `utf8mb4` character set to store Devanagari, Marwadi, Hindi, and all Indian scripts accurately
- Connection limits: TiDB Cloud free-tier has concurrency caps; keep Django database connections short-lived (`CONN_MAX_AGE=60`)
- Primary keys: Prefer `AUTO_RANDOM` or standard auto-increment integer IDs for Django models

---

## 8. Security & Legal Compliance

- **DPDP Act 2023**: Mandatory explicit consent tickbox on registration; transparent privacy charter; account deletion on request.
- **Argon2 Passwords**: State-of-the-art password hashing resisting GPU/ASIC brute-force attacks.
- **HMAC OTP Storage**: OTPs are never stored in plaintext; hashed using HMAC-SHA256 with the server's secret key.
- **Emblem Restriction**: No use of the State Emblem of India or government logos (in strict compliance with the State Emblem of India Prohibition of Improper Use Act, 2005). Clear independent disclaimer on every page.
