from typing import List, Dict, Any
from datetime import datetime, timedelta
from .fetcher import EmailFetcher
from .parser import EmailParser
from ..data.access.payment_access import PaymentAccess
from ..core.exceptions import EmailProcessingError

class EmailProcessor:
    def __init__(self):
        self.fetcher = EmailFetcher()
        self.parser = EmailParser()
        self.payment_access = PaymentAccess()

    def process_new_payments(self, days_back: int = 1) -> List[Dict[str, Any]]:
        """
        Process new payment emails and store them in the database.
        
        Args:
            days_back: Number of days to look back for emails
            
        Returns:
            List of processed payment records
        """
        try:
            # Calculate start date
            start_date = datetime.now() - timedelta(days=days_back)
            
            # Fetch emails
            emails = self.fetcher.fetch_emails(since=start_date)
            
            # Process each email
            processed_payments = []
            for email_data in emails:
                if self._is_payment_email(email_data):
                    payment_info = self.parser.parse_payment_email(email_data)
                    if payment_info:
                        # Store in database
                        payment_id = self.payment_access.store_payment(payment_info)
                        payment_info['id_payment_history'] = payment_id
                        processed_payments.append(payment_info)
            
            return processed_payments
        except Exception as e:
            raise EmailProcessingError(f"Failed to process payments: {str(e)}")

    def _is_payment_email(self, email_data: Dict[str, Any]) -> bool:
        """Check if the email is a payment notification."""
        # Check if it's from the payment notification service
        return 'notify@payments.interac.ca' in email_data.get('from', '').lower() 