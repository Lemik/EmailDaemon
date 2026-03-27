#!/usr/bin/env python3
"""
Daily Email Processing Job
Processes emails and saves transaction data to database.
Designed for automated execution via cron.
"""

import sys
import os
import logging
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from services.fetch_emails import fetch_emails
from services.parse_emails import parse_email, extract_authentication_data, extract_email_headers
from services.emails_manipulations import mark_email_read, move_email_to_folder, mark_email_starred, remove_inbox_label
from db.mySql_db_manipulations import insert_email_data, log_email_error, start_job_execution, complete_job_execution, update_job_execution
from services.debug import log_debug_data, log_dict, get_all_data
from config import LOGGING_CONFIG, DEBUG
from services.helpers import convert_email_date, log_suspicious_email, validate_authentication_results, get_data_ready_for_db


def setup_job_logging():
    """Setup logging configuration for scheduled job execution."""
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Create daily log file
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"email_job_{today}.log"
    
    # Configure logging to both file and console
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return log_file


def process_emails():
    """Main email processing function with enhanced error handling."""
    start_time = datetime.now()
    processed_count = 0
    success_count = 0
    error_count = 0
    emails_fetched = 0
    error_details = []
    
    logging.info("🚀 Starting daily email processing job")
    logging.info(f"📅 Job started at: {start_time}")
    
    # Start job tracking in database
    job_id = start_job_execution()
    if not job_id:
        logging.warning("⚠️ Could not start job tracking in database")
    
    try:
        # Step 1: Fetch emails
        emails = fetch_emails()
        emails_fetched = len(emails)
        logging.info(f"📬 Fetched {emails_fetched} emails for processing")
        
        # Update job with fetched count
        if job_id:
            update_job_execution(job_id, "PROCESSING", emails_fetched=emails_fetched)
        
        if not emails:
            logging.info("📭 No emails to process")
            # Complete job tracking
            if job_id:
                complete_job_execution(job_id, "SUCCESS", emails_fetched=0, emails_processed=0, 
                                     successful_transactions=0, failed_transactions=0, 
                                     errors_encountered=0, start_time=start_time)
            return {"processed": 0, "success": 0, "errors": 0}
        
        # Step 2: Get all Email IDs
        email_ids = [email['id'] for email in emails]
        logging.info(f"📋 Email IDs to process: {email_ids}")
        
        # Step 3: Process each email
        for email in emails:
            processed_count += 1
            email_id = email.get('id', 'Unknown')
            
            try:
                logging.info(f"🔄 Processing email {processed_count}/{len(emails)}: {email_id}")
                
                # Step 3.1: Validate authentication
                auth_data = extract_authentication_data(email["payload"]["headers"])
                result_of_validate_email = validate_authentication_results(auth_data)
                merge_data = {**auth_data, **result_of_validate_email}
                logging.debug(f"🔐 Auth data: {merge_data}")
                result_of_extract_email_headers = extract_email_headers(email["payload"]["headers"])
                
                # Step 3.2: Handle suspicious emails
                if not result_of_validate_email["Likely Legitimate"]:
                    logging.warning(f"🚨 Suspicious email detected: {email_id}")
                    log_suspicious_email(email_id)
                else:
                    logging.debug(f"✅ Email {email_id} appears legitimate")
                
                # Step 3.3: Parse email
                parsed_data = parse_email(email)
                
                # Step 3.4: Check for Interac e-Transfer
                email_subject = parsed_data.get("Subject", "").strip()
                test_email_id = parsed_data["msg_id"]
                
                if "interac e-transfer" not in email_subject.lower():
                    logging.warning(f"❌ Email {test_email_id} is not an Interac e-Transfer")
                    logging.warning(f"❌ Subject: {email_subject}")
                    logging.warning(f"❌ From: {parsed_data['Sender']}")
                    
                    # Log the error
                    try:
                        log_email_error(
                            id=test_email_id,
                            subject=email_subject,
                            send_from=parsed_data['Sender'],
                            send_date=datetime.now(),
                            error_message="Email does not contain 'Interac e-Transfer' in subject",
                            raw_email=str(parsed_data)
                        )
                    except Exception as log_error:
                        logging.error(f"❌ Failed to log email error for {test_email_id}: {log_error}")
                    
                    # Mark and skip
                    mark_email_starred(test_email_id)
                    mark_email_read(test_email_id)
                    error_count += 1
                    continue
                
                # Step 3.5: Process valid Interac e-Transfer
                email_details = parsed_data["Email_details"]
                logging.debug(f"💰 Processing Interac e-Transfer: {email_details.get('Reference Number', 'Unknown')}")
                
                # Debug logging
                if DEBUG:
                    logging.debug("🐛 Debug information:")
                    log_dict('parsed_data', parsed_data)
                    log_dict('email_details', email_details)
                    log_dict('validation_result', result_of_validate_email)
                    log_dict('header_data', result_of_extract_email_headers)
                
                # Step 3.6: Database insertion
                insert_success = False
                data_for_db = get_data_ready_for_db(
                    test_email_id, 
                    result_of_validate_email, 
                    result_of_extract_email_headers, 
                    email_details, 
                    parsed_data
                )
                
                try:
                    insert_result = insert_email_data(**data_for_db)
                    
                    if insert_result is not None:
                        reference = email_details.get('Reference Number', 'Unknown')
                        logging.info(f"✅ Successfully inserted data for Reference #{reference}")
                        insert_success = True
                        success_count += 1
                    else:
                        logging.error(f"❌ Failed to insert data for email {test_email_id}")
                        error_count += 1
                
                except Exception as e:
                    error_msg = f"Database insertion error for {test_email_id}: {e}"
                    logging.error(f"❌ {error_msg}")
                    error_details.append(error_msg)
                    error_count += 1
                
                # Step 3.7: Email management
                if insert_success:
                    mark_email_read(test_email_id)
                    move_email_to_folder(test_email_id, data_for_db['sender_name'])
                    remove_inbox_label(test_email_id)
                    logging.info(f"📥 Email {test_email_id} processed and archived")
                else:
                    logging.warning(f"⭐ Email {test_email_id} marked with star due to processing failure")
                    mark_email_starred(test_email_id)
                
            except Exception as e:
                error_msg = f"Unexpected error processing email {email_id}: {e}"
                logging.error(f"🚨 {error_msg}")
                error_details.append(error_msg)
                error_count += 1
                continue
    
    except Exception as e:
        error_msg = f"Critical error in email processing job: {e}" 
        logging.error(f"🚨 {error_msg}")
        error_details.append(error_msg)
        error_count += 1
    
    # Job summary and database completion
    end_time = datetime.now()
    duration = end_time - start_time
    
    # Determine job status
    if error_count == 0:
        job_status = "SUCCESS"
    elif success_count > 0:
        job_status = "PARTIAL_SUCCESS"
    else:
        job_status = "FAILED"
    
    # Complete job tracking in database
    if job_id:
        failed_transactions = processed_count - success_count
        error_details_str = "; ".join(error_details[-10:]) if error_details else None  # Keep last 10 errors
        complete_job_execution(
            job_id, job_status, emails_fetched=emails_fetched, emails_processed=processed_count,
            successful_transactions=success_count, failed_transactions=failed_transactions,
            errors_encountered=error_count, error_details=error_details_str, start_time=start_time
        )
    
    logging.info("📊 Job Summary:")
    logging.info(f"⏱️  Duration: {duration}")
    logging.info(f"📬 Total emails fetched: {emails_fetched}")
    logging.info(f"📧 Total emails processed: {processed_count}")
    logging.info(f"✅ Successful transactions: {success_count}")
    logging.info(f"❌ Errors encountered: {error_count}")
    logging.info(f"🏁 Job completed at: {end_time}")
    
    return {
        "processed": processed_count,
        "success": success_count,
        "errors": error_count,
        "duration": str(duration),
        "job_id": job_id
    }


def main():
    """Main entry point for the daily job."""
    try:
        # Setup logging
        log_file = setup_job_logging()
        logging.info(f"📝 Logging to: {log_file}")
        
        # Run email processing
        results = process_emails()
        
        # Exit with appropriate code
        if results["errors"] > 0:
            logging.warning(f"⚠️  Job completed with {results['errors']} errors")
            sys.exit(1)  # Non-zero exit for monitoring
        else:
            logging.info("🎉 Job completed successfully!")
            sys.exit(0)
            
    except Exception as e:
        logging.error(f"💥 Fatal error in daily job: {e}")
        sys.exit(2)  # Different exit code for fatal errors


if __name__ == "__main__":
    main()
