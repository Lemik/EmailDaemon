import mysql.connector
from mysql.connector import Error
import logging
from config import DB_CONFIG
from config import LOGGING_CONFIG

# Configure logging from config.py
logging.basicConfig(**LOGGING_CONFIG)

def connect_to_db():
    """Establishes a connection to AWS MySQL."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
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
    recipient_account_ending: str, view_in_browser_link: str = None
):
    connection = connect_to_db()
    if not connection:
        logging.error(f"❌ Error Connection to DB: {connection}")
        return 

    query = """
    INSERT INTO Rental_Payments_Log (id,
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
        return None
    
    finally:
        cursor.close()
        connection.close()


def log_email_error(id: str, subject: str, send_from: str, send_date: str, error_message: str, raw_email: str = None):
    """Logs email processing errors into Rental_Payments_Log_Errors table."""
    connection = connect_to_db()
    if not connection:
        logging.error(f"❌ Error Connection to DB: {connection}")
        return 

    query = """
    INSERT INTO Rental_Payments_Log_Errors (id, subject, send_from, send_date, error_message, raw_email, created_at, updated_at)
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