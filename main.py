from services.fetch_emails import fetch_emails
from services.parse_emails import parse_email, validate_email, extract_email_info
from services.emails_manipulations import mark_email_read, move_email_to_folder, mark_email_starred,remove_inbox_label
from db.mySql_db_manipulations import insert_email_data
from config import LOGGING_CONFIG, DEBUG
import logging
from helpers import convert_email_date, log_suspicious_email

logging.basicConfig(**LOGGING_CONFIG)
    
if __name__ == "__main__":
# Step 1: Fetch a list of emails
    emails = fetch_emails()
    logging.info(f"📬 Fetched {len(emails)} emails.")

# Step 2: Get all Email IDs
    if emails:
        email_ids = [email['id'] for email in emails]
        logging.info(f"Fetched Email IDs: {email_ids}")

# Step 3: Parse every Email
    for email in emails:
        try:
# Step 3.1: Validate suspicious emails
            result_of_validate_email = validate_email(email["payload"]["headers"])
            result_of_extract_email_info = extract_email_info(email["payload"]["headers"])
            
# Step 3.2 Ignore / Log suspicious emails
            if not result_of_validate_email["Likely Legitimate"]:
                log_suspicious_email(email['id'])
            else:
                logging.info(f"✅ Email is likely legitimate")
# Step 3.3: Parse
            parsed_data = parse_email(email)
            
# Step 3.4: Check if subject contains "Interac e-Transfer" Mark it with Star if it's not related to interac e-transfer
            email_subject = parsed_data.get("Subject", "").strip()
            test_email_id = parsed_data["msg_id"]
            if "interac e-transfer" not in email_subject.lower():
                logging.warning(f"❌ Email {test_email_id} does not contain 'Interac e-Transfer' in the subject.")
                mark_email_starred(test_email_id) 
                mark_email_read(test_email_id)
                continue 
            
# Step 3.5: Debug 
            logging.debug("--- Debug --- \n")      
            logging.debug(f"\n ID: {test_email_id}")
            logging.debug(f"📩 Email from: {parsed_data['Sender']}")
            logging.debug(f"📜 Subject: {email_subject}")
            logging.debug("📊 Extracted Transaction Details:")

            email_details = parsed_data["Email_details"]
            if(logging.debug):
                logging.debug("-- parsed_data  -- \n")
                for key, value in parsed_data.items():
                    logging.debug(f"{key}: {value}")
                logging.debug("--------------------  \n")

                logging.debug("-- email_details  -- \n")
                for key, value in email_details.items():
                    logging.debug(f"{key}: {value}")
                logging.debug("--------------------  \n")

                logging.debug("-- result_of_validate_email  -- \n")
                for key, value in result_of_validate_email.items():
                    logging.debug(f"{key}: {value}")
                logging.debug("--------------------  \n")

                logging.debug("-- result_of_extract_email_info  -- \n")
                for key, value in result_of_extract_email_info.items():
                    logging.debug(f"{key}: {value}")
                logging.debug("--------------------  \n")

            logging.debug("--- All Data -----")
            logging.debug(f'Sent From: {email_details.get("Sent From") or "🚨  🚨  🚨"} ')
            logging.debug(f'sender_email aka Reply-To Email: {result_of_validate_email.get("Reply-To Email") or "🚨  🚨  🚨"}')
            logging.debug(f'Send_date: {convert_email_date(email_details.get("Date") or result_of_validate_email.get("Date")) or "🚨  🚨  🚨"}')
            logging.debug(f'Send_amount: {float(email_details.get("Amount", "0").replace(",", "")) or "🚨  🚨  🚨"}')
            logging.debug(f'currency: {email_details.get("Currency") or result_of_validate_email.get("Currency") or "🚨  🚨  🚨"}')
            logging.debug(f'sender_message: {email_details.get("Message") or "🚨  🚨  🚨"}')
            logging.debug(f'reference_number: {email_details.get("Reference Number") or "🚨  🚨  🚨"}')
            logging.debug(f'recipient_name: {email_details.get("Recipient Name") or "🚨  🚨  🚨"}')
            logging.debug(f'recipient_email: {email_details.get("Recipient Email") or result_of_extract_email_info.get("to_email") or "🚨  🚨  🚨"}')
            logging.debug(f'status_message: {email_details.get("Status Message") or "🚨  🚨  🚨"}')
            logging.debug(f'recipient_bank_name: {email_details.get("Recipient Bank Name") or "🚨  🚨  🚨"}')
            logging.debug(f'recipient_account_ending: {email_details.get("Account Ending") or "🚨  🚨  🚨"}')
            logging.debug(f'view_in_browser_link: {parsed_data["E-Transfer Links"][0]}')
            logging.debug("--------------------------------------------------\n")
            
            logging.debug("🔗 E-Transfer Links:")
            if(logging.debug):
                if parsed_data["E-Transfer Links"]:
                    logging.debug(f'{parsed_data["E-Transfer Links"][0]}')
                else:
                    logging.debug("No e-transfer links found.")
            logging.debug("---\n")


            sender_name = email_details.get("Sent From") or "Unknown"
# Step 3.6: MySQL insertion
# Ensure default values for required fields to avoid NULL errors
            insert_success = False
            #if not DEBUG:
                
            try:
                    insert_result = insert_email_data(
                        id = test_email_id,
                        sender_name = sender_name,
                        sender_email= result_of_validate_email.get("Reply-To Email","Unknown"),
                        send_date = convert_email_date(email_details.get("Date") or result_of_validate_email.get("Date") or "Unknown"),
                        send_amount=float(email_details.get("Amount", "0").replace(",", "")) if email_details.get("Amount") else 0.0,
                        currency=email_details.get("Currency", "Unknown"),
                        sender_message=email_details.get("Message", "No message"),
                        reference_number=email_details.get("Reference Number", "Unknown"),
                        recipient_name = email_details.get("Recipient Name", "Unknown"),
                        recipient_email= (email_details.get("Recipient Email") or result_of_extract_email_info.get("to_email") or "Unknown"),
                        status_message=email_details.get("Status Message", "Unknown"),
                        recipient_bank_name=email_details.get("Recipient Bank Name", "Unknown"),
                        recipient_account_ending=email_details.get("Account Ending", "Unknown"),
                        view_in_browser_link=parsed_data["E-Transfer Links"][0] if parsed_data["E-Transfer Links"] else None
                    )
                    if (insert_result != None) :
                        logging.info(f"✅ Data inserted for Reference #: {email_details.get('Reference Number', 'Unknown')}")
                        logging.debug(f"---\n insert_email_data: {insert_email_data} ---\n")
                        insert_success = True
                    else:
                        logging.error(f"❌ Data wasn't inserted {test_email_id}")
                        insert_success = False

            except Exception as e:
                        logging.error(f"❌ Failed to insert email data for ID {test_email_id}: {e}")
                        insert_success = False

            #Only mark the email as read & move it if it was successfully inserted
            if insert_success:
                mark_email_read(test_email_id)
                move_email_to_folder(test_email_id, sender_name)
                remove_inbox_label(test_email_id)
                logging.info(f"📥 Email {test_email_id} marked as read and moved.")
            else:
                logging.warning(f"❌ Email {test_email_id} was NOT marked as read/moved due to DB failure.")
                mark_email_starred(test_email_id)  # ⭐ Mark email with a star if DB insertion fails

        except Exception as e:
            logging.error(f"🚨 Unexpected error processing email {email.get('id', 'Unknown')}: {e}")
            continue  # Ensure processing continues with the next email

        logging.debug("---\n")
