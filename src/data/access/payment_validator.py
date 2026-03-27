from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal
from src.core.exceptions import ValidationError

class PaymentDataValidator:
    """Validator for payment and agreement data"""
    
    # Valid payment statuses
    VALID_PAYMENT_STATUSES = {'pending', 'completed', 'failed', 'cancelled', 'refunded'}
    
    # Valid payment methods
    VALID_PAYMENT_METHODS = {'e-transfer', 'bank_transfer', 'cash', 'check', 'credit_card'}
    
    def __init__(self):
        """Initialize the validator"""
        pass
        
    def validate_payment_data(self, payment_data: Dict[str, Any]) -> bool:
        """
        Validate payment data structure and values
        
        Args:
            payment_data (Dict[str, Any]): Payment data to validate
            
        Returns:
            bool: True if data is valid
            
        Raises:
            ValidationError: If validation fails
        """
        # Check required fields
        required_fields = {
            'ref_tenantID': str,
            'ref_propertyID': str,
            'ref_landlordID': str,
            'amount': (int, float, Decimal),
            'payment_date': datetime,
            'payment_method': str,
            'confirmation_number': str,
            'status': str
        }
        
        self._validate_required_fields(payment_data, required_fields)
        
        # Validate amount
        amount = payment_data['amount']
        if not isinstance(amount, (int, float, Decimal)):
            raise ValidationError("Amount must be a number")
        if amount <= 0:
            raise ValidationError("Amount must be greater than 0")
            
        # Validate payment method
        if payment_data['payment_method'] not in self.VALID_PAYMENT_METHODS:
            raise ValidationError(
                f"Invalid payment method. Must be one of: {', '.join(self.VALID_PAYMENT_METHODS)}"
            )
            
        # Validate status
        if payment_data['status'] not in self.VALID_PAYMENT_STATUSES:
            raise ValidationError(
                f"Invalid payment status. Must be one of: {', '.join(self.VALID_PAYMENT_STATUSES)}"
            )
            
        # Validate confirmation number
        if not payment_data['confirmation_number'].strip():
            raise ValidationError("Confirmation number cannot be empty")
            
        # Validate optional fields if present
        if 'note' in payment_data and not isinstance(payment_data['note'], str):
            raise ValidationError("Note must be a string")
            
        if 'ref_AgreementId' in payment_data and not isinstance(payment_data['ref_AgreementId'], (int, str)):
            raise ValidationError("Agreement ID must be an integer or string")
            
        return True
        
    def validate_agreement_data(self, agreement_data: Dict[str, Any]) -> bool:
        """
        Validate agreement data structure and values
        
        Args:
            agreement_data (Dict[str, Any]): Agreement data to validate
            
        Returns:
            bool: True if data is valid
            
        Raises:
            ValidationError: If validation fails
        """
        # Check required fields
        required_fields = {
            'ref_tenantID': str,
            'ref_propertyID': str,
            'ref_landlordID': str,
            'start_date': datetime,
            'end_date': datetime,
            'amount': (int, float, Decimal),
            'paymentDay': int,
            'paymentMethod': str
        }
        
        self._validate_required_fields(agreement_data, required_fields)
        
        # Validate dates
        start_date = agreement_data['start_date']
        end_date = agreement_data['end_date']
        
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            raise ValidationError("Start and end dates must be datetime objects")
            
        if start_date >= end_date:
            raise ValidationError("End date must be after start date")
            
        # Validate amount
        amount = agreement_data['amount']
        if not isinstance(amount, (int, float, Decimal)):
            raise ValidationError("Amount must be a number")
        if amount <= 0:
            raise ValidationError("Amount must be greater than 0")
            
        # Validate payment day
        payment_day = agreement_data['paymentDay']
        if not isinstance(payment_day, int):
            raise ValidationError("Payment day must be an integer")
        if not 1 <= payment_day <= 31:
            raise ValidationError("Payment day must be between 1 and 31")
            
        # Validate payment method
        if agreement_data['paymentMethod'] not in self.VALID_PAYMENT_METHODS:
            raise ValidationError(
                f"Invalid payment method. Must be one of: {', '.join(self.VALID_PAYMENT_METHODS)}"
            )
            
        # Validate optional fields if present
        if 'monthToMonth' in agreement_data and not isinstance(agreement_data['monthToMonth'], bool):
            raise ValidationError("monthToMonth must be a boolean")
            
        return True
        
    def validate_payment_update(self, payment_id: Any, update_data: Dict[str, Any]) -> bool:
        """
        Validate payment update data
        
        Args:
            payment_id (Any): ID of the payment to update
            update_data (Dict[str, Any]): Update data to validate
            
        Returns:
            bool: True if data is valid
            
        Raises:
            ValidationError: If validation fails
        """
        if not payment_id:
            raise ValidationError("Payment ID is required")
            
        if not update_data:
            raise ValidationError("Update data cannot be empty")
            
        # Validate status if present
        if 'status' in update_data:
            if update_data['status'] not in self.VALID_PAYMENT_STATUSES:
                raise ValidationError(
                    f"Invalid payment status. Must be one of: {', '.join(self.VALID_PAYMENT_STATUSES)}"
                )
                
        # Validate note if present
        if 'note' in update_data and not isinstance(update_data['note'], str):
            raise ValidationError("Note must be a string")
            
        return True
        
    def _validate_required_fields(self, data: Dict[str, Any], required_fields: Dict[str, Any]) -> None:
        """
        Validate that all required fields are present and of correct type
        
        Args:
            data (Dict[str, Any]): Data to validate
            required_fields (Dict[str, Any]): Required fields and their types
            
        Raises:
            ValidationError: If validation fails
        """
        for field, expected_type in required_fields.items():
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
                
            if not isinstance(data[field], expected_type):
                if isinstance(expected_type, tuple):
                    if not any(isinstance(data[field], t) for t in expected_type):
                        raise ValidationError(
                            f"Field {field} must be one of types: {expected_type}"
                        )
                else:
                    raise ValidationError(
                        f"Field {field} must be of type {expected_type.__name__}"
                    ) 