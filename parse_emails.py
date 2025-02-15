from bs4 import BeautifulSoup
import base64
import re

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
    }

    return email_details

def parse_email(email):
    """Extract subject, sender, body, and e-transfer links from email."""
    msg_id = email["id"]
    headers = email["payload"]["headers"]
    payload = email["payload"]

    # Extract Subject and Sender
    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
    sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")

    # Extract Email Body (HTML content)
    body = None
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/html":
                body_data = part["body"]["data"]
                body = base64.urlsafe_b64decode(body_data).decode("utf-8")
                break  # Stop after finding the first HTML part

    # If no HTML body was found, check for plain text
    if body is None and payload.get("body", {}).get("data"):
        body_data = payload["body"]["data"]
        body = base64.urlsafe_b64decode(body_data).decode("utf-8")

    # Parse the transaction details
    if body:
        email_details = extract_email_details(body)
    else:
        email_details = {}    

    # Parse HTML with BeautifulSoup
    filtered_links = []
    text_content = "No body found"
    if body:
        soup = BeautifulSoup(body, "html.parser")
        text_content = soup.get_text(separator="\n", strip=True)  # Extract plain text
        # Extract all links
        all_links = [a["href"] for a in soup.find_all("a", href=True)]
        # Filter links that start with "https://etransfer"
        filtered_links = [link for link in all_links if "etransfer" in link]

    # Return parsed email details
    return {
        "msg_id": msg_id,
        "Sender": sender,
        "Subject": subject,
        "Email_details": email_details,
        "E-Transfer Links": filtered_links
    }