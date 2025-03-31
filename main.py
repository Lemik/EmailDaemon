from services.fetch_emails import fetch_emails
from services.parse_emails import parse_email, extract_authentication_data, extract_email_headers
from services.emails_manipulations import mark_email_read, move_email_to_folder, mark_email_starred,remove_inbox_label
from db.mySql_db_manipulations import insert_email_data
from debug import log_debug_data, log_dict, get_all_data
from config import LOGGING_CONFIG, DEBUG
import logging
from helpers import convert_email_date, log_suspicious_email,validate_authentication_results,get_data_ready_for_db

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
            auth_data = extract_authentication_data(email["payload"]["headers"])
            result_of_validate_email = validate_authentication_results(auth_data)
            merge_data = {**auth_data, **result_of_validate_email}
            logging.debug(f"auth_data:\n {merge_data}")
            result_of_extract_email_headers = extract_email_headers(email["payload"]["headers"])
            
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
            email_details = parsed_data["Email_details"]
            if(logging.debug):
                logging.debug("--- Debug --- \n")      
                logging.debug(f"\n ID: {test_email_id}")
                logging.debug(f"📩 Email from: {parsed_data['Sender']}")
                logging.debug(f"📜 Subject: {email_subject}")
                logging.debug("📊 Extracted Transaction Details:")

                log_dict('parsed_data',parsed_data)
                log_dict('email_details',email_details)
                log_dict('result_of_validate_email',result_of_validate_email)
                log_dict('result_of_extract_email_headers',result_of_extract_email_headers)
               
            logging.debug("🔗 E-Transfer Links:")
            if(logging.debug):
                if parsed_data["E-Transfer Links"]:
                    logging.debug(f'{parsed_data["E-Transfer Links"][0]}')
                else:
                    logging.debug("No e-transfer links found.")
            logging.debug("---\n")

# Step 3.6: MySQL insertion
# Ensure default values for required fields to avoid NULL errors
            insert_success = False
            
            data_for_db = get_data_ready_for_db(test_email_id, result_of_validate_email, result_of_extract_email_headers, email_details, parsed_data)
            log_dict("All Data", data_for_db)
           
            try:
                    insert_result = insert_email_data(**data_for_db)

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
                move_email_to_folder(test_email_id, data_for_db['sender_name'])
                remove_inbox_label(test_email_id)
                logging.info(f"📥 Email {test_email_id} marked as read and moved.")
            else:
                logging.warning(f"❌ Email {test_email_id} was NOT marked as read/moved due to DB failure.")
                mark_email_starred(test_email_id)  # ⭐ Mark email with a star if DB insertion fails

        except Exception as e:
            logging.error(f"🚨 Unexpected error processing email {email.get('id', 'Unknown')}: {e}")
            continue  # Ensure processing continues with the next email

        logging.debug("---\n")
