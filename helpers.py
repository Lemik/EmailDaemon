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
        "%b %d, %Y"                          # e.g., Feb 28, 2025
        
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