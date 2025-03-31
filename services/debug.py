import logging
from config import LOGGING_CONFIG, DEBUG
logging.basicConfig(**LOGGING_CONFIG)

def log_dict(title, data):
    logging.debug(f"-- {title} --")
    for key, value in data.items():
        logging.debug(f"{key}: {value}")
    logging.debug("--------------------\n")

def log_debug_data(email_id, parsed, validation, headers, details):
    logging.debug(f"--- Debug Info for Email ID {email_id} ---")
    logging.debug(f"Parsed Data: {parsed}")
    logging.debug(f"Email Details: {details}")
    logging.debug(f"Validation: {validation}")
    logging.debug(f"Header Extraction: {headers}")
    logging.debug(f"--------------------------------------------------\n")


def get_all_data(email_details,result_of_validate_email,convert_email_date,result_of_extract_email_headers,parsed_data):
    logging.debug("--- All Data -----")
    logging.debug(f'Sent From: {email_details.get("Sent From") or "🚨  🚨  🚨"} ')
    logging.debug(f'sender_email aka Reply-To Email: {result_of_validate_email.get("Reply-To Email") or "🚨  🚨  🚨"}')
    logging.debug(f'Send_date: {convert_email_date(email_details.get("Date") or result_of_validate_email.get("Date")) or "🚨  🚨  🚨"}')
    logging.debug(f'Send_amount: {email_details.get("Amount", "0")}')
    logging.debug(f'Send_amount: {float(email_details.get("Amount", "0").replace(",", "")) or "🚨  🚨  🚨"}')
    logging.debug(f'currency: {email_details.get("Currency") or result_of_validate_email.get("Currency") or "🚨  🚨  🚨"}')
    logging.debug(f'sender_message: {email_details.get("Message") or "🚨  🚨  🚨"}')
    logging.debug(f'reference_number: {email_details.get("Reference Number") or "🚨  🚨  🚨"}')
    logging.debug(f'recipient_name: {email_details.get("Recipient Name") or "🚨  🚨  🚨"}')
    logging.debug(f'recipient_email: {email_details.get("Recipient Email") or result_of_extract_email_headers.get("to_email") or "🚨  🚨  🚨"}')
    logging.debug(f'status_message: {email_details.get("Status Message") or "🚨  🚨  🚨"}')
    logging.debug(f'recipient_bank_name: {email_details.get("Recipient Bank Name") or "🚨  🚨  🚨"}')
    logging.debug(f'recipient_account_ending: {email_details.get("Account Ending") or "🚨  🚨  🚨"}')
    logging.debug(f'view_in_browser_link: {parsed_data["E-Transfer Links"][0]}')
    logging.debug("--------------------------------------------------\n")