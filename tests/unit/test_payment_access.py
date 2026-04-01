import pytest
from datetime import datetime, timedelta
from src.data.access.payment_access import PaymentDataAccess, DataAccessError
from config import TEST_DB_CONFIG

@pytest.fixture
def db_config():
    """Test database configuration"""
    return TEST_DB_CONFIG

@pytest.fixture
def payment_access(db_config):
    """Create PaymentDataAccess instance for testing"""
    return PaymentDataAccess(db_config)

def test_get_tenant_agreements_empty(payment_access):
    """Test getting agreements for non-existent tenant"""
    agreements = payment_access.get_tenant_agreements("NON_EXISTENT_TENANT")
    assert isinstance(agreements, list)
    assert len(agreements) == 0

def test_get_tenant_agreements_with_data(payment_access):
    """Test getting agreements for existing tenant"""
    agreements = payment_access.get_tenant_agreements("TENANT_001")
    assert isinstance(agreements, list)
    if agreements:
        agreement = agreements[0]
        assert 'id_tenancy_agreement' in agreement
        assert 'property_name' in agreement
        assert 'property_address' in agreement
        assert 'start_date' in agreement
        assert 'end_date' in agreement
        assert 'amount' in agreement

def test_get_historical_payments_empty(payment_access):
    """Test getting payments for non-existent period"""
    future_date = datetime.now() + timedelta(days=365)
    payments = payment_access.get_historical_payments(
        "TENANT_001",
        future_date,
        future_date + timedelta(days=30)
    )
    assert isinstance(payments, list)
    assert len(payments) == 0

def test_get_historical_payments_with_data(payment_access):
    """Test getting payments for existing period"""
    past_date = datetime.now() - timedelta(days=30)
    payments = payment_access.get_historical_payments(
        "TENANT_001",
        past_date,
        datetime.now()
    )
    assert isinstance(payments, list)
    if payments:
        payment = payments[0]
        assert 'id_payment_history' in payment
        assert 'amount' in payment
        assert 'payment_date' in payment
        assert 'status' in payment
        assert 'expected_amount' in payment
        assert 'due_day' in payment

def test_get_property_payments_empty(payment_access):
    """Test getting payments for non-existent property"""
    payments = payment_access.get_property_payments(
        "NON_EXISTENT_PROPERTY",
        1,
        2024
    )
    assert isinstance(payments, list)
    assert len(payments) == 0

def test_get_property_payments_with_data(payment_access):
    """Test getting payments for existing property"""
    payments = payment_access.get_property_payments(
        "PROPERTY_001",
        1,
        2024
    )
    assert isinstance(payments, list)
    if payments:
        payment = payments[0]
        assert 'id_payment_history' in payment
        assert 'amount' in payment
        assert 'payment_date' in payment
        assert 'status' in payment
        assert 'tenant_first_name' in payment
        assert 'tenant_last_name' in payment
        assert 'expected_amount' in payment

def test_create_payment_record(payment_access):
    """Test creating a new payment record"""
    from src.core.constants import PaymentMethodCode, PaymentRecordStatus
    payment_data = {
        'tenant_id': 1,
        'property_id': 1,
        'landlord_id': 1,
        'amount': 1000.00,
        'payment_date': datetime.now(),
        'payment_method': PaymentMethodCode.E_TRANSFER,
        'confirmation_number': 'TEST123',
        'status': PaymentRecordStatus.PENDING
    }

    try:
        payment_id = payment_access.create_payment_record(payment_data)
        assert isinstance(payment_id, int)
        assert payment_id > 0
    except DataAccessError:
        pass

def test_update_payment_status(payment_access):
    """Test updating payment status"""
    from src.core.constants import PaymentMethodCode, PaymentRecordStatus
    try:
        payment_data = {
            'tenant_id': 1,
            'property_id': 1,
            'landlord_id': 1,
            'amount': 1000.00,
            'payment_date': datetime.now(),
            'payment_method': PaymentMethodCode.E_TRANSFER,
            'confirmation_number': 'TEST123',
            'status': PaymentRecordStatus.PENDING
        }
        payment_id = payment_access.create_payment_record(payment_data)

        success = payment_access.update_payment_status(
            payment_id,
            PaymentRecordStatus.CLEARED,
        )
        assert isinstance(success, bool)
    except DataAccessError:
        pass

def test_connection_pool_creation(payment_access):
    """Test connection pool creation"""
    assert payment_access.pool is not None
    assert payment_access.pool.pool_name == "payment_pool"
    assert payment_access.pool.pool_size == 5

def test_connection_handling(payment_access):
    """Test connection handling"""
    with payment_access._get_connection() as connection:
        assert connection is not None
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1
        cursor.close()

def test_error_handling(payment_access):
    """Test error handling"""
    with pytest.raises(DataAccessError):
        with payment_access._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("INVALID SQL")
            cursor.close()

def test_validate_payment_data(payment_access):
    """Test payment data validation"""
    from src.core.constants import PaymentMethodCode, PaymentRecordStatus
    valid_payment = {
        'tenant_id': 'TENANT_001',
        'property_id': 'PROPERTY_001',
        'landlord_id': 'LANDLORD_001',
        'amount': 1000.00,
        'payment_date': datetime.now(),
        'payment_method': PaymentMethodCode.E_TRANSFER,
        'confirmation_number': 'TEST123',
        'status': PaymentRecordStatus.PENDING
    }
    assert payment_access.validate_payment_data(valid_payment) is True

    invalid_payment = valid_payment.copy()
    del invalid_payment['amount']
    with pytest.raises(DataAccessError) as exc:
        payment_access.validate_payment_data(invalid_payment)
    assert "Missing required field" in str(exc.value)

    invalid_payment = valid_payment.copy()
    invalid_payment['amount'] = -100
    with pytest.raises(DataAccessError) as exc:
        payment_access.validate_payment_data(invalid_payment)
    assert "Payment amount must be greater than 0" in str(exc.value)

    invalid_payment = valid_payment.copy()
    invalid_payment['status'] = 'invalid_status'
    with pytest.raises(DataAccessError) as exc:
        payment_access.validate_payment_data(invalid_payment)
    assert "status must be an integer" in str(exc.value)

def test_validate_agreement_data(payment_access):
    """Test agreement data validation"""
    valid_agreement = {
        'tenant_id': 'TENANT_001',
        'property_id': 'PROPERTY_001',
        'landlord_id': 'LANDLORD_001',
        'start_date': datetime.now(),
        'end_date': datetime.now() + timedelta(days=365),
        'amount': 1000.00,
        'payment_day': 1
    }
    assert payment_access.validate_agreement_data(valid_agreement) is True

    invalid_agreement = valid_agreement.copy()
    del invalid_agreement['amount']
    with pytest.raises(DataAccessError) as exc:
        payment_access.validate_agreement_data(invalid_agreement)
    assert "Missing required field" in str(exc.value)

    invalid_agreement = valid_agreement.copy()
    invalid_agreement['end_date'] = invalid_agreement['start_date'] - timedelta(days=1)
    with pytest.raises(DataAccessError) as exc:
        payment_access.validate_agreement_data(invalid_agreement)
    assert "End date must be after start date" in str(exc.value)

    invalid_agreement = valid_agreement.copy()
    invalid_agreement['payment_day'] = 32
    with pytest.raises(DataAccessError) as exc:
        payment_access.validate_agreement_data(invalid_agreement)
    assert "Payment day must be between 1 and 31" in str(exc.value)
