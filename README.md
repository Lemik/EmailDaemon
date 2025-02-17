# 📩 Gmail Email Fetcher & Parser

## **Overview**

This Python project fetches recent emails from Gmail using the Gmail API, extracts relevant details from HTML-formatted emails, and parses transaction data such as e-transfer details. 

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
✅ Stores parsed data** in an AWS MySQL database
✅ Marks emails as read** and moves them to a specified folder
✅ Runs automatically on an EC2 instance** using a cron job

## **Project Structure**

```
📁 email-daemon/
 ├── auth/
 │   ├── client_secret.json  # Google API credentials
 │   ├── auth.py  # Handles Gmail authentication
 │
 ├── db/
 │   ├── mySql_db_manipulations.py  # MySQL connection & inserts
 │
 ├── fetch_emails.py  # Fetches emails using Gmail API
 ├── parse_emails.py  # Extracts details from HTML email body
 ├── emails_manipulations.py  # Marks emails as read/moves them
 ├── config.py  # Configuration (DB, logging, API scopes)
 ├── main.py  # Main script execution
 ├── requirements.txt  # Required Python packages
 ├── README.md  # Documentation

```

## **Setup & Installation**

### **1️⃣ Enable Gmail API & Get Credentials**

1. **Go to** [Google API Console](https://console.cloud.google.com/)
2. Enable **Gmail API** for your Google account
3. Create OAuth credentials (OAuth Client ID)
4. Download `credentials.json` and place it in the project root

### **2️⃣ Install Dependencies**

Ensure you have Python 3 installed, then run:

```sh
python3 -m pip install -r requirements.txt
```

Or install manually:

```sh
python3 -m pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client beautifulsoup4
```

### **3️⃣ Run the Script**

```sh
python3 main.py
```

This will authenticate your Gmail account, fetch recent emails, and extract transaction details.

## **Troubleshooting**

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

1. **Authentication (********`auth.py`********\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*)**
   - Checks if `token.pickle` exists to reuse credentials.
   - If not, prompts the user to log in via OAuth2.
2. **Fetching Emails (********`fetch_emails.py`********\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*)**
   - Connects to Gmail API and fetches the latest 10 emails.
   - Extracts sender, subject, and email body.
3. **Parsing Emails (********`parse_emails.py`********\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*)**
   - Uses `BeautifulSoup` to clean HTML.
   - Extracts links, filters for e-transfer links.
   - Extracts transaction details (amount, reference number, etc.).
4. **Send Data to AWS MYSQL (********`mySql_db_manipulations.py`********\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*)**
   - Uses `mysql.connector` to connect.

## **Example Output**

```
📩 Email from: notify@payments.interac.ca
📜 Subject: Interac e-Transfer: You've received $1,000.00
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

## **Contributing**

Feel free to fork this project, submit issues, or suggest improvements!

## **License**

MIT License

