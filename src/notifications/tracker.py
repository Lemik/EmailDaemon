from typing import Dict, Any, List, Optional
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import PROD_DB_CONFIG
from ..core.exceptions import NotificationError
from ..core.constants import TableNames

class NotificationTracker:
    def __init__(self):
        self.connection = None
        self._connect()

    def _connect(self) -> None:
        """Establish database connection."""
        try:
            import mysql.connector
            self.connection = mysql.connector.connect(**PROD_DB_CONFIG)
        except Exception as e:
            raise NotificationError(f"Failed to connect to database: {str(e)}")

    def log_notification(self, user_id: str, payment_id: Optional[str],
                        notification_type: str, channel: str,
                        message: str, status: str = 'pending') -> int:
        """
        Log a notification in the database.

        Args:
            user_id: User ID
            payment_id: Optional payment ID if notification is payment-related
            notification_type: Type of notification
            channel: Notification channel (email/telegram/both)
            message: Notification message
            status: Initial status of the notification

        Returns:
            ID of the created notification record
        """
        try:
            cursor = self.connection.cursor()
            query = f"""
                INSERT INTO {TableNames.RENTAL_PAYMENT_NOTIFICATIONS}
                (user_id, payment_id, notification_type,
                notification_channel, message_content, notification_status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (
                user_id,
                payment_id,
                notification_type,
                channel,
                message,
                status
            )
            cursor.execute(query, values)
            self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            raise NotificationError(f"Failed to log notification: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def update_notification_status(self, notification_id: int, status: str,
                                 error_message: Optional[str] = None) -> None:
        """Update the status of a notification."""
        try:
            cursor = self.connection.cursor()
            query = f"""
                UPDATE {TableNames.RENTAL_PAYMENT_NOTIFICATIONS}
                SET notification_status = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            values = (status, notification_id)
            cursor.execute(query, values)
            if error_message and status == 'failed':
                cursor.execute(
                    f"""
                    UPDATE {TableNames.RENTAL_PAYMENT_NOTIFICATIONS}
                    SET error_message = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (error_message, notification_id),
                )
            self.connection.commit()
        except Exception as e:
            raise NotificationError(f"Failed to update notification status: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def get_notification_history(self, user_id: str, start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get notification history for a user."""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = f"""
                SELECT * FROM {TableNames.RENTAL_PAYMENT_NOTIFICATIONS}
                WHERE user_id = %s
                AND deleted_at IS NULL
            """
            params = [user_id]

            if start_date:
                query += " AND created_at >= %s"
                params.append(start_date)
            if end_date:
                query += " AND created_at <= %s"
                params.append(end_date)

            query += " ORDER BY created_at DESC"

            cursor.execute(query, params)
            return cursor.fetchall()
        except Exception as e:
            raise NotificationError(f"Failed to get notification history: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def get_failed_notifications(self, max_retries: int = 3) -> List[Dict[str, Any]]:
        """Get notifications that failed to send and haven't exceeded max retries."""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = f"""
                SELECT * FROM {TableNames.RENTAL_PAYMENT_NOTIFICATIONS}
                WHERE notification_status = 'failed'
                AND retry_count < %s
                AND deleted_at IS NULL
                ORDER BY created_at ASC
            """
            cursor.execute(query, (max_retries,))
            return cursor.fetchall()
        except Exception as e:
            raise NotificationError(f"Failed to get failed notifications: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def increment_retry_count(self, notification_id: int) -> None:
        """Increment the retry count for a notification."""
        try:
            cursor = self.connection.cursor()
            query = f"""
                UPDATE {TableNames.RENTAL_PAYMENT_NOTIFICATIONS}
                SET retry_count = retry_count + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            cursor.execute(query, (notification_id,))
            self.connection.commit()
        except Exception as e:
            raise NotificationError(f"Failed to increment retry count: {str(e)}")
        finally:
            if cursor:
                cursor.close()
