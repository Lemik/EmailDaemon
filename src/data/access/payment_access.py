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
                query = f"""
                    SELECT
                        ta.*,
                        p.name as property_name,
                        p.address as property_address
                    FROM {TableNames.RENTAL_AGREEMENTS} ta
                    JOIN {TableNames.PROPERTIES} p ON ta.property_id = p.id_property
                    WHERE ta.tenant_id = %s
                    AND ta.deleted_at IS NULL
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
                query = f"""
                    SELECT
                        rph.*,
                        ta.amount as expected_amount,
                        ta.payment_day as due_day
                    FROM {TableNames.RENTAL_PAYMENT_HISTORY} rph
                    LEFT JOIN {TableNames.RENTAL_AGREEMENTS} ta
                        ON rph.agreement_id = ta.id_tenancy_agreement
                    WHERE rph.tenant_id = %s
                    AND rph.payment_date BETWEEN %s AND %s
                    AND rph.deleted_at IS NULL
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
                query = f"""
                    SELECT
                        rph.*,
                        pt.first_name as tenant_first_name,
                        pt.last_name as tenant_last_name,
                        ta.amount as expected_amount
                    FROM {TableNames.RENTAL_PAYMENT_HISTORY} rph
                    JOIN {TableNames.PROPERTY_TENANTS} pt
                        ON rph.tenant_id = pt.id_property_tenant
                    LEFT JOIN {TableNames.RENTAL_AGREEMENTS} ta
                        ON rph.agreement_id = ta.id_tenancy_agreement
                    WHERE rph.property_id = %s
                    AND MONTH(rph.payment_date) = %s
                    AND YEAR(rph.payment_date) = %s
                    AND rph.deleted_at IS NULL
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
                - tenant_id
                - property_id
                - landlord_id
                - agreement_id (optional)
                - amount
                - payment_date
                - payment_method (int)
                - confirmation_number
                - status (int)

        Returns:
            int: ID of the created payment record

        Raises:
            DataAccessError: If database operation fails
        """
        try:
            with self._get_connection() as connection:
                cursor = connection.cursor()
                query = f"""
                    INSERT INTO {TableNames.RENTAL_PAYMENT_HISTORY} (
                        tenant_id, property_id, landlord_id,
                        agreement_id, amount, payment_date,
                        payment_method, confirmation_number, status
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """
                values = (
                    payment_data['tenant_id'],
                    payment_data['property_id'],
                    payment_data['landlord_id'],
                    payment_data.get('agreement_id'),
                    payment_data['amount'],
                    payment_data['payment_date'],
                    payment_data['payment_method'],
                    payment_data['confirmation_number'],
                    payment_data['status'],
                )
                cursor.execute(query, values)
                connection.commit()
                return cursor.lastrowid
        except Error as e:
            raise DataAccessError(f"Failed to create payment record: {str(e)}")

    def update_payment_status(self, payment_id: int,
                            status: int) -> bool:
        """
        Update the status of a payment record

        Args:
            payment_id (int): ID of the payment record
            status (int): New status code (see PaymentRecordStatus)

        Returns:
            bool: True if update successful

        Raises:
            DataAccessError: If database operation fails
        """
        try:
            with self._get_connection() as connection:
                cursor = connection.cursor()
                query = f"""
                    UPDATE {TableNames.RENTAL_PAYMENT_HISTORY}
                    SET status = %s
                    WHERE id_payment_history = %s
                """
                cursor.execute(query, (status, payment_id))
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
            'tenant_id',
            'property_id',
            'landlord_id',
            'amount',
            'payment_date',
            'payment_method',
            'confirmation_number',
            'status',
        ]

        for field in required_fields:
            if field not in payment_data:
                raise DataAccessError(f"Missing required field: {field}")

        try:
            amount = float(payment_data['amount'])
            if amount <= 0:
                raise DataAccessError("Payment amount must be greater than 0")
        except (ValueError, TypeError):
            raise DataAccessError("Invalid payment amount format")

        if not isinstance(payment_data['payment_date'], datetime):
            raise DataAccessError("Invalid payment date format")

        if not isinstance(payment_data['payment_method'], int):
            raise DataAccessError("payment_method must be an integer (see PaymentMethodCode)")

        if not isinstance(payment_data['status'], int):
            raise DataAccessError("status must be an integer (see PaymentRecordStatus)")

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
            'tenant_id',
            'property_id',
            'landlord_id',
            'start_date',
            'end_date',
            'amount',
            'payment_day',
        ]

        for field in required_fields:
            if field not in agreement_data:
                raise DataAccessError(f"Missing required field: {field}")

        if not isinstance(agreement_data['start_date'], datetime):
            raise DataAccessError("Invalid start date format")
        if not isinstance(agreement_data['end_date'], datetime):
            raise DataAccessError("Invalid end date format")
        if agreement_data['start_date'] >= agreement_data['end_date']:
            raise DataAccessError("End date must be after start date")

        try:
            amount = float(agreement_data['amount'])
            if amount <= 0:
                raise DataAccessError("Agreement amount must be greater than 0")
        except (ValueError, TypeError):
            raise DataAccessError("Invalid agreement amount format")

        try:
            payment_day = int(agreement_data['payment_day'])
            if not 1 <= payment_day <= 31:
                raise DataAccessError("Payment day must be between 1 and 31")
        except (ValueError, TypeError):
            raise DataAccessError("Invalid payment day format")

        return True


class PaymentAccess:
    def __init__(self):
        self.connection = None
        self._connect()

    def _connect(self) -> None:
        """Establish database connection."""
        try:
            self.connection = mysql.connector.connect(**PROD_DB_CONFIG)
        except Exception as e:
            raise DataAccessError(f"Failed to connect to database: {str(e)}")

    def store_payment(self, payment_data: Dict[str, Any]) -> str:
        """
        Store payment information in the database.

        Args:
            payment_data: Dictionary containing payment information

        Returns:
            New row id as string (id_payment_history)
        """
        try:
            cursor = self.connection.cursor()

            query = f"""
                INSERT INTO {TableNames.RENTAL_PAYMENT_HISTORY} (
                    tenant_id, property_id, landlord_id,
                    agreement_id, amount, payment_date,
                    payment_method, confirmation_number, status
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """

            values = (
                payment_data.get('tenant_id'),
                payment_data.get('property_id'),
                payment_data.get('landlord_id'),
                payment_data.get('agreement_id'),
                payment_data['amount'],
                payment_data['payment_date'],
                payment_data['payment_method'],
                payment_data['confirmation_number'],
                payment_data['status'],
            )

            cursor.execute(query, values)
            self.connection.commit()

            return str(cursor.lastrowid)
        except Exception as e:
            self.connection.rollback()
            raise DataAccessError(f"Failed to store payment: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def get_payments_for_agreement(
        self, agreement_id: int, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Payments linked to an agreement within a date range (by payment_date)."""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = f"""
                SELECT * FROM {TableNames.RENTAL_PAYMENT_HISTORY}
                WHERE agreement_id = %s
                AND payment_date BETWEEN DATE(%s) AND DATE(%s)
                AND deleted_at IS NULL
            """
            cursor.execute(query, (agreement_id, start_date, end_date))
            return cursor.fetchall()
        except Exception as e:
            raise DataAccessError(f"Failed to retrieve payments for agreement: {str(e)}")
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
                AND deleted_at IS NULL
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
