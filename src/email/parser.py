import re
from typing import Dict, Any, Optional
from datetime import datetime
from ..core.exceptions import EmailProcessingError
from ..core.constants import TableNames

class EmailParser:
    def __init__(self):
        self.payment_patterns = {
            'amount': r'\$(\d+\.\d{2})',
            'confirmation': r'Confirmation number: (\w+)',
            'sender': r'From: (.+)',
            'date': r'Date: (.+)'
        }

    def parse_payment_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse payment information from an email.
        
        Args:
            email_data: Dictionary containing email data
            
        Returns:
            Dictionary containing parsed payment information
        """
        try:
            payment_info = {
                'ref_tenantID': None,
                'ref_propertyID': None,
                'ref_landlordID': None,
                'ref_AgreementId': None,
                'amount': self._extract_amount(email_data['body']),
                'payment_date': self._extract_date(email_data['date']),
                'payment_method': 'e-transfer',
                'confirmation_number': self._extract_confirmation(email_data['body']),
                'status': 'pending',
                'note': email_data['subject']
            }
            
            # Validate required fields
            if not all([payment_info['amount'], payment_info['confirmation_number']]):
                raise EmailProcessingError("Missing required payment information")
                
            return payment_info
        except Exception as e:
            raise EmailProcessingError(f"Failed to parse payment email: {str(e)}")

    def _extract_amount(self, body: str) -> Optional[float]:
        """Extract payment amount from email body."""
        match = re.search(self.payment_patterns['amount'], body)
        return float(match.group(1)) if match else None

    def _extract_confirmation(self, body: str) -> Optional[str]:
        """Extract confirmation number from email body."""
        match = re.search(self.payment_patterns['confirmation'], body)
        return match.group(1) if match else None

    def _extract_date(self, date_str: str) -> datetime:
        """Parse date from email date string."""
        try:
            return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
        except ValueError:
            return datetime.now() 