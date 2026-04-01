from typing import Dict, Any
from datetime import datetime
from decimal import Decimal
from src.core.exceptions import ValidationError
from src.core.constants import PaymentMethodCode


class PaymentDataValidator:
    """Validator for payment and agreement data"""

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
        required_fields = {
            'tenant_id': (int, str),
            'property_id': (int, str),
            'landlord_id': (int, str),
            'amount': (int, float, Decimal),
            'payment_date': datetime,
            'payment_method': int,
            'confirmation_number': str,
            'status': int,
        }

        self._validate_required_fields(payment_data, required_fields)

        amount = payment_data['amount']
        if not isinstance(amount, (int, float, Decimal)):
            raise ValidationError("Amount must be a number")
        if amount <= 0:
            raise ValidationError("Amount must be greater than 0")

        if payment_data['payment_method'] not in {
            PaymentMethodCode.UNKNOWN,
            PaymentMethodCode.E_TRANSFER,
            PaymentMethodCode.OTHER,
        }:
            raise ValidationError("Invalid payment_method code")

        if not isinstance(payment_data['status'], int):
            raise ValidationError("status must be an integer (PaymentRecordStatus)")

        if not payment_data['confirmation_number'].strip():
            raise ValidationError("Confirmation number cannot be empty")

        if 'agreement_id' in payment_data and payment_data['agreement_id'] is not None:
            if not isinstance(payment_data['agreement_id'], (int, str)):
                raise ValidationError("agreement_id must be an integer or string")

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
        required_fields = {
            'tenant_id': (int, str),
            'property_id': (int, str),
            'landlord_id': (int, str),
            'start_date': datetime,
            'end_date': datetime,
            'amount': (int, float, Decimal),
            'payment_day': int,
            'payment_method': int,
        }

        self._validate_required_fields(agreement_data, required_fields)

        start_date = agreement_data['start_date']
        end_date = agreement_data['end_date']

        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            raise ValidationError("Start and end dates must be datetime objects")

        if start_date >= end_date:
            raise ValidationError("End date must be after start date")

        amount = agreement_data['amount']
        if not isinstance(amount, (int, float, Decimal)):
            raise ValidationError("Amount must be a number")
        if amount <= 0:
            raise ValidationError("Amount must be greater than 0")

        payment_day = agreement_data['payment_day']
        if not isinstance(payment_day, int):
            raise ValidationError("Payment day must be an integer")
        if not 1 <= payment_day <= 31:
            raise ValidationError("Payment day must be between 1 and 31")

        if agreement_data['payment_method'] not in {
            PaymentMethodCode.UNKNOWN,
            PaymentMethodCode.E_TRANSFER,
            PaymentMethodCode.OTHER,
        }:
            raise ValidationError("Invalid payment_method code")

        if 'month_to_month' in agreement_data and not isinstance(agreement_data['month_to_month'], bool):
            raise ValidationError("month_to_month must be a boolean")

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

        if 'status' in update_data:
            if not isinstance(update_data['status'], int):
                raise ValidationError("status must be an integer (PaymentRecordStatus)")

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

            if isinstance(expected_type, tuple):
                if not any(isinstance(data[field], t) for t in expected_type):
                    raise ValidationError(
                        f"Field {field} must be one of types: {expected_type}"
                    )
            else:
                if not isinstance(data[field], expected_type):
                    raise ValidationError(
                        f"Field {field} must be of type {expected_type.__name__}"
                    )
