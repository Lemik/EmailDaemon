import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from src.data.access.payment_validator import PaymentDataValidator
from src.core.exceptions import ValidationError
from src.core.constants import PaymentMethodCode, PaymentRecordStatus

@pytest.fixture
def validator():
    """Create a PaymentDataValidator instance for testing"""
    return PaymentDataValidator()

@pytest.fixture
def valid_payment_data():
    """Create valid payment data for testing"""
    return {
        'tenant_id': 'TENANT_001',
        'property_id': 'PROPERTY_001',
        'landlord_id': 'LANDLORD_001',
        'amount': 1000.00,
        'payment_date': datetime.now(),
        'payment_method': PaymentMethodCode.E_TRANSFER,
        'confirmation_number': 'TEST123',
        'status': PaymentRecordStatus.PENDING,
        'agreement_id': 'AGREEMENT_001'
    }

@pytest.fixture
def valid_agreement_data():
    """Create valid agreement data for testing"""
    return {
        'tenant_id': 'TENANT_001',
        'property_id': 'PROPERTY_001',
        'landlord_id': 'LANDLORD_001',
        'start_date': datetime.now(),
        'end_date': datetime.now() + timedelta(days=365),
        'amount': 1000.00,
        'payment_day': 1,
        'payment_method': PaymentMethodCode.E_TRANSFER,
        'month_to_month': True
    }

def test_validate_payment_data_valid(validator, valid_payment_data):
    """Test validation of valid payment data"""
    assert validator.validate_payment_data(valid_payment_data) is True

def test_validate_payment_data_missing_field(validator, valid_payment_data):
    """Test validation of payment data with missing field"""
    del valid_payment_data['amount']
    with pytest.raises(ValidationError) as exc:
        validator.validate_payment_data(valid_payment_data)
    assert "Missing required field" in str(exc.value)

def test_validate_payment_data_invalid_amount(validator, valid_payment_data):
    """Test validation of payment data with invalid amount"""
    valid_payment_data['amount'] = -100
    with pytest.raises(ValidationError) as exc:
        validator.validate_payment_data(valid_payment_data)
    assert "Amount must be greater than 0" in str(exc.value)

def test_validate_payment_data_invalid_status(validator, valid_payment_data):
    """Test validation of payment data with invalid status"""
    valid_payment_data['status'] = 'invalid_status'
    with pytest.raises(ValidationError) as exc:
        validator.validate_payment_data(valid_payment_data)
    assert "Field status must be of type int" in str(exc.value)

def test_validate_payment_data_invalid_method(validator, valid_payment_data):
    """Test validation of payment data with invalid payment method"""
    valid_payment_data['payment_method'] = 99
    with pytest.raises(ValidationError) as exc:
        validator.validate_payment_data(valid_payment_data)
    assert "Invalid payment_method" in str(exc.value)

def test_validate_agreement_data_valid(validator, valid_agreement_data):
    """Test validation of valid agreement data"""
    assert validator.validate_agreement_data(valid_agreement_data) is True

def test_validate_agreement_data_missing_field(validator, valid_agreement_data):
    """Test validation of agreement data with missing field"""
    del valid_agreement_data['amount']
    with pytest.raises(ValidationError) as exc:
        validator.validate_agreement_data(valid_agreement_data)
    assert "Missing required field" in str(exc.value)

def test_validate_agreement_data_invalid_dates(validator, valid_agreement_data):
    """Test validation of agreement data with invalid dates"""
    valid_agreement_data['end_date'] = valid_agreement_data['start_date'] - timedelta(days=1)
    with pytest.raises(ValidationError) as exc:
        validator.validate_agreement_data(valid_agreement_data)
    assert "End date must be after start date" in str(exc.value)

def test_validate_agreement_data_invalid_payment_day(validator, valid_agreement_data):
    """Test validation of agreement data with invalid payment day"""
    valid_agreement_data['payment_day'] = 32
    with pytest.raises(ValidationError) as exc:
        validator.validate_agreement_data(valid_agreement_data)
    assert "Payment day must be between 1 and 31" in str(exc.value)

def test_validate_payment_update_valid(validator):
    """Test validation of valid payment update data"""
    update_data = {
        'status': PaymentRecordStatus.CLEARED,
    }
    assert validator.validate_payment_update('PAYMENT_001', update_data) is True

def test_validate_payment_update_invalid_status(validator):
    """Test validation of payment update with invalid status"""
    update_data = {
        'status': 'invalid_status',
    }
    with pytest.raises(ValidationError) as exc:
        validator.validate_payment_update('PAYMENT_001', update_data)
    assert "status must be an integer" in str(exc.value)

def test_validate_payment_update_empty_data(validator):
    """Test validation of payment update with empty data"""
    with pytest.raises(ValidationError) as exc:
        validator.validate_payment_update('PAYMENT_001', {})
    assert "Update data cannot be empty" in str(exc.value)

def test_validate_payment_update_missing_id(validator):
    """Test validation of payment update with missing ID"""
    update_data = {'status': PaymentRecordStatus.CLEARED}
    with pytest.raises(ValidationError) as exc:
        validator.validate_payment_update(None, update_data)
    assert "Payment ID is required" in str(exc.value)
