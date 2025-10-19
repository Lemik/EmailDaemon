from enum import IntEnum

class NotificationLevel(IntEnum):
    LATE_PAYMENT = 1 << 0      # 0001
    MISSING_PAYMENT = 1 << 1   # 0010
    PAYMENT_DISCREPANCY = 1 << 2 # 0100
    MONTHLY_SUMMARY = 1 << 3   # 1000
    DUE_DATE_REMINDER = 1 << 4 # 10000
    PAYMENT_RECEIVED = 1 << 5  # 100000
    SYSTEM_ALERTS = 1 << 6     # 1000000

class PaymentStatus:
    ON_TIME = 'on_time'
    LATE = 'late'
    MISSING = 'missing'
    INCORRECT = 'incorrect'
    PARTIAL = 'partial'

class NotificationType:
    EMAIL = 'email'
    TELEGRAM = 'telegram'
    BOTH = 'both'

# Database table names
class TableNames:
    RENTAL_PAYMENT_HISTORY = 'Rental_Payment_History'
    RENTAL_PAYMENT_ANALYSIS = 'Rental_Payment_Analysis'
    NOTIFICATION_PREFERENCES = 'Notification_Preferences'
    TENANTS = 'Tenants'
    PROPERTIES = 'Properties'
    LANDLORDS = 'Landlords'
    RENTAL_AGREEMENTS = 'Rental_Agreements' 