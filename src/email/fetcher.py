import imaplib
import email
from typing import List, Dict, Any
from datetime import datetime
from ..core.config import Config
from ..core.exceptions import EmailProcessingError

class EmailFetcher:
    def __init__(self):
        self.imap = None
        self._connect()

    def _connect(self) -> None:
        try:
            self.imap = imaplib.IMAP4_SSL(Config.EMAIL_HOST, Config.EMAIL_PORT)
            self.imap.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
        except Exception as e:
            raise EmailProcessingError(f"Failed to connect to email server: {str(e)}")

    def fetch_emails(self, since: datetime = None) -> List[Dict[str, Any]]:
        """
        Fetch emails from the server.
        
        Args:
            since: Optional datetime to fetch emails since
            
        Returns:
            List of email data dictionaries
        """
        try:
            self.imap.select('INBOX')
            
            # Construct search criteria
            search_criteria = 'ALL'
            if since:
                search_criteria = f'SINCE {since.strftime("%d-%b-%Y")}'
            
            _, messages = self.imap.search(None, search_criteria)
            emails = []
            
            for num in messages[0].split():
                _, msg_data = self.imap.fetch(num, '(RFC822)')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                emails.append({
                    'subject': email_message['subject'],
                    'from': email_message['from'],
                    'date': email_message['date'],
                    'body': self._get_email_body(email_message)
                })
            
            return emails
        except Exception as e:
            raise EmailProcessingError(f"Failed to fetch emails: {str(e)}")

    def _get_email_body(self, email_message: email.message.Message) -> str:
        """Extract the email body from the message."""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode()
        else:
            return email_message.get_payload(decode=True).decode()

    def __del__(self):
        if self.imap:
            try:
                self.imap.close()
                self.imap.logout()
            except:
                pass 