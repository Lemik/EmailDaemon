import mysql.connector
from typing import List, Dict, Any, Optional
from datetime import datetime
from ...core.config import Config
from ...core.exceptions import DataAccessError
from ...core.constants import TableNames

class AgreementAccess:
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
                WHERE ref_tenantID = %s
                AND ddate IS NULL
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
                WHERE id_agreement = %s
                AND ddate IS NULL
            """
            
            cursor.execute(query, (agreement_id,))
            return cursor.fetchone()
        except Exception as e:
            raise DataAccessError(f"Failed to retrieve agreement: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def __del__(self):
        if self.connection:
            self.connection.close() 