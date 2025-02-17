from fetch_emails import fetch_emails
from parse_emails import parse_email
from datetime import datetime
from emails_manipulations import mark_email_read, move_email_to_folder
from db.mySql_db_manipulations import insert_email_data
from config import LOGGING_CONFIG
import logging

logging.basicConfig(**LOGGING_CONFIG)


def convert_email_date(date_str):
    """Convert email date format to MySQL-compatible DATETIME format."""
    try:
        return datetime.strptime(date_str, "%a, %b %d, %Y at %I:%M %p").strftime("%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        logging.warning(f"⚠️ Date conversion failed for {date_str}: {e}")
        return None  # Return None if date parsing fails
    
if __name__ == "__main__":
    emails = fetch_emails()
    logging.info(f"📬 Fetched {len(emails)} emails.")

    if emails:
        email_ids = [email['id'] for email in emails]
        logging.info(f"Fetched Email IDs: {email_ids}")

    for email in emails:
        parsed_data = parse_email(email)
        email_details = parsed_data["Email_details"]

        logging.debug(f"\n ID: {parsed_data['msg_id']}")
        logging.debug(f"📩 Email from: {parsed_data['Sender']}")
        logging.debug(f"📜 Subject: {parsed_data['Subject']}")

        logging.debug("📊 Extracted Transaction Details:")
        for key, value in email_details.items():
            logging.debug(f"{key}: {value}")

        logging.debug("🔗 E-Transfer Links:")
        if parsed_data["E-Transfer Links"]:
            logging.debug(f'   {parsed_data["E-Transfer Links"][0]}')
        else:
            logging.debug("   No e-transfer links found.")

        logging.debug("---\n")

        test_email_id = parsed_data['msg_id']

        # Extract relevant fields for MySQL insertion
        insert_success = False
        try:
            insert_email_data(
                id=test_email_id,
                sender_name=email_details.get("Sent From", "Unknown"),
                send_date=convert_email_date(email_details.get("Date", "Unknown")),
                send_amount=float(email_details.get("Amount", "0").replace(",", "")) if email_details.get("Amount") else 0.0,
                currency=email_details.get("Currency", "Unknown"),
                sender_message=email_details.get("Message", "No message"),
                reference_number=email_details.get("Reference Number", "Unknown"),
                recipient_name=email_details.get("Recipient Name", "Unknown"),
                recipient_email=email_details.get("Recipient Email", "Unknown"),
                status_message=email_details.get("Status Message", "Unknown"),
                recipient_bank_name=email_details.get("Recipient Bank Name", "Unknown"),
                recipient_account_ending=email_details.get("Account Ending", "Unknown"),
                view_in_browser_link=parsed_data["E-Transfer Links"][0] if parsed_data["E-Transfer Links"] else None
            )
            logging.info(f"✅ Data inserted for Reference #: {email_details.get('Reference Number', 'Unknown')}")
            insert_success = True

        except Exception as e:
            logging.error(f"❌ Failed to insert email data: {e}")
            insert_success = False

        # ✅ Only mark the email as read & move it if it was successfully inserted
        if insert_success:
            mark_email_read(test_email_id)
            move_email_to_folder(test_email_id, email_details.get("Sent From", "Unknown"))
            logging.info(f"📥 Email {test_email_id} marked as read and moved.")
        else:
            logging.warning(f"❌ Email {test_email_id} was NOT marked as read/moved due to DB failure.")

        logging.debug("---\n")
