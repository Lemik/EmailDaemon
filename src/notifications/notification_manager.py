from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time
from ..core.config import Config
from ..core.exceptions import NotificationError
from ..core.constants import NotificationLevel, NotificationType, TableNames
from .email_notifier import EmailNotifier
from .telegram_notifier import TelegramNotifier
from .preferences import NotificationPreferences
from .templates import NotificationTemplates
from .tracker import NotificationTracker

class NotificationManager:
    def __init__(self):
        self.config = Config()
        self.email_notifier = EmailNotifier()
        self.telegram_notifier = TelegramNotifier()
        self.preferences = NotificationPreferences()
        self.tracker = NotificationTracker()
        self.templates = NotificationTemplates()
        self.max_retries = self.config.get('NOTIFICATION_MAX_RETRIES', 3)
        self.retry_delay = self.config.get('NOTIFICATION_RETRY_DELAY', 300)  # 5 minutes

    def send_notification(self, user_id: str, level: NotificationLevel,
                         template_name: str, template_data: Dict[str, Any],
                         payment_id: Optional[str] = None) -> None:
        """
        Send notification to a user based on their preferences.
        
        Args:
            user_id: User ID
            level: Notification level
            template_name: Name of the template to use
            template_data: Data for template formatting
            payment_id: Optional payment ID if notification is payment-related
        """
        try:
            # Get user preferences
            preferences = self.preferences.get_user_preferences(user_id)
            if not preferences:
                raise NotificationError(f"No notification preferences found for user {user_id}")

            # Check if notification level is enabled
            if not self.preferences.is_notification_enabled(preferences['notification_levels'], level):
                return

            # Get template method
            template_method = getattr(self.templates, template_name, None)
            if not template_method:
                raise NotificationError(f"Template {template_name} not found")

            # Generate message
            message = template_method(**template_data)

            # Log notification
            notification_id = self.tracker.log_notification(
                user_id=user_id,
                payment_id=payment_id,
                notification_type=level.name,
                channel=preferences['notification_type'],
                message=message
            )

            # Send notifications based on preferences
            success = True
            error_message = None

            try:
                if preferences['notification_type'] in [NotificationType.EMAIL, NotificationType.BOTH]:
                    self.email_notifier.send(
                        to=preferences['email_address'],
                        subject=f"Payment Notification: {level.name}",
                        message=message,
                        data=template_data
                    )

                if preferences['notification_type'] in [NotificationType.TELEGRAM, NotificationType.BOTH]:
                    self.telegram_notifier.send(
                        chat_id=preferences['telegram_chat_id'],
                        message=message,
                        data=template_data
                    )

                # Update status to sent
                self.tracker.update_notification_status(notification_id, 'sent')

            except Exception as e:
                success = False
                error_message = str(e)
                self.tracker.update_notification_status(
                    notification_id, 'failed', error_message
                )
                raise NotificationError(f"Failed to send notification: {error_message}")

        except Exception as e:
            raise NotificationError(f"Failed to process notification: {str(e)}")

    def send_bulk_notifications(self, notifications: List[Dict[str, Any]]) -> None:
        """
        Send multiple notifications efficiently.
        
        Args:
            notifications: List of notification dictionaries with:
                - user_id
                - level
                - template_name
                - template_data
                - payment_id (optional)
        """
        for notification in notifications:
            try:
                self.send_notification(
                    user_id=notification['user_id'],
                    level=notification['level'],
                    template_name=notification['template_name'],
                    template_data=notification['template_data'],
                    payment_id=notification.get('payment_id')
                )
            except Exception as e:
                # Log error but continue with other notifications
                print(f"Failed to send notification: {str(e)}")

    def retry_failed_notifications(self) -> None:
        """Retry sending failed notifications."""
        try:
            failed_notifications = self.tracker.get_failed_notifications(self.max_retries)
            
            for notification in failed_notifications:
                try:
                    # Get user preferences
                    preferences = self.preferences.get_user_preferences(notification['ref_userID'])
                    if not preferences:
                        continue

                    # Increment retry count
                    self.tracker.increment_retry_count(notification['id_Notification'])

                    # Retry sending
                    if preferences['notification_type'] in [NotificationType.EMAIL, NotificationType.BOTH]:
                        self.email_notifier.send(
                            to=preferences['email_address'],
                            subject=f"Payment Notification: {notification['notification_type']}",
                            message=notification['message_content']
                        )

                    if preferences['notification_type'] in [NotificationType.TELEGRAM, NotificationType.BOTH]:
                        self.telegram_notifier.send(
                            chat_id=preferences['telegram_chat_id'],
                            message=notification['message_content']
                        )

                    # Update status to sent
                    self.tracker.update_notification_status(
                        notification['id_Notification'], 'sent'
                    )

                except Exception as e:
                    # Update status to failed
                    self.tracker.update_notification_status(
                        notification['id_Notification'],
                        'failed',
                        f"Retry failed: {str(e)}"
                    )

                # Add delay between retries
                time.sleep(self.retry_delay)

        except Exception as e:
            raise NotificationError(f"Failed to retry notifications: {str(e)}")

    def schedule_monthly_summaries(self) -> None:
        """Schedule monthly summary notifications for all users."""
        try:
            # Get current month and year
            now = datetime.now()
            month = now.month
            year = now.year

            # Get all users with notification preferences
            cursor = self.connection.cursor(dictionary=True)
            query = f"""
                SELECT DISTINCT np.ref_userID, np.notification_levels
                FROM {TableNames.NOTIFICATION_PREFERENCES} np
                WHERE np.ddate IS NULL
            """
            cursor.execute(query)
            users = cursor.fetchall()

            for user in users:
                # Check if monthly summary is enabled
                if self.preferences.is_notification_enabled(
                    user['notification_levels'],
                    NotificationLevel.MONTHLY_SUMMARY
                ):
                    # Get user's payments for the month
                    payments = self._get_user_monthly_payments(
                        user['ref_userID'],
                        month,
                        year
                    )

                    if payments:
                        # Send monthly summary
                        self.send_notification(
                            user_id=user['ref_userID'],
                            level=NotificationLevel.MONTHLY_SUMMARY,
                            template_name='monthly_summary',
                            template_data={
                                'tenant_name': payments[0]['tenant_name'],
                                'month': month,
                                'year': year,
                                'payments': payments
                            }
                        )

        except Exception as e:
            raise NotificationError(f"Failed to schedule monthly summaries: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def _get_user_monthly_payments(self, user_id: str, month: int, year: int) -> List[Dict[str, Any]]:
        """Get user's payments for a specific month."""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = f"""
                SELECT 
                    rph.*,
                    pt.Fname as tenant_name,
                    ta.amount as expected_amount
                FROM {TableNames.RENTAL_PAYMENT_HISTORY} rph
                JOIN Property_tenant pt ON rph.ref_tenantID = pt.id_Property_tenant
                LEFT JOIN Tenancy_Agreement ta ON rph.ref_AgreementId = ta.id_Tenancy_Agreement
                WHERE rph.ref_tenantID = %s
                AND MONTH(rph.payment_date) = %s
                AND YEAR(rph.payment_date) = %s
                AND rph.ddate IS NULL
                ORDER BY rph.payment_date
            """
            cursor.execute(query, (user_id, month, year))
            return cursor.fetchall()
        except Exception as e:
            raise NotificationError(f"Failed to get monthly payments: {str(e)}")
        finally:
            if cursor:
                cursor.close() 