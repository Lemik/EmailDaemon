import argparse
import logging
from services.fetch_emails import fetch_emails
from services.parse_emails import parse_email, extract_authentication_data, extract_email_headers
from db.mySql_db_manipulations import insert_email_data
from services.helpers import validate_authentication_results, get_data_ready_for_db, log_suspicious_email
from services.debug import log_dict
from config import LOGGING_CONFIG

logging.basicConfig(**LOGGING_CONFIG)

def fetch_email_by_id(email_id):
    all_emails = fetch_emails()
    for email in all_emails:
        logging.info(f"email: {email['id']}")
        if email['id'] == email_id:
            return email
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Debug a specific email by ID.")
    parser.add_argument("email_id", help="The ID of the email to debug")
    parser.add_argument("-u", "--update", action="store_true", help="Update database with parsed email data")
    args = parser.parse_args()

    email = fetch_email_by_id(args.email_id)

    if not email:
        logging.error(f"❌ Email with ID {args.email_id} not found.")
        exit(1)

    logging.info(f"🔍 Debugging Email ID: {args.email_id}")
    
    # Step 1: Authentication
    auth_data = extract_authentication_data(email["payload"]["headers"])
    validation_result = validate_authentication_results(auth_data)
    header_data = extract_email_headers(email["payload"]["headers"])

    # Step 2: Parsing
    parsed_data = parse_email(email)
    email_details = parsed_data["Email_details"]
    msg_id = parsed_data["msg_id"]

    # Log everything
    log_dict("auth_data", auth_data)
    log_dict("validation_result", validation_result)
    log_dict("header_data", header_data)
    log_dict("parsed_data", parsed_data)
    log_dict("email_details", email_details)

    # Step 3: Optional DB Update
    if args.update:
        logging.info("📝 --update flag passed. Attempting to write to DB...")
        try:
            db_data = get_data_ready_for_db(msg_id, validation_result, header_data, email_details, parsed_data)
            result = insert_email_data(**db_data)
            if result:
                logging.info("✅ Email data inserted/updated successfully.")
            else:
                logging.error("❌ Failed to insert/update email data.")
        except Exception as e:
            logging.error(f"🚨 DB update error: {e}")
