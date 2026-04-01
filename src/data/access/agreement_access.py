import mysql.connector
from typing import List, Dict, Any, Optional
from datetime import date, datetime
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from config import PROD_DB_CONFIG
from ...core.exceptions import DataAccessError
from ...core.constants import TableNames


class AgreementAccess:
    def __init__(self):
        self.connection = None
        self._connect()

    def _connect(self) -> None:
        """Establish database connection."""
        try:
            self.connection = mysql.connector.connect(**PROD_DB_CONFIG)
        except Exception as e:
            raise DataAccessError(f"Failed to connect to database: {str(e)}")

    def get_tenant_agreements(self, tenant_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve active agreements for a tenant.

        Args:
            tenant_id: Tenant ID

        Returns:
            List of agreement records
        """
        try:
            cursor = self.connection.cursor(dictionary=True)

            query = f"""
                SELECT * FROM {TableNames.RENTAL_AGREEMENTS}
                WHERE tenant_id = %s
                AND deleted_at IS NULL
                AND end_date >= CURDATE()
            """

            cursor.execute(query, (tenant_id,))
            return cursor.fetchall()
        except Exception as e:
            raise DataAccessError(f"Failed to retrieve agreements: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def get_agreement_by_id(self, agreement_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific agreement by ID.

        Args:
            agreement_id: Agreement ID

        Returns:
            Agreement record or None if not found
        """
        try:
            cursor = self.connection.cursor(dictionary=True)

            query = f"""
                SELECT * FROM {TableNames.RENTAL_AGREEMENTS}
                WHERE id_tenancy_agreement = %s
                AND deleted_at IS NULL
            """

            cursor.execute(query, (agreement_id,))
            return cursor.fetchone()
        except Exception as e:
            raise DataAccessError(f"Failed to retrieve agreement: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def get_agreements_due_on(self, due: date) -> List[Dict[str, Any]]:
        """Agreements whose rent is due on the calendar day of ``due`` and are active on that date."""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = f"""
                SELECT
                    ta.*,
                    CONCAT(pt.first_name, ' ', pt.last_name) AS tenant_name
                FROM {TableNames.RENTAL_AGREEMENTS} ta
                JOIN {TableNames.PROPERTY_TENANTS} pt
                    ON ta.tenant_id = pt.tenant_id AND ta.property_id = pt.property_id
                WHERE ta.payment_day = %s
                AND ta.deleted_at IS NULL
                AND pt.deleted_at IS NULL
                AND ta.start_date <= %s AND ta.end_date >= %s
            """
            d = due.date() if isinstance(due, datetime) else due
            cursor.execute(query, (d.day, d, d))
            return cursor.fetchall()
        except Exception as e:
            raise DataAccessError(f"Failed to retrieve agreements due on date: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def __del__(self):
        if self.connection:
            self.connection.close()
