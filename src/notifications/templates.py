from datetime import datetime
from typing import Dict, Any

class NotificationTemplates:
    @staticmethod
    def late_payment(tenant_name: str, amount: float, due_date: datetime, days_late: int) -> str:
        return f"""
Dear {tenant_name},

This is a reminder that your rent payment of ${amount:.2f} was due on {due_date.strftime('%Y-%m-%d')}.
Your payment is currently {days_late} days late.

Please process your payment as soon as possible to avoid any late fees.

Best regards,
Property Management
"""

    @staticmethod
    def missing_payment(tenant_name: str, amount: float, due_date: datetime) -> str:
        return f"""
Dear {tenant_name},

We have not received your rent payment of ${amount:.2f} which was due on {due_date.strftime('%Y-%m-%d')}.

Please process your payment immediately to avoid any late fees or potential legal action.

Best regards,
Property Management
"""

    @staticmethod
    def payment_discrepancy(tenant_name: str, expected: float, actual: float, payment_date: datetime) -> str:
        return f"""
Dear {tenant_name},

We noticed a discrepancy in your recent rent payment received on {payment_date.strftime('%Y-%m-%d')}.

Expected amount: ${expected:.2f}
Received amount: ${actual:.2f}
Difference: ${(actual - expected):.2f}

Please contact us to resolve this matter.

Best regards,
Property Management
"""

    @staticmethod
    def monthly_summary(tenant_name: str, month: int, year: int, payments: Dict[str, Any]) -> str:
        total_expected = sum(p['expected_amount'] for p in payments.values())
        total_received = sum(p['actual_amount'] for p in payments.values())
        
        summary = f"""
Dear {tenant_name},

Here is your payment summary for {datetime(year, month, 1).strftime('%B %Y')}:

Total Expected: ${total_expected:.2f}
Total Received: ${total_received:.2f}
Status: {'Complete' if total_received >= total_expected else 'Incomplete'}

Payment Details:
"""
        
        for date, payment in payments.items():
            summary += f"""
Date: {date}
Expected: ${payment['expected_amount']:.2f}
Received: ${payment['actual_amount']:.2f}
Status: {payment['status']}
"""
        
        summary += """
Best regards,
Property Management
"""
        return summary

    @staticmethod
    def due_date_reminder(tenant_name: str, amount: float, due_date: datetime, days_until: int) -> str:
        return f"""
Dear {tenant_name},

This is a friendly reminder that your rent payment of ${amount:.2f} is due in {days_until} days ({due_date.strftime('%Y-%m-%d')}).

Please ensure your payment is processed on time to avoid any late fees.

Best regards,
Property Management
"""

    @staticmethod
    def payment_received(tenant_name: str, amount: float, payment_date: datetime, confirmation_number: str) -> str:
        return f"""
Dear {tenant_name},

We have received your rent payment of ${amount:.2f} on {payment_date.strftime('%Y-%m-%d')}.

Confirmation Number: {confirmation_number}

Thank you for your timely payment.

Best regards,
Property Management
"""

    @staticmethod
    def system_alert(alert_type: str, message: str, severity: str) -> str:
        return f"""
SYSTEM ALERT - {severity.upper()}

Type: {alert_type}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Message: {message}

Please check the system logs for more details.
""" 