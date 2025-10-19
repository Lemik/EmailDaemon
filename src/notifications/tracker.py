from typing import Dict, Any, List, Optional
from datetime import datetime
from ..core.config import Config
from ..core.exceptions import NotificationError
from ..core.constants import NotificationType, TableNames

class NotificationTracker:
    def __init__(self):
        self.config = Config()
        self.connection = None
        self._connect()

    def _connect(self) -> None:
        """Establish database connection."""
        try:
            self.connection = self.config.get_db_connection()
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
                (ref_userID, ref_payment_id, notification_type,
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
        """
        Update the status of a notification.
        
        Args:
            notification_id: ID of the notification record
            status: New status
            error_message: Optional error message if status is 'failed'
        """
        try:
            cursor = self.connection.cursor()
            query = f"""
                UPDATE {TableNames.RENTAL_PAYMENT_NOTIFICATIONS}
                SET notification_status = %s,
                    sent_at = CASE WHEN %s = 'sent' THEN CURRENT_TIMESTAMP ELSE sent_at END,
                    message_content = CASE WHEN %s IS NOT NULL 
                                         THEN CONCAT(message_content, '\nError: ', %s)
                                         ELSE message_content END,
                    udate = CURRENT_TIMESTAMP
                WHERE id_Notification = %s
            """
            values = (status, status, error_message, error_message, notification_id)
            cursor.execute(query, values)
            self.connection.commit()
        except Exception as e:
            raise NotificationError(f"Failed to update notification status: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def get_notification_history(self, user_id: str, start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get notification history for a user.
        
        Args:
            user_id: User ID
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            List of notification records
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = f"""
                SELECT * FROM {TableNames.RENTAL_PAYMENT_NOTIFICATIONS}
                WHERE ref_userID = %s
                AND ddate IS NULL
            """
            params = [user_id]
            
            if start_date:
                query += " AND crdate >= %s"
                params.append(start_date)
            if end_date:
                query += " AND crdate <= %s"
                params.append(end_date)
                
            query += " ORDER BY crdate DESC"
            
            cursor.execute(query, params)
            return cursor.fetchall()
        except Exception as e:
            raise NotificationError(f"Failed to get notification history: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def get_failed_notifications(self, max_retries: int = 3) -> List[Dict[str, Any]]:
        """
        Get notifications that failed to send and haven't exceeded max retries.
        
        Args:
            max_retries: Maximum number of retry attempts
            
        Returns:
            List of failed notification records
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = f"""
                SELECT * FROM {TableNames.RENTAL_PAYMENT_NOTIFICATIONS}
                WHERE notification_status = 'failed'
                AND retry_count < %s
                AND ddate IS NULL
                ORDER BY crdate ASC
            """
            cursor.execute(query, (max_retries,))
            return cursor.fetchall()
        except Exception as e:
            raise NotificationError(f"Failed to get failed notifications: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def increment_retry_count(self, notification_id: int) -> None:
        """
        Increment the retry count for a notification.
        
        Args:
            notification_id: ID of the notification record
        """
        try:
            cursor = self.connection.cursor()
            query = f"""
                UPDATE {TableNames.RENTAL_PAYMENT_NOTIFICATIONS}
                SET retry_count = retry_count + 1,
                    udate = CURRENT_TIMESTAMP
                WHERE id_Notification = %s
            """
            cursor.execute(query, (notification_id,))
            self.connection.commit()
        except Exception as e:
            raise NotificationError(f"Failed to increment retry count: {str(e)}")
        finally:
            if cursor:
                cursor.close() 