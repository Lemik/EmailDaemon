import mysql.connector
from typing import List, Dict, Any, Optional
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from config import PROD_DB_CONFIG
from ...core.exceptions import DataAccessError
from ...core.constants import TableNames
from mysql.connector import Error
from mysql.connector.pooling import MySQLConnectionPool

class DataAccessError(Exception):
    """Custom exception for database access errors"""
    pass

class PaymentDataAccess:
    def __init__(self, db_config: Dict[str, str]):
        """
        Initialize PaymentDataAccess with database configuration
        
        Args:
            db_config (Dict[str, str]): Database configuration including:
                - host
                - port
                - user
                - password
                - database
        """
        self.db_config = db_config
        self.pool = self._create_connection_pool()
        
    def _create_connection_pool(self) -> MySQLConnectionPool:
        """Create a connection pool for database access"""
        try:
            return MySQLConnectionPool(
                pool_name="payment_pool",
                pool_size=5,
                **self.db_config
            )
        except Error as e:
            raise DataAccessError(f"Failed to create connection pool: {str(e)}")
            
    def _get_connection(self):
        """Get a connection from the pool"""
        try:
            connection = self.pool.get_connection()
            # Wrap the connection in a context manager that catches all database errors
            class ConnectionWrapper:
                def __init__(self, conn):
                    self.conn = conn
                
                def __enter__(self):
                    return self.conn
                
                def __exit__(self, exc_type, exc_val, exc_tb):
                    if exc_type is not None:
                        if isinstance(exc_val, Error):
                            raise DataAccessError(f"Database error: {str(exc_val)}")
                        raise exc_val
                    self.conn.close()
            
            return ConnectionWrapper(connection)
        except Error as e:
            raise DataAccessError(f"Failed to get connection from pool: {str(e)}")
            
    def get_tenant_agreements(self, tenant_id: str) -> List[Dict]:
        """
        Retrieve all active agreements for a tenant
        
        Args:
            tenant_id (str): The unique identifier of the tenant
            
        Returns:
            List[Dict]: List of agreement records
            
        Raises:
            DataAccessError: If database operation fails
        """
        try:
            with self._get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                query = """
                    SELECT 
                        ta.*,
                        p.name as property_name,
                        p.address as property_address
                    FROM Tenancy_Agreement ta
                    JOIN Property p ON ta.ref_propertyID = p.id_Property
                    WHERE ta.ref_tenantID = %s 
                    AND ta.ddate IS NULL
                    AND ta.end_date >= CURDATE()
                """
                cursor.execute(query, (tenant_id,))
                return cursor.fetchall()
        except Error as e:
            raise DataAccessError(f"Failed to get tenant agreements: {str(e)}")
            
    def get_historical_payments(self, tenant_id: str, 
                              start_date: datetime, 
                              end_date: datetime) -> List[Dict]:
        """
        Retrieve payment history for a tenant within a specified date range
        
        Args:
            tenant_id (str): The unique identifier of the tenant
            start_date (datetime): Start date of the period
            end_date (datetime): End date of the period
            
        Returns:
            List[Dict]: List of payment records
            
        Raises:
            DataAccessError: If database operation fails
        """
        try:
            with self._get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                query = """
                    SELECT 
                        rph.*,
                        ta.amount as expected_amount,
                        ta.paymentDay as due_day
                    FROM Rental_Payment_History rph
                    LEFT JOIN Tenancy_Agreement ta ON rph.ref_AgreementId = ta.id_Tenancy_Agreement
                    WHERE rph.ref_tenantID = %s 
                    AND rph.payment_date BETWEEN %s AND %s
                    AND rph.ddate IS NULL
                    ORDER BY rph.payment_date DESC
                """
                cursor.execute(query, (tenant_id, start_date, end_date))
                return cursor.fetchall()
        except Error as e:
            raise DataAccessError(f"Failed to get historical payments: {str(e)}")
            
    def get_property_payments(self, property_id: str, 
                            month: int, year: int) -> List[Dict]:
        """
        Retrieve all payments for a specific property in a given month/year
        
        Args:
            property_id (str): The unique identifier of the property
            month (int): Month number (1-12)
            year (int): Year number
            
        Returns:
            List[Dict]: List of payment records
            
        Raises:
            DataAccessError: If database operation fails
        """
        try:
            with self._get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                query = """
                    SELECT 
                        rph.*,
                        pt.Fname as tenant_first_name,
                        pt.Lname as tenant_last_name,
                        ta.amount as expected_amount
                    FROM Rental_Payment_History rph
                    JOIN Property_tenant pt ON rph.ref_tenantID = pt.id_Property_tenant
                    LEFT JOIN Tenancy_Agreement ta ON rph.ref_AgreementId = ta.id_Tenancy_Agreement
                    WHERE rph.ref_propertyID = %s 
                    AND MONTH(rph.payment_date) = %s 
                    AND YEAR(rph.payment_date) = %s
                    AND rph.ddate IS NULL
                    ORDER BY rph.payment_date DESC
                """
                cursor.execute(query, (property_id, month, year))
                return cursor.fetchall()
        except Error as e:
            raise DataAccessError(f"Failed to get property payments: {str(e)}")
            
    def create_payment_record(self, payment_data: Dict) -> int:
        """
        Create a new payment record
        
        Args:
            payment_data (Dict): Payment information including:
                - ref_tenantID
                - ref_propertyID
                - ref_landlordID
                - ref_AgreementId (optional)
                - amount
                - payment_date
                - payment_method
                - confirmation_number
                - status
                - note (optional)
                
        Returns:
            int: ID of the created payment record
            
        Raises:
            DataAccessError: If database operation fails
        """
        try:
            with self._get_connection() as connection:
                cursor = connection.cursor()
                query = """
                    INSERT INTO Rental_Payment_History (
                        ref_tenantID, ref_propertyID, ref_landlordID,
                        ref_AgreementId, amount, payment_date,
                        payment_method, confirmation_number, status, note
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """
                values = (
                    payment_data['ref_tenantID'],
                    payment_data['ref_propertyID'],
                    payment_data['ref_landlordID'],
                    payment_data.get('ref_AgreementId'),
                    payment_data['amount'],
                    payment_data['payment_date'],
                    payment_data['payment_method'],
                    payment_data['confirmation_number'],
                    payment_data['status'],
                    payment_data.get('note')
                )
                cursor.execute(query, values)
                connection.commit()
                return cursor.lastrowid
        except Error as e:
            raise DataAccessError(f"Failed to create payment record: {str(e)}")
            
    def update_payment_status(self, payment_id: int, 
                            status: str, 
                            note: Optional[str] = None) -> bool:
        """
        Update the status of a payment record
        
        Args:
            payment_id (int): ID of the payment record
            status (str): New status
            note (str, optional): Additional note
            
        Returns:
            bool: True if update successful
            
        Raises:
            DataAccessError: If database operation fails
        """
        try:
            with self._get_connection() as connection:
                cursor = connection.cursor()
                query = """
                    UPDATE Rental_Payment_History 
                    SET status = %s, note = %s
                    WHERE id_Payment_History = %s
                """
                cursor.execute(query, (status, note, payment_id))
                connection.commit()
                return cursor.rowcount > 0
        except Error as e:
            raise DataAccessError(f"Failed to update payment status: {str(e)}")

    def validate_payment_data(self, payment_data: Dict) -> bool:
        """
        Validate payment data before insertion or update
        
        Args:
            payment_data (Dict): Payment information to validate
            
        Returns:
            bool: True if data is valid
            
        Raises:
            DataAccessError: If validation fails
        """
        required_fields = [
            'ref_tenantID',
            'ref_propertyID',
            'ref_landlordID',
            'amount',
            'payment_date',
            'payment_method',
            'confirmation_number',
            'status'
        ]
        
        # Check required fields
        for field in required_fields:
            if field not in payment_data:
                raise DataAccessError(f"Missing required field: {field}")
        
        # Validate amount
        try:
            amount = float(payment_data['amount'])
            if amount <= 0:
                raise DataAccessError("Payment amount must be greater than 0")
        except ValueError:
            raise DataAccessError("Invalid payment amount format")
        
        # Validate payment date
        if not isinstance(payment_data['payment_date'], datetime):
            raise DataAccessError("Invalid payment date format")
        
        # Validate status
        valid_statuses = ['pending', 'completed', 'failed', 'cancelled']
        if payment_data['status'] not in valid_statuses:
            raise DataAccessError(f"Invalid payment status. Must be one of: {', '.join(valid_statuses)}")
        
        return True

    def validate_agreement_data(self, agreement_data: Dict) -> bool:
        """
        Validate agreement data before insertion or update
        
        Args:
            agreement_data (Dict): Agreement information to validate
            
        Returns:
            bool: True if data is valid
            
        Raises:
            DataAccessError: If validation fails
        """
        required_fields = [
            'ref_tenantID',
            'ref_propertyID',
            'ref_landlordID',
            'start_date',
            'end_date',
            'amount',
            'paymentDay'
        ]
        
        # Check required fields
        for field in required_fields:
            if field not in agreement_data:
                raise DataAccessError(f"Missing required field: {field}")
        
        # Validate dates
        if not isinstance(agreement_data['start_date'], datetime):
            raise DataAccessError("Invalid start date format")
        if not isinstance(agreement_data['end_date'], datetime):
            raise DataAccessError("Invalid end date format")
        if agreement_data['start_date'] >= agreement_data['end_date']:
            raise DataAccessError("End date must be after start date")
        
        # Validate amount
        try:
            amount = float(agreement_data['amount'])
            if amount <= 0:
                raise DataAccessError("Agreement amount must be greater than 0")
        except ValueError:
            raise DataAccessError("Invalid agreement amount format")
        
        # Validate payment day
        try:
            payment_day = int(agreement_data['paymentDay'])
            if not 1 <= payment_day <= 31:
                raise DataAccessError("Payment day must be between 1 and 31")
        except ValueError:
            raise DataAccessError("Invalid payment day format")
        
        return True

class PaymentAccess:
    def __init__(self):
        self.connection = None
        self._connect()

    def _connect(self) -> None:
        """Establish database connection."""
        try:
            self.connection = mysql.connector.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME
            )
        except Exception as e:
            raise DataAccessError(f"Failed to connect to database: {str(e)}")

    def store_payment(self, payment_data: Dict[str, Any]) -> str:
        """
        Store payment information in the database.
        
        Args:
            payment_data: Dictionary containing payment information
            
        Returns:
            Payment ID
        """
        try:
            cursor = self.connection.cursor()
            
            # Generate payment ID
            payment_id = f"PAY_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Prepare SQL query
            query = f"""
                INSERT INTO {TableNames.RENTAL_PAYMENT_HISTORY} (
                    id_Payment_History, ref_tenantID, ref_propertyID, 
                    ref_landlordID, ref_AgreementId, amount, payment_date,
                    payment_method, confirmation_number, status, note
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            
            # Prepare values
            values = (
                payment_id,
                payment_data.get('ref_tenantID'),
                payment_data.get('ref_propertyID'),
                payment_data.get('ref_landlordID'),
                payment_data.get('ref_AgreementId'),
                payment_data['amount'],
                payment_data['payment_date'],
                payment_data['payment_method'],
                payment_data['confirmation_number'],
                payment_data['status'],
                payment_data['note']
            )
            
            # Execute query
            cursor.execute(query, values)
            self.connection.commit()
            
            return payment_id
        except Exception as e:
            self.connection.rollback()
            raise DataAccessError(f"Failed to store payment: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def get_payments_by_period(self, month: int, year: int) -> List[Dict[str, Any]]:
        """
        Retrieve payments for a specific month and year.
        
        Args:
            month: Month number (1-12)
            year: Year
            
        Returns:
            List of payment records
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = f"""
                SELECT * FROM {TableNames.RENTAL_PAYMENT_HISTORY}
                WHERE MONTH(payment_date) = %s AND YEAR(payment_date) = %s
                AND ddate IS NULL
            """
            
            cursor.execute(query, (month, year))
            return cursor.fetchall()
        except Exception as e:
            raise DataAccessError(f"Failed to retrieve payments: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def __del__(self):
        if self.connection:
            self.connection.close() 