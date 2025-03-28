from bs4 import BeautifulSoup
import base64
import re
import logging
from config import LOGGING_CONFIG
from email.utils import parseaddr
from helpers import extract_html_body


logging.basicConfig(**LOGGING_CONFIG)

def extract_email_details(body):
    """Extract important details from the email body."""
    
    soup = BeautifulSoup(body, "html.parser")
    text_content = soup.get_text(separator="\n", strip=True)  # Convert HTML to plain text
    
    # Extract data using regular expressions
    extracted_data = {
        "account_ending": re.search(r"Account ending in\s*(\d{4})", text_content),
        "message": re.search(r"Message:\s*(.+)", text_content),
        "date": re.search(r"Date:\s*(.+)", text_content),
        "reference_number": re.search(r"Reference Number:\s*([A-Za-z0-9]+)", text_content),
        "sent_from": re.search(r"Sent From:\s*(.+)", text_content),
        "amount_currency": re.search(r"Amount:\s*\$([\d,]+\.\d+)\s*\((\w{3})\)", text_content),
        "recipient_name": re.search(r"Hi\s+(.+?),", text_content),  
        "recipient_email": re.search(r"To:\s*(.*?)\s*<([^>]+)>", text_content),
        "status_message": re.search(r"Funds Deposited!", text_content), 
        "recipient_bank_name": re.search(r"deposited into your account at\s+([\w\s]+)", text_content)
}

    # Process extracted values and handle None cases
    email_details = {
        "Account Ending": extracted_data["account_ending"].group(1) if extracted_data["account_ending"] else None,
        "Message": extracted_data["message"].group(1) if extracted_data["message"] else None,
        "Date": extracted_data["date"].group(1) if extracted_data["date"] else None,
        "Reference Number": extracted_data["reference_number"].group(1) if extracted_data["reference_number"] else None,
        "Sent From": extracted_data["sent_from"].group(1) if extracted_data["sent_from"] else None,
        "Amount": extracted_data["amount_currency"].group(1) if extracted_data["amount_currency"] else None,
        "Currency": extracted_data["amount_currency"].group(2) if extracted_data["amount_currency"] else None,
        "Recipient Name": extracted_data["recipient_name"].group(1) if extracted_data["recipient_name"] else None,
        "Recipient Email": extracted_data["recipient_email"].group(2) if extracted_data["recipient_email"] else None,
        "Status Message": extracted_data["status_message"].group(0) if extracted_data["status_message"] else None,
        "Recipient Bank Name": extracted_data["recipient_bank_name"].group(1) if extracted_data["recipient_bank_name"] else None,
    }

    return email_details

def parse_email(email):
    """Extract subject, sender, body, and e-transfer links from email."""
    msg_id = email["id"]
    headers = email["payload"]["headers"]
    payload = email["payload"]
    logging.debug(f" PARSE EMAIL -->")
    logging.debug(f"msg_id: {msg_id:}")
    #logging.debug(f"headers: {headers:}")
    logging.debug(f"payload: {payload:}")

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

    logging.debug(f" <---- parse_email --")
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

def validate_email(headers):
    """Validates an email using SPF, DKIM, DMARC, and header consistency checks."""
    
    # Extract relevant headers
    from_header = extract_header_value(headers, "From")
    reply_to_header = extract_header_value(headers, "Reply-To")
    date = extract_header_value(headers, "date")
    #return_path_header = extract_header_value(headers, "Return-Path")
    authentication_results = extract_header_value(headers, "Authentication-Results")
    
    # Parse email addresses
    from_name, from_email = parseaddr(from_header)
    reply_to_name, reply_to_email = parseaddr(reply_to_header) if reply_to_header else (None, None)
   # return_path_email = parseaddr(return_path_header)[1] if return_path_header else None
    
    # Check SPF, DKIM, DMARC in Authentication-Results
    spf_pass = "spf=pass" in authentication_results if authentication_results else False
    dkim_pass = "dkim=pass" in authentication_results if authentication_results else False
    dmarc_pass = "dmarc=pass" in authentication_results if authentication_results else False
    
    # Suspicious conditions
   # header_mismatch = from_email != return_path_email  # Possible spoofing
    #reply_to_mismatch = reply_to_email and from_email.split('@')[-1] != reply_to_email.split('@')[-1]  # Reply-To different domain
    
    # Validation Results
    results = {
        "From Email": from_email,
        "From Name": from_name,
        "Reply-To Email": reply_to_email,
       # "Return-Path Email": return_path_email,
        "SPF Pass": spf_pass,
        "DKIM Pass": dkim_pass,
        "DMARC Pass": dmarc_pass,
        "Date": date,
    #    "Header Consistency": not header_mismatch,
    #    "Reply-To Spoofing": reply_to_mismatch,
        "Likely Legitimate": all([spf_pass, dkim_pass, dmarc_pass])
    }

    logging.debug(f"validate_email: {results}  \n")
    return results

def extract_email_info(headers):
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
