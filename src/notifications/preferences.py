from typing import Dict, Any, List, Optional
from datetime import datetime
from ..core.config import Config
from ..core.exceptions import NotificationError
from ..core.constants import NotificationLevel, NotificationType, TableNames

class NotificationPreferences:
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

    def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get notification preferences for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary containing user preferences or None if not found
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = f"""
                SELECT * FROM {TableNames.NOTIFICATION_PREFERENCES}
                WHERE ref_userID = %s
                AND ddate IS NULL
            """
            cursor.execute(query, (user_id,))
            preferences = cursor.fetchone()
            
            if preferences:
                # Convert notification_levels bitmask to list of enabled notifications
                preferences['enabled_notifications'] = self.get_enabled_notifications(
                    preferences['notification_levels']
                )
            
            return preferences
        except Exception as e:
            raise NotificationError(f"Failed to get user preferences: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> None:
        """
        Update notification preferences for a user.
        
        Args:
            user_id: User ID
            preferences: Dictionary containing updated preferences
        """
        try:
            cursor = self.connection.cursor()
            
            # Check if preferences exist
            existing = self.get_user_preferences(user_id)
            
            if existing:
                # Update existing preferences
                query = f"""
                    UPDATE {TableNames.NOTIFICATION_PREFERENCES}
                    SET notification_type = %s,
                        email_address = %s,
                        telegram_chat_id = %s,
                        notification_levels = %s,
                        udate = CURRENT_TIMESTAMP
                    WHERE ref_userID = %s
                    AND ddate IS NULL
                """
                values = (
                    preferences.get('notification_type', existing['notification_type']),
                    preferences.get('email_address', existing['email_address']),
                    preferences.get('telegram_chat_id', existing['telegram_chat_id']),
                    preferences.get('notification_levels', existing['notification_levels']),
                    user_id
                )
            else:
                # Insert new preferences
                query = f"""
                    INSERT INTO {TableNames.NOTIFICATION_PREFERENCES}
                    (ref_userID, notification_type, email_address, telegram_chat_id, notification_levels)
                    VALUES (%s, %s, %s, %s, %s)
                """
                values = (
                    user_id,
                    preferences.get('notification_type', NotificationType.EMAIL),
                    preferences.get('email_address'),
                    preferences.get('telegram_chat_id'),
                    preferences.get('notification_levels', 0)
                )
            
            cursor.execute(query, values)
            self.connection.commit()
        except Exception as e:
            raise NotificationError(f"Failed to update user preferences: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def enable_notification(self, user_id: str, notification_level: NotificationLevel) -> None:
        """
        Enable a specific notification type for a user.
        
        Args:
            user_id: User ID
            notification_level: Notification level to enable
        """
        try:
            preferences = self.get_user_preferences(user_id)
            if not preferences:
                raise NotificationError(f"No preferences found for user {user_id}")
            
            current_levels = preferences['notification_levels']
            new_levels = current_levels | notification_level.value
            
            self.update_user_preferences(user_id, {
                'notification_levels': new_levels
            })
        except Exception as e:
            raise NotificationError(f"Failed to enable notification: {str(e)}")

    def disable_notification(self, user_id: str, notification_level: NotificationLevel) -> None:
        """
        Disable a specific notification type for a user.
        
        Args:
            user_id: User ID
            notification_level: Notification level to disable
        """
        try:
            preferences = self.get_user_preferences(user_id)
            if not preferences:
                raise NotificationError(f"No preferences found for user {user_id}")
            
            current_levels = preferences['notification_levels']
            new_levels = current_levels & ~notification_level.value
            
            self.update_user_preferences(user_id, {
                'notification_levels': new_levels
            })
        except Exception as e:
            raise NotificationError(f"Failed to disable notification: {str(e)}")

    def is_notification_enabled(self, current_levels: int, notification_level: NotificationLevel) -> bool:
        """
        Check if a specific notification type is enabled.
        
        Args:
            current_levels: Current notification levels bitmask
            notification_level: Notification level to check
            
        Returns:
            True if the notification type is enabled
        """
        return bool(current_levels & notification_level.value)

    def get_enabled_notifications(self, current_levels: int) -> List[str]:
        """
        Get list of enabled notification types.
        
        Args:
            current_levels: Current notification levels bitmask
            
        Returns:
            List of enabled notification type names
        """
        return [
            level.name for level in NotificationLevel
            if self.is_notification_enabled(current_levels, level)
        ] 