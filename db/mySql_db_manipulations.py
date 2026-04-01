import mysql.connector
from mysql.connector import Error
import logging
import sys
from datetime import datetime
from config import PROD_DB_CONFIG
from config import LOGGING_CONFIG

# Configure logging from config.py
logging.basicConfig(**LOGGING_CONFIG)

def connect_to_db():
    """Establishes a connection to AWS MySQL."""
    try:
        connection = mysql.connector.connect(**PROD_DB_CONFIG)
        if connection.is_connected():
            logging.info("✅ Connected to AWS MySQL database")
            return connection
    except Exception as e:
        logging.error(f"❌ Error connecting to MySQL: {e}")
        return None

def insert_email_data(id: str,
    sender_name: str, 
    sender_email: str,
    send_date: str, send_amount: float, currency: str,
    sender_message: str, reference_number: str, recipient_name: str,
    recipient_email: str, status_message: str, recipient_bank_name: str,
    recipient_account_ending: str, view_in_browser_link: str = None, subject: str = "Unknown Subject"
):
    connection = connect_to_db()
    if not connection:
        logging.error(f"❌ Error Connection to DB: {connection}")
        return 

    query = """
    INSERT INTO rental_payments_log (id,
        sender_name,sender_email, send_date, send_amount, currency, sender_message, reference_number,
        recipient_name, recipient_email, status_message, recipient_bank_name,
        recipient_account_ending, view_in_browser_link, created_at, updated_at
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """

    data = (
        id, sender_name,sender_email, send_date, send_amount, currency, sender_message, reference_number,
        recipient_name, recipient_email, status_message, recipient_bank_name,
        recipient_account_ending, view_in_browser_link
    )

    try:
        cursor = connection.cursor()
        cursor.execute(query, data)
        connection.commit()
        logging.info(f"✅ Email transaction saved: Reference #{reference_number}")
        return {reference_number}
    
    except Exception as e:
        logging.error(f"❌ Error inserting data: {e}")
        
        # Log the error to the database
        try:
            log_email_error(
                id=id,
                subject=subject,
                send_from=sender_email,
                send_date=send_date,
                error_message=f"Database insertion error: {str(e)}",
                raw_email=None  # We don't have raw email data in this function
            )
        except Exception as log_error:
            logging.error(f"❌ Failed to log email error: {log_error}")
        
        return None
    
    finally:
        cursor.close()
        connection.close()

def log_email_error(id: str, subject: str, send_from: str, send_date: str, error_message: str, raw_email: str = None):
    """Logs email processing errors into rental_payments_log_errors table."""
    connection = connect_to_db()
    if not connection:
        logging.error(f"❌ Error Connection to DB: {connection}")
        return 

    query = """
    INSERT INTO rental_payments_log_errors (id, subject, send_from, send_date, error_message, raw_email, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """

    data = (id, subject, send_from, send_date, error_message, raw_email)

    try:
        cursor = connection.cursor()
        cursor.execute(query, data)
        connection.commit()
        logging.info(f"✅ Logged email error: ID #{id}")
        return id
    
    except Exception as e:
        logging.error(f"❌ Error logging email error: {e}")
        return None
    
    finally:
        cursor.close()
        connection.close()


def start_job_execution():
    """Start a new job execution record and return the job ID."""
    connection = connect_to_db()
    if not connection:
        logging.error(f"❌ Error Connection to DB: {connection}")
        return None

    query = """
    INSERT INTO rental_payments_log_stats (
        job_start_time, status, python_version, script_version, environment
    ) VALUES (%s, %s, %s, %s, %s)
    """

    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    data = (
        datetime.now(),
        "STARTED", 
        python_version,
        "1.0",  # Script version - you can make this dynamic
        "production"
    )

    try:
        cursor = connection.cursor()
        cursor.execute(query, data)
        connection.commit()
        job_id = cursor.lastrowid
        logging.info(f"✅ Started job execution tracking: ID #{job_id}")
        return job_id
    
    except Exception as e:
        logging.error(f"❌ Error starting job execution tracking: {e}")
        return None
    
    finally:
        cursor.close()
        connection.close()


def update_job_execution(job_id, status, emails_fetched=0, emails_processed=0, 
                        successful_transactions=0, failed_transactions=0, 
                        errors_encountered=0, error_details=None):
    """Update job execution record with progress/results."""
    if not job_id:
        return False
        
    connection = connect_to_db()
    if not connection:
        logging.error(f"❌ Error Connection to DB: {connection}")
        return False

    query = """
    UPDATE rental_payments_log_stats 
    SET status = %s, emails_fetched = %s, emails_processed = %s, 
        successful_transactions = %s, failed_transactions = %s, 
        errors_encountered = %s, error_details = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id = %s
    """

    data = (
        status, emails_fetched, emails_processed, successful_transactions, 
        failed_transactions, errors_encountered, error_details, job_id
    )

    try:
        cursor = connection.cursor()
        cursor.execute(query, data)
        connection.commit()
        logging.debug(f"✅ Updated job execution: ID #{job_id}, Status: {status}")
        return True
    
    except Exception as e:
        logging.error(f"❌ Error updating job execution: {e}")
        return False
    
    finally:
        cursor.close()
        connection.close()


def complete_job_execution(job_id, status, emails_fetched=0, emails_processed=0, 
                          successful_transactions=0, failed_transactions=0, 
                          errors_encountered=0, error_details=None, start_time=None):
    """Complete job execution record with final results."""
    if not job_id:
        return False
        
    connection = connect_to_db()
    if not connection:
        logging.error(f"❌ Error Connection to DB: {connection}")
        return False

    end_time = datetime.now()
    duration_seconds = None
    
    if start_time:
        duration = end_time - start_time
        duration_seconds = int(duration.total_seconds())

    query = """
    UPDATE rental_payments_log_stats
    SET job_end_time = %s, duration_seconds = %s, status = %s, 
        emails_fetched = %s, emails_processed = %s, successful_transactions = %s, 
        failed_transactions = %s, errors_encountered = %s, error_details = %s,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = %s
    """

    data = (
        end_time, duration_seconds, status, emails_fetched, emails_processed, 
        successful_transactions, failed_transactions, errors_encountered, 
        error_details, job_id
    )

    try:
        cursor = connection.cursor()
        cursor.execute(query, data)
        connection.commit()
        logging.info(f"✅ Completed job execution: ID #{job_id}, Status: {status}, Duration: {duration_seconds}s")
        return True
    
    except Exception as e:
        logging.error(f"❌ Error completing job execution: {e}")
        return False
    
    finally:
        cursor.close()
        connection.close()


def get_job_history(limit=10, days=None):
    """Get recent job execution history."""
    connection = connect_to_db()
    if not connection:
        logging.error(f"❌ Error Connection to DB: {connection}")
        return []

    base_query = """
    SELECT id, job_start_time, job_end_time, duration_seconds, status,
           emails_fetched, emails_processed, successful_transactions, 
           failed_transactions, errors_encountered, error_details
    FROM rental_payments_log_stats 
    """
    
    if days:
        query = base_query + "WHERE job_start_time >= DATE_SUB(NOW(), INTERVAL %s DAY) ORDER BY job_start_time DESC LIMIT %s"
        data = (days, limit)
    else:
        query = base_query + "ORDER BY job_start_time DESC LIMIT %s"
        data = (limit,)

    try:
        cursor = connection.cursor()
        cursor.execute(query, data)
        results = cursor.fetchall()
        
        # Convert to list of dictionaries
        columns = [desc[0] for desc in cursor.description]
        job_history = [dict(zip(columns, row)) for row in results]
        
        return job_history
    
    except Exception as e:
        logging.error(f"❌ Error getting job history: {e}")
        return []
    
    finally:
        cursor.close()
        connection.close()