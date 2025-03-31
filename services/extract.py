import re
from bs4 import BeautifulSoup

import logging
from config import LOGGING_CONFIG
logging.basicConfig(**LOGGING_CONFIG)

def extract_with_fallbacks(patterns, text,  group=1):
    logging.debug(f"extract: {patterns}  \n")
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                result = match.group(group).strip()
                logging.debug(f"Matched pattern: {pattern} -> {result}")
                return result
            except IndexError:
                logging.warning(f" 🚨 Pattern matched but group {group} missing: {pattern}")
    return None

def extract_amount_currency(text):
    patterns = [
        r"Amount:\s*\$([\d,]+\.\d+)\s*\((\w{3})\)",
        r"has sent you\s*\$([\d,]+\.\d+)\s*\((\w{3})\)",
        r"\$([\d,]+\.\d+)\s*\((\w{3})\)",
        r"([\d,]+\.\d+)\s*(CAD|USD|EUR)"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1), match.group(2)
    return None, None

def extract_email_details(body):#this is data from text 
    logging.debug(f"Start extracting data from the body -> \n")
    soup = BeautifulSoup(body, "html.parser")
    text_content = soup.get_text(separator="\n", strip=True)

    email_details = {
        "Account Ending": extract_with_fallbacks([
            r"Account ending in\s*(\d{4})"
        ], text_content),

        "Message": extract_with_fallbacks([
            r"Message:\s*(.+?)\n",
            r"Message:\s*(.+)"
        ], text_content),

        "Date": extract_with_fallbacks([
            r"Date:\s*(.+?)\n",
            r"Date:\s*(.+)"
        ], text_content),

        "Reference Number": extract_with_fallbacks([
            r"Reference Number:\s*([A-Za-z0-9]+)"
        ], text_content),

        "Sent From": extract_with_fallbacks([
            r"Sent From:\s*(.+?)\n",
            r"([A-Z][a-z]+\s[A-Z][a-z]+)\s+has sent you"
        ], text_content),

        "Recipient Name": extract_with_fallbacks([
            r"Hi\s+(.+?),",
            r"Hi\s+(.+?)\n"
        ], text_content),

        "Recipient Email": extract_with_fallbacks([
            r"To:\s*(.*?)\s*<([^>]+)>"
        ], text_content, group=2),

        "Status Message": extract_with_fallbacks([
            r"Funds Deposited!",
            r"has been automatically deposited"
        ], text_content),

        "Recipient Bank Name": extract_with_fallbacks([
            r"deposited into your bank account at\s+([\w\s]+)",
            r"your account at\s+([\w\s]+)"
        ], text_content),
    }

    # Amount and Currency
    amount, currency = extract_amount_currency(text_content)
    email_details["Amount"] = amount
    email_details["Currency"] = currency

    return email_details
