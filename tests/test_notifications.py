import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from src.core.exceptions import NotificationError
from src.core.constants import NotificationLevel
from src.notifications.notification_manager import NotificationManager
from src.notifications.preferences import NotificationPreferences
from src.notifications.tracker import NotificationTracker
from src.notifications.templates import NotificationTemplates

class TestNotificationTemplates(unittest.TestCase):
    def setUp(self):
        self.tenant_name = "John Doe"
        self.amount = 1000.00
        self.due_date = datetime.now()
        self.days_late = 2

    def test_late_payment_template(self):
        template = NotificationTemplates.late_payment(
            self.tenant_name,
            self.amount,
            self.due_date,
            self.days_late
        )
        self.assertIn(self.tenant_name, template)
        self.assertIn(str(self.amount), template)
        self.assertIn(str(self.days_late), template)

    def test_missing_payment_template(self):
        template = NotificationTemplates.missing_payment(
            self.tenant_name,
            self.amount,
            self.due_date
        )
        self.assertIn(self.tenant_name, template)
        self.assertIn(str(self.amount), template)

    def test_payment_discrepancy_template(self):
        expected = 1000.00
        actual = 900.00
        template = NotificationTemplates.payment_discrepancy(
            self.tenant_name,
            expected,
            actual,
            self.due_date
        )
        self.assertIn(self.tenant_name, template)
        self.assertIn(str(expected), template)
        self.assertIn(str(actual), template)

class TestNotificationPreferences(unittest.TestCase):
    def setUp(self):
        self.preferences = NotificationPreferences()
        self.user_id = "test_user"
        self.mock_db = Mock()

    @patch('src.notifications.preferences.Database')
    def test_get_user_preferences(self, mock_db):
        mock_db.return_value = self.mock_db
        self.mock_db.fetch_one.return_value = {
            'user_id': self.user_id,
            'levels': 7,  # All notifications enabled
            'email_enabled': True,
            'telegram_enabled': False
        }

        prefs = self.preferences.get_user_preferences(self.user_id)
        self.assertEqual(prefs['user_id'], self.user_id)
        self.assertTrue(prefs['email_enabled'])
        self.assertFalse(prefs['telegram_enabled'])

    @patch('src.notifications.preferences.Database')
    def test_update_user_preferences(self, mock_db):
        mock_db.return_value = self.mock_db
        self.mock_db.fetch_one.return_value = None

        prefs = {
            'user_id': self.user_id,
            'levels': 7,
            'email_enabled': True,
            'telegram_enabled': True
        }
        self.preferences.update_user_preferences(prefs)
        self.mock_db.execute.assert_called_once()

class TestNotificationTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = NotificationTracker()
        self.user_id = "test_user"
        self.payment_id = 1
        self.mock_db = Mock()

    @patch('src.notifications.tracker.Database')
    def test_log_notification(self, mock_db):
        mock_db.return_value = self.mock_db
        self.mock_db.fetch_one.return_value = {'id': 1}

        notification_id = self.tracker.log_notification(
            self.user_id,
            self.payment_id,
            NotificationLevel.LATE_PAYMENT,
            'email',
            'Test message'
        )
        self.assertEqual(notification_id, 1)
        self.mock_db.execute.assert_called_once()

    @patch('src.notifications.tracker.Database')
    def test_update_notification_status(self, mock_db):
        mock_db.return_value = self.mock_db
        self.tracker.update_notification_status(1, 'failed', 'Test error')
        self.mock_db.execute.assert_called_once()

class TestNotificationManager(unittest.TestCase):
    def setUp(self):
        self.manager = NotificationManager()
        self.user_id = "test_user"
        self.payment_id = 1

    @patch('src.notifications.notification_manager.EmailNotifier')
    @patch('src.notifications.notification_manager.TelegramNotifier')
    @patch('src.notifications.notification_manager.NotificationPreferences')
    def test_send_notification(self, mock_prefs, mock_telegram, mock_email):
        mock_prefs.return_value.get_user_preferences.return_value = {
            'email_enabled': True,
            'telegram_enabled': False
        }
        mock_email.return_value.send.return_value = True

        result = self.manager.send_notification(
            self.user_id,
            NotificationLevel.LATE_PAYMENT,
            'late_payment',
            {
                'tenant_name': 'John Doe',
                'amount': 1000.00,
                'due_date': datetime.now(),
                'days_late': 2
            },
            self.payment_id
        )
        self.assertTrue(result)
        mock_email.return_value.send.assert_called_once()

    @patch('src.notifications.notification_manager.NotificationTracker')
    def test_retry_failed_notifications(self, mock_tracker):
        mock_tracker.return_value.get_failed_notifications.return_value = [
            {
                'id': 1,
                'user_id': self.user_id,
                'notification_type': NotificationLevel.LATE_PAYMENT,
                'channel': 'email',
                'message': 'Test message'
            }
        ]
        self.manager.retry_failed_notifications()
        mock_tracker.return_value.update_notification_status.assert_called_once()

if __name__ == '__main__':
    unittest.main() 