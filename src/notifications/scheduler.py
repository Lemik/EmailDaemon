import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from ..core.config import Config
from ..core.exceptions import NotificationError
from ..core.constants import NotificationLevel
from .notification_manager import NotificationManager
from ..data.access.payment_access import PaymentAccess
from ..data.access.agreement_access import AgreementAccess

class NotificationScheduler:
    def __init__(self):
        self.config = Config()
        self.notification_manager = NotificationManager()
        self.payment_access = PaymentAccess()
        self.agreement_access = AgreementAccess()
        self.check_interval = self.config.get('NOTIFICATION_CHECK_INTERVAL', 300)  # 5 minutes

    def start(self):
        """Start the notification scheduler."""
        try:
            # Schedule daily tasks
            schedule.every().day.at("00:00").do(self.check_due_payments)
            schedule.every().day.at("09:00").do(self.check_late_payments)
            schedule.every().day.at("15:00").do(self.retry_failed_notifications)
            
            # Schedule monthly tasks
            schedule.every().month.at("01 00:00").do(self.send_monthly_summaries)
            
            # Run the scheduler
            while True:
                schedule.run_pending()
                time.sleep(self.check_interval)
        except Exception as e:
            raise NotificationError(f"Failed to start notification scheduler: {str(e)}")

    def check_due_payments(self):
        """Check for upcoming due payments and send reminders."""
        try:
            # Get tomorrow's date
            tomorrow = datetime.now() + timedelta(days=1)
            
            # Get agreements with payments due tomorrow
            agreements = self.agreement_access.get_agreements_due_on(tomorrow)
            
            for agreement in agreements:
                # Send due date reminder
                self.notification_manager.send_notification(
                    user_id=agreement['ref_tenantID'],
                    level=NotificationLevel.DUE_DATE_REMINDER,
                    template_name='due_date_reminder',
                    template_data={
                        'tenant_name': agreement['tenant_name'],
                        'amount': agreement['amount'],
                        'due_date': tomorrow,
                        'days_until': 1
                    },
                    payment_id=None
                )
        except Exception as e:
            raise NotificationError(f"Failed to check due payments: {str(e)}")

    def check_late_payments(self):
        """Check for late payments and send notifications."""
        try:
            # Get agreements with payments due yesterday
            yesterday = datetime.now() - timedelta(days=1)
            agreements = self.agreement_access.get_agreements_due_on(yesterday)
            
            for agreement in agreements:
                # Check if payment was received
                payments = self.payment_access.get_payments_for_agreement(
                    agreement['id_Tenancy_Agreement'],
                    yesterday,
                    yesterday
                )
                
                if not payments:
                    # No payment received - send missing payment notification
                    self.notification_manager.send_notification(
                        user_id=agreement['ref_tenantID'],
                        level=NotificationLevel.MISSING_PAYMENT,
                        template_name='missing_payment',
                        template_data={
                            'tenant_name': agreement['tenant_name'],
                            'amount': agreement['amount'],
                            'due_date': yesterday
                        },
                        payment_id=None
                    )
                else:
                    # Payment received but late - send late payment notification
                    payment = payments[0]
                    days_late = (datetime.now() - yesterday).days
                    
                    self.notification_manager.send_notification(
                        user_id=agreement['ref_tenantID'],
                        level=NotificationLevel.LATE_PAYMENT,
                        template_name='late_payment',
                        template_data={
                            'tenant_name': agreement['tenant_name'],
                            'amount': agreement['amount'],
                            'due_date': yesterday,
                            'days_late': days_late
                        },
                        payment_id=payment['id_Payment_History']
                    )
        except Exception as e:
            raise NotificationError(f"Failed to check late payments: {str(e)}")

    def retry_failed_notifications(self):
        """Retry sending failed notifications."""
        try:
            self.notification_manager.retry_failed_notifications()
        except Exception as e:
            raise NotificationError(f"Failed to retry notifications: {str(e)}")

    def send_monthly_summaries(self):
        """Send monthly payment summaries to all users."""
        try:
            self.notification_manager.schedule_monthly_summaries()
        except Exception as e:
            raise NotificationError(f"Failed to send monthly summaries: {str(e)}")

def main():
    """Main entry point for the notification scheduler."""
    try:
        scheduler = NotificationScheduler()
        scheduler.start()
    except Exception as e:
        print(f"Error running notification scheduler: {str(e)}")
        raise

if __name__ == "__main__":
    main() 