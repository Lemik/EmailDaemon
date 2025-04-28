from datetime import datetime
import base64
import logging
from config import LOGGING_CONFIG
logging.basicConfig(**LOGGING_CONFIG)

def convert_email_date(date_str):
    """Convert email date format to MySQL-compatible DATETIME format."""
    logging.debug(f"HELPERS - > date_str: {date_str}")
    
    # List of possible formats
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",          # e.g., Sat, 1 Mar 2025 23:22:06 +0000
        "%a, %b %d, %Y at %I:%M %p",         # e.g., Sat, Mar 1, 2025 at 11:03 PM
        "%B %d, %Y",                         # e.g., March 1, 2025
        "%b %d, %Y",                         # e.g.,  Feb 28, 2025
        "YYYY-MM-DD HH:MM:SS.ssssss",        # e.g., 2025-03-01 23:22:06.123456
        
    ]
    
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            return parsed_date.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

    logging.warning(f"🚨 Date conversion failed for {date_str}")
    return None
    
def log_suspicious_email(emailID):
    """Logs suspicious emails to console """
    logging.info(f"🚨🚨🚨 Suspicious email logged! {emailID} 🚨🚨🚨")

def extract_html_body(part):
    """Recursively extract HTML body from email parts."""
    if part.get("mimeType") == "text/html":
        body_data = part["body"].get("data")
        if body_data:
            return base64.urlsafe_b64decode(body_data).decode("utf-8")

    # If the part has sub-parts, search inside them
    for subpart in part.get("parts", []):
        result = extract_html_body(subpart)
        if result:
            return result
    return None

def validate_authentication_results(auth_data):
    """Checks SPF, DKIM, and DMARC from auth results and returns legitimacy."""
    auth_results = auth_data.get("Authentication-Results", "")

    return {
        "SPF Pass": "spf=pass" in auth_results,
        "DKIM Pass": "dkim=pass" in auth_results,
        "DMARC Pass": "dmarc=pass" in auth_results,
        "Likely Legitimate": all([
            "spf=pass" in auth_results,
            "dkim=pass" in auth_results,
            "dmarc=pass" in auth_results
        ])
    }

def get_data_ready_for_db(email_id, validation, headers, details, parsed):
    logging.debug(f"get_data_ready_for_db  ->\n")
    data_to_insert = {
            "id": email_id,
            "sender_name":  details.get("Sent From") or "Unknown",
            "sender_email": validation.get("Reply-To Email") or headers.get('reply_to_email') or None,
            "send_date": convert_email_date(details.get("Date") or validation.get("Date") or "Unknown"),
            "send_amount": float(details.get("Amount", "0").replace(",", "")) if details.get("Amount") else 0.0,
            "currency": details.get("Currency", "Unknown"),
            "sender_message": details.get("Message", "No message"),
            "reference_number": details.get("Reference Number", "Unknown"),
            "recipient_name": details.get("Recipient Name", "Unknown"),
            "recipient_email": details.get("Recipient Email") or headers.get("to_email") or "Unknown",
            "status_message": details.get("Status Message", "Unknown"),
            "recipient_bank_name": details.get("Recipient Bank Name", "Unknown"),
            "recipient_account_ending": details.get("Account Ending", "Unknown"),
            "view_in_browser_link": parsed["E-Transfer Links"][0] if parsed["E-Transfer Links"] else None
        }
    logging.debug(f"-----------\n")
    return data_to_insert