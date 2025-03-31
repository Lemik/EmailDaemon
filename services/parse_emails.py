from bs4 import BeautifulSoup
import base64
import re
import logging
from config import LOGGING_CONFIG
from email.utils import parseaddr
from services.helpers import extract_html_body
from services.extract import extract_email_details

logging.basicConfig(**LOGGING_CONFIG)

def parse_email(email):
    """Extract subject, sender, body, and e-transfer links from email."""
    msg_id = email["id"]
    headers = email["payload"]["headers"]
    payload = email["payload"]
    logging.debug(f" PARSE EMAIL -->")
    logging.debug(f"msg_id: {msg_id:}")
    #logging.debug(f"headers: {headers:}")
    #logging.debug(f"payload: {payload:}")

    # Extract Subject and Sender
    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
    sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")

    logging.debug(f"subject: {subject:}")
    logging.debug(f"sender: {sender:}")

    # Extract Email Body (HTML content)
    body = None
    if "parts" in payload:
        for part in payload["parts"]:
            body = extract_html_body(part)
            if body:
                logging.debug(f"body found in payload: {body}")
                break 

    #logging.debug(f"BODY: {body}")
    # If no HTML body was found, check for plain text
    if body is None and payload.get("body", {}).get("data"):
        body_data = payload["body"]["data"]
        body = base64.urlsafe_b64decode(body_data).decode("utf-8")
        logging.debug(f"body decode: {body}")

    
    # Parse the transaction details
    if body:
        email_details = extract_email_details(body)
        logging.debug(f"Body found: lets's see body:\n {body} \n")
        logging.debug(f"Body found: lets's see email_details:\n {email_details} \n")
    else:
        email_details = {}    
        logging.debug(f"❌  no Body: {body}")

    # Parse HTML with BeautifulSoup
    filtered_links = []
    text_content = "No body found"
    if body:
        soup = BeautifulSoup(body, "html.parser")
        text_content = soup.get_text(separator="\n", strip=True)
        # Extract all links
        all_links = [a["href"] for a in soup.find_all("a", href=True)]
        filtered_links = [link for link in all_links if "etransfer" in link]

    return {
        "msg_id": msg_id,
        "Sender": sender,
        "Subject": subject,
        "Email_details": email_details,
        "E-Transfer Links": filtered_links,
        "text_content": text_content
    }

def extract_header_value(headers, key):
    """Helper function to extract a specific header's value."""
    for header in headers:
        if header['name'].lower() == key.lower():
            return header['value']
    return None

def extract_authentication_data(headers):
    """Extract structured email authentication data from headers."""
    from_header = extract_header_value(headers, "From")
    reply_to_header = extract_header_value(headers, "Reply-To")
    date = extract_header_value(headers, "Date")
    auth_results = extract_header_value(headers, "Authentication-Results")
    
    from_name, from_email = parseaddr(from_header)
    reply_to_name, reply_to_email = parseaddr(reply_to_header) if reply_to_header else (None, None)

    return {
        "From Email": from_email,
        "From Name": from_name,
        "Reply-To Email": reply_to_email,
        "Date": date,
        "Authentication-Results": auth_results
    }


def extract_email_headers(headers):
    def get_value(name):
        for h in headers:
            if h['name'].lower() == name.lower():
                return h['value']
        return None

    to, to_email = parseaddr(get_value("To"))
    from_name, from_email = parseaddr (get_value("From"))
    reply_to, reply_to_email = parseaddr (get_value("Reply-To"))

    return {
        "to": to,
        "to_email": to_email,
        "from": from_name,
        "from_email": from_email,
        "reply_to": reply_to,
        "reply_to_email": reply_to_email,
        "subject": get_value("Subject"),
        "date": get_value("Date"),
        "x_date": get_value("X-Date"),
        "payment_key": get_value("X-PaymentKey"),
        "payment_id": get_value("X-Payment-Notification"),
        "message_type": get_value("X-MessageType"),
        "message_id": get_value("Message-ID"),
    }
