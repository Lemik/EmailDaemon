from fetch_emails import fetch_emails
from parse_emails import parse_email
from emails_manipulations import mark_email_read, mark_email_unread, move_email_to_folder
from config import LOGGING_CONFIG
import logging

# Configure logging
logging.basicConfig(**LOGGING_CONFIG)

if __name__ == "__main__":
    emails = fetch_emails()
    logging.info(f"📬 Fetched {len(emails)} emails.")
    if emails:
        email_ids = [email['id'] for email in emails]
        logging.info(f"Fetched Email IDs: {email_ids}")
    
    for email in emails:
        parsed_data = parse_email(email)
        
        logging.debug(f"\n ID: {parsed_data['msg_id']}")
        logging.debug(f"📩 Email from: {parsed_data['Sender']}")
        logging.debug(f"📜 Subject: {parsed_data['Subject']}")
        logging.debug("📊 Extracted Transaction Details:")
        for key, value in parsed_data['Email_details'].items():
            logging.debug(f"{key}: {value}")
        
        logging.debug("🔗 E-Transfer Links:")
        if parsed_data["E-Transfer Links"]:
            logging.debug(f'   {parsed_data["E-Transfer Links"][0]}')
        else:
            logging.debug("   No e-transfer links found.")
        logging.debug("---\n")
        
        test_email_id = parsed_data['msg_id']
        mark_email_read(test_email_id)
        move_email_to_folder(test_email_id, parsed_data['Email_details']['Sent From'])
        logging.debug("---\n")
