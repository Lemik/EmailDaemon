# 📩 Gmail Email Fetcher & Parser

## **Overview**

This Python project fetches recent emails from Gmail using the Gmail API, extracts relevant details from HTML-formatted emails, and parses transaction data such as e-transfer details.

For architecture, operational workflows, and known gaps in the `src/` stack, see [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md).

## **Main Focus**
Interac e-Transfer

## **Features**

✅ Fetches latest emails from Gmail API
✅ Extracts sender, subject, and email body
✅ Parses HTML emails and extracts links
✅ Filters e-transfer-related links
✅ Extracts transaction details (amount, reference number, sender, etc.)
✅ Modular structure for easy expansion
✅ Configurable settings via config.py
✅ Stores parsed data in an AWS MySQL database
✅ Marks emails as read and moves them to a specified folder
✅ Runs automatically on an EC2 instance using a cron job

## **Project Structure**

```
📁 EmailDaemon/
 ├── auth/
 │   ├── client_secret.json   # Google OAuth client JSON from Cloud Console (not committed)
 │   ├── token.pickle         # Saved Gmail tokens (generated after first login; not committed)
 │   └── auth.py              # Gmail OAuth / token handling
 │
 ├── db/
 │   └── mySql_db_manipulations.py  # MySQL connection & inserts
 │
 ├── services/
 │   ├── fetch_emails.py        # Fetch messages via Gmail API
 │   ├── parse_emails.py        # Parse HTML, Interac fields, headers
 │   ├── emails_manipulations.py # Mark read, move, labels, star
 │   ├── helpers.py             # Validation, DB payload shaping
 │   ├── extract.py             # Extraction helpers
 │   └── debug.py               # Debug logging helpers
 │
 ├── src/                       # Rental analytics, notifications (see MAP.md)
 ├── config.py                  # Configuration (DB, logging, API scopes)
 ├── main.py                    # Main Gmail ingest script
 ├── daily_email_job.py         # Scheduled job variant (logging + job stats)
 ├── job_monitor.py             # Inspect job runs / logs
 ├── PROJECT_OVERVIEW.md        # Architecture, workflows, gaps
 ├── requirements.txt
 └── README.md

```

## **Setup & Installation**

### **1️⃣ Enable Gmail API & Get Credentials**

1. **Go to** [Google API Console](https://console.cloud.google.com/)
2. Enable **Gmail API** for your Google account
3. Create OAuth credentials (OAuth Client ID)
4. Download the client JSON and save it as **`auth/client_secret.json`** (this path is what `auth/auth.py` uses).

### **2️⃣ Install Dependencies**

Use **Python 3.10 or newer**. The Google client libraries no longer support Python 3.9; on macOS the default `/usr/bin/python3` is often 3.9, so prefer a current interpreter (for example Homebrew `python@3.12`) when creating the virtual environment.

```sh
python3.12 -m venv .venv   # or: pyenv local 3.12.x && python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
```

Or install manually:

```sh
python -m pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client beautifulsoup4
```

### **3️⃣ Run the Script**

With the venv activated:

```sh
python main.py
```

This will authenticate your Gmail account, fetch recent emails, and extract transaction details.

## **Troubleshooting**

### **Python / `google.api_core` version warning**

If you see a `FutureWarning` that Python 3.9 is not supported, recreate the venv with **Python 3.10+** (see **Install Dependencies** above).

### **Gmail token errors (`EOFError`, corrupt `token.pickle`)**

`auth/token.pickle` stores your OAuth session. If it is **empty, truncated, or corrupted**, you may see `EOFError: Ran out of input` when starting the app. The auth code removes a bad file and prompts you to sign in again. You can also reset manually:

```sh
rm -f auth/token.pickle
python main.py
```

Complete the browser OAuth flow once; a new `token.pickle` will be written.

---

Check Running Processes
```sh
ps aux | grep main.py
```

Kill Running Process
```sh
pkill -f main.py
```
Database Not Updating?
```
tail -f email_log.out
```

## **How It Works**

1. **Authentication (`auth.py`)**
   - Loads `auth/token.pickle` if present and valid.
   - If credentials are missing, expired, or the pickle file is invalid, runs the Google OAuth flow (browser) and saves a new `token.pickle`.
2. **Fetching Emails (`fetch_emails.py`)**
   - Connects to Gmail API and fetches the latest 10 emails.
   - Extracts sender, subject, and email body.
3. **Parsing Emails (`parse_emails.py`)**
   - Uses `BeautifulSoup` to clean HTML.
   - Extracts links, filters for e-transfer links.
   - Extracts transaction details (amount, reference number, etc.).
4. **Send Data to AWS MySQL (`mySql_db_manipulations.py`)**
   - Uses `mysql.connector` to connect.

## **Example Output on DEBUG**

```
📩 Email from: notify@payments.interac.ca
📜 Subject: Interac e-Transfer: You've received $1,000.00
📊 Extracted Transaction Details:
   "Account Ending": ...
   "Message": ...
   "Date": ...
   "Reference Number": ... 
   "Sent From":  ...
   "Amount":  ...
   "Currency":    ...
   "Recipient Name": ...
   "Recipient Email":  ...
   "Status Message":  ...
   "Recipient Bank Name":  ...
📖 Body: JOHN SITHE your funds sent from BONNIE BASS have been automatically deposited...
🔗 E-Transfer Links:
   https://etransfer.example.com/view-transaction...

---
```

### **🚀 Summary of Updates**
| ✅ **Improvement** | ✅ **Details** |
|------------------|--------------|
| 📌 **Added EC2 Instructions** | How to run on AWS with cron jobs |
| 📌 **Added Logging & Troubleshooting** | Debugging MySQL & script issues |
| 📌 **Improved Structure & Readability** | Clear sections & easy-to-follow steps |

## **Next Steps**

- 📌 Mark emails with issues 
- 📌 Send API call if there is an issue or email or telegram 
- 📌 Send API call if there is a different email or telegram 
- 📌 Send API when work is done and is it pass or not or email or telegram 
- 📌 Handle duplicate transactions in DB
- 📌 Optimize performance using threading

## **Testing**

Install test dependencies:

```sh
pip install -r tests/requirements-test.txt
```

Run all tests:

```sh
pytest tests/unit/test_payment_access.py -v
```

With coverage:

```sh
pytest tests/unit/test_payment_access.py --cov=src.data.access.payment_access -v
```

Run a single test:

```sh
pytest tests/unit/test_payment_access.py::test_get_tenant_agreements_empty -v
```

## **GitHub / deployment secrets**

Run the app locally (activate the venv), complete OAuth once so `auth/token.pickle` exists, then base64-encode the auth files for CI or hosted secrets:

```sh
source .venv/bin/activate
```

- **`GMAIL_CLIENT_SECRET_B64`** — from `auth/client_secret.json`:

```sh
base64 < auth/client_secret.json | tr -d '\n'
```

- **`GMAIL_TOKEN_PICKLE_B64`** — from `auth/token.pickle` (after a successful local login):

```sh
base64 < auth/token.pickle | tr -d '\n'
```

## **Contributing**

Feel free to fork this project, submit issues, or suggest improvements!

## **License**

MIT License


# Git hub setup
run app localy 
then update this secrets 
GMAIL_CLIENT_SECRET_B64: 
with info based on this terminal run:
   base64 < auth/client_secret.json | tr -d '\n'
GMAIL_TOKEN_PICKLE_B64	
   base64 < auth/token.pickle | tr -d '\n'