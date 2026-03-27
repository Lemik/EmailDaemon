# EmailDaemon Implementation Details

This document contains the detailed implementation specifications for the EmailDaemon project.

## Implemented Table Updates

The following tables have been updated with their respective indexes and constraints:

### Users Table Updates
- Added performance indexes:
  - `idx_users_email` on `email` column
  - `idx_users_type` on `type` column
  - `idx_users_provider` on `provider` and `provider_id` columns
- Implemented timestamp fields with automatic updates
- Added ENUM constraint for user types

### Property Table Updates
- Added performance indexes:
  - `idx_property_landlord` on `landlord_id` column
  - `idx_property_name` on `name` column
- Implemented timestamp fields with automatic updates
- Added foreign key constraint to Users table

### Property_tenant Table Updates
- Added performance indexes:
  - `idx_tenant_property` on `ref_propertyID` column
  - `idx_tenant_landlord` on `ref_landlordID` column
  - `idx_tenant_tenant` on `ref_tenantID` column
  - `idx_tenant_email` on `email` column
- Implemented timestamp fields with automatic updates
- Added foreign key constraints to Property and Users tables

These updates improve:
1. Query performance through strategic indexing
2. Data integrity through foreign key constraints
3. Data tracking through automatic timestamp updates
4. Data consistency through proper constraints

## Database Schema

### Users Table
```sql
CREATE TABLE Users (
    user_id VARCHAR(255) PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255),
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    provider VARCHAR(50),
    provider_id VARCHAR(255),
    provider_pic TEXT,
    token TEXT,
    invitedBy VARCHAR(255),
    type ENUM('1', '2', '3') NOT NULL, -- 1:landlord, 2:tenant, 3:admin
    testAccount BOOLEAN DEFAULT FALSE,
    crdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    ddate TIMESTAMP NULL
);

-- Performance Indexes
CREATE INDEX idx_users_email ON Users(email);
CREATE INDEX idx_users_type ON Users(type);
CREATE INDEX idx_users_provider ON Users(provider, provider_id);
```

### Property Table
```sql
CREATE TABLE Property (
    id_Property INT PRIMARY KEY,
    landlord_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    image TEXT,
    color VARCHAR(7) DEFAULT '#000000',
    personalUse BOOLEAN DEFAULT FALSE,
    crdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    ddate TIMESTAMP NULL,
    FOREIGN KEY (landlord_id) REFERENCES Users(user_id)
);

-- Performance Indexes
CREATE INDEX idx_property_landlord ON Property(landlord_id);
CREATE INDEX idx_property_name ON Property(name);
```

### Property_tenant Table
```sql
CREATE TABLE Property_tenant (
    id_Property_tenant INT PRIMARY KEY,
    ref_propertyID INT NOT NULL,
    unit VARCHAR(50) DEFAULT 'A',
    ref_landlordID INT NOT NULL,
    Fname VARCHAR(255) NOT NULL,
    Lname VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    ref_tenantID INT NOT NULL,
    endTenancy DATE,
    crdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    ddate TIMESTAMP NULL,
    FOREIGN KEY (ref_propertyID) REFERENCES Property(id_Property),
    FOREIGN KEY (ref_landlordID) REFERENCES Users(user_id),
    FOREIGN KEY (ref_tenantID) REFERENCES Users(user_id)
);

-- Performance Indexes
CREATE INDEX idx_tenant_property ON Property_tenant(ref_propertyID);
CREATE INDEX idx_tenant_landlord ON Property_tenant(ref_landlordID);
CREATE INDEX idx_tenant_tenant ON Property_tenant(ref_tenantID);
CREATE INDEX idx_tenant_email ON Property_tenant(email);
```

### Tenancy_Agreement Table
```sql
CREATE TABLE Tenancy_Agreement (
    id_Tenancy_Agreement INT PRIMARY KEY,
    ref_propertyID INT NOT NULL,
    ref_tenantID INT NOT NULL,
    ref_landlordID INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    paymentMethod VARCHAR(50) NOT NULL,
    monthToMonth BOOLEAN DEFAULT TRUE,
    paymentDay INT NOT NULL,
    last_payment_confirmation TIMESTAMP NULL,
    crdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    ddate TIMESTAMP NULL,
    FOREIGN KEY (ref_propertyID) REFERENCES Property(id_Property),
    FOREIGN KEY (ref_tenantID) REFERENCES Users(user_id),
    FOREIGN KEY (ref_landlordID) REFERENCES Users(user_id)
);

-- Performance Indexes
CREATE INDEX idx_agreement_property ON Tenancy_Agreement(ref_propertyID);
CREATE INDEX idx_agreement_tenant ON Tenancy_Agreement(ref_tenantID);
CREATE INDEX idx_agreement_landlord ON Tenancy_Agreement(ref_landlordID);
CREATE INDEX idx_agreement_dates ON Tenancy_Agreement(start_date, end_date);
```

### Rental_Payment_Analysis Table
```sql
CREATE TABLE Rental_Payment_Analysis (
    id_Payment_Analysis INT PRIMARY KEY,
    ref_tenantID INT,
    ref_propertyID INT,
    ref_landlordID INT,
    ref_AgreementId INT,
    month INT,
    year INT,
    expected_amount DECIMAL(10,2),
    actual_amount DECIMAL(10,2),
    payment_status ENUM('on_time', 'late', 'missing', 'incorrect'),
    due_date DATE,
    payment_date DATE,
    payment_method VARCHAR(50),
    confirmation_number VARCHAR(255),
    analysis_details TEXT,
    crdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    ddate TIMESTAMP NULL,
    FOREIGN KEY (ref_tenantID) REFERENCES Users(user_id),
    FOREIGN KEY (ref_propertyID) REFERENCES Property(id_Property),
    FOREIGN KEY (ref_landlordID) REFERENCES Users(user_id),
    FOREIGN KEY (ref_AgreementId) REFERENCES Tenancy_Agreement(id_Tenancy_Agreement)
);

-- Performance Indexes
CREATE INDEX idx_payment_analysis_tenant ON Rental_Payment_Analysis(ref_tenantID);
CREATE INDEX idx_payment_analysis_property ON Rental_Payment_Analysis(ref_propertyID);
CREATE INDEX idx_payment_analysis_date ON Rental_Payment_Analysis(payment_date);
```

### Rental_Payment_History Table
```sql
CREATE TABLE Rental_Payment_History (
    id_Payment_History INT PRIMARY KEY,
    ref_tenantID INT,
    ref_propertyID INT,
    ref_landlordID INT,
    ref_AgreementId INT NULL,  -- Can be NULL if payment is not associated with any agreement
    amount DECIMAL(10,2),
    payment_date DATE,
    payment_method VARCHAR(50),
    confirmation_number VARCHAR(255),
    status ENUM('pending', 'completed', 'failed', 'refunded'),
    note TEXT,
    crdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    ddate TIMESTAMP NULL,
    FOREIGN KEY (ref_tenantID) REFERENCES Property_tenant(id_Property_tenant),
    FOREIGN KEY (ref_propertyID) REFERENCES Property(id_Property),
    FOREIGN KEY (ref_landlordID) REFERENCES Users(user_id),
    FOREIGN KEY (ref_AgreementId) REFERENCES Tenancy_Agreement(id_Tenancy_Agreement)
);

-- Performance Indexes
CREATE INDEX idx_payment_history_tenant ON Rental_Payment_History(ref_tenantID);
CREATE INDEX idx_payment_history_property ON Rental_Payment_History(ref_propertyID);
CREATE INDEX idx_payment_history_date ON Rental_Payment_History(payment_date);
```

### Notification_Preferences Table
```sql
CREATE TABLE Notification_Preferences (
    id_Preference INT PRIMARY KEY,
    ref_userID INT,
    notification_type ENUM('email', 'telegram', 'both'),
    email_address VARCHAR(255),
    telegram_chat_id VARCHAR(255),
    notification_levels INT UNSIGNED,  -- Using INT to store bitmask
    crdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    ddate TIMESTAMP NULL,
    FOREIGN KEY (ref_userID) REFERENCES Users(user_id)
);

CREATE INDEX idx_notification_prefs_user ON Notification_Preferences(ref_userID);
```

### Error_Logs Table
```sql
CREATE TABLE Error_Logs (
    id_Error_Log INT PRIMARY KEY,
    error_type VARCHAR(50),
    error_message TEXT,
    stack_trace TEXT,
    source_module VARCHAR(100),
    severity ENUM('low', 'medium', 'high', 'critical'),
    status ENUM('new', 'in_progress', 'resolved', 'ignored'),
    resolution_notes TEXT,
    assigned_to INT,
    crdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    ddate TIMESTAMP NULL,
    FOREIGN KEY (assigned_to) REFERENCES Users(user_id)
);

-- Performance Indexes
CREATE INDEX idx_error_logs_type ON Error_Logs(error_type);
CREATE INDEX idx_error_logs_status ON Error_Logs(status);
CREATE INDEX idx_error_logs_severity ON Error_Logs(severity);
```

Note: Payment discrepancy tracking functionality can be added later when needed. This will include:
- Tracking payment amount mismatches
- Monitoring late payments
- Recording payment method issues
- Managing resolution of payment discrepancies

### Rental_Payment_Notifications Table
```sql
CREATE TABLE Rental_Payment_Notifications (
    id_Notification INT PRIMARY KEY,
    ref_userID INT,
    ref_payment_id INT,
    notification_type ENUM('late_payment', 'discrepancy', 'summary', 'other'),
    notification_status ENUM('pending', 'sent', 'failed'),
    notification_channel ENUM('email', 'telegram', 'both'),
    message_content TEXT,
    sent_at TIMESTAMP NULL,
    crdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    ddate TIMESTAMP NULL,
    FOREIGN KEY (ref_userID) REFERENCES Users(user_id),
    FOREIGN KEY (ref_payment_id) REFERENCES Rental_Payment_History(id_Payment_History)
);

-- Performance Indexes
CREATE INDEX idx_notifications_user ON Rental_Payment_Notifications(ref_userID);
CREATE INDEX idx_notifications_payment ON Rental_Payment_Notifications(ref_payment_id);
CREATE INDEX idx_notifications_status ON Rental_Payment_Notifications(notification_status);
```

### Rental_Payment_Audit_Log Table
```sql
CREATE TABLE Rental_Payment_Audit_Log (
    id_Audit_Log INT PRIMARY KEY,
    ref_payment_id INT,
    action_type ENUM('create', 'update', 'delete', 'verify', 'analyze'),
    action_by INT,
    action_details TEXT,
    previous_state TEXT,
    new_state TEXT,
    crdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ref_payment_id) REFERENCES Rental_Payment_History(id_Payment_History),
    FOREIGN KEY (action_by) REFERENCES Users(user_id)
);

-- Performance Indexes
CREATE INDEX idx_audit_payment ON Rental_Payment_Audit_Log(ref_payment_id);
CREATE INDEX idx_audit_date ON Rental_Payment_Audit_Log(crdate);
```

## Data Structures

### Email Payment Data Structure
The system processes email payment data with the following structure from `Rental_Payments_Log`:

```sql
UPDATE `llHub`.`Rental_Payments_Log`
SET
    `id` = <{id: }>,
    `sender_name` = <{sender_name: }>,
    `sender_email` = <{sender_email: }>,
    `send_date` = <{send_date: }>,
    `send_amount` = <{send_amount: }>,
    `currency` = <{currency: }>,
    `sender_message` = <{sender_message: }>,
    `reference_number` = <{reference_number: }>,
    `recipient_name` = <{recipient_name: }>,
    `recipient_email` = <{recipient_email: }>,
    `status_message` = <{status_message: }>,
    `recipient_bank_name` = <{recipient_bank_name: }>,
    `recipient_account_ending` = <{recipient_account_ending: }>,
    `view_in_browser_link` = <{view_in_browser_link: }>,
    `created_at` = <{created_at: CURRENT_TIMESTAMP}>,
    `updated_at` = <{updated_at: CURRENT_TIMESTAMP}>,
    `deleted_at` = <{deleted_at: }>
WHERE `id` = <{expr}>;
```

This structure provides the following key information for payment analysis:
- Sender details (name, email)
- Payment details (amount, currency, date)
- Reference information (reference number, sender message)
- Recipient details (name, email, bank information)
- Status tracking (status message, timestamps)
- Audit trail (created_at, updated_at, deleted_at)

The data from this table will be used for:
1. Payment verification against tenant agreements
2. Payment status tracking
3. Discrepancy detection
4. Historical payment analysis
5. Audit trail maintenance

## Data Access Layer Implementation

### PaymentDataAccess Class
```python
class PaymentDataAccess:
    def get_tenant_agreements(self, tenant_id: str) -> List[Dict]:
        """Retrieve active agreements for a tenant"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT * FROM Rental_Agreements 
                WHERE ref_tenantID = %s 
                AND ddate IS NULL
                AND end_date >= CURDATE()
            """
            cursor.execute(query, (tenant_id,))
            return cursor.fetchall()
        except Exception as e:
            raise DataAccessError(f"Failed to get tenant agreements: {str(e)}")

    def get_historical_payments(self, tenant_id: str, 
                              start_date: datetime, 
                              end_date: datetime) -> List[Dict]:
        """Retrieve payment history for analysis"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT * FROM Rental_Payment_History
                WHERE ref_tenantID = %s 
                AND payment_date BETWEEN %s AND %s
                AND ddate IS NULL
            """
            cursor.execute(query, (tenant_id, start_date, end_date))
            return cursor.fetchall()
        except Exception as e:
            raise DataAccessError(f"Failed to get historical payments: {str(e)}")

    def get_property_payments(self, property_id: str, 
                            month: int, year: int) -> List[Dict]:
        """Retrieve all payments for a specific property"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT * FROM Rental_Payment_History
                WHERE ref_propertyID = %s 
                AND MONTH(payment_date) = %s 
                AND YEAR(payment_date) = %s
                AND ddate IS NULL
            """
            cursor.execute(query, (property_id, month, year))
            return cursor.fetchall()
        except Exception as e:
            raise DataAccessError(f"Failed to get property payments: {str(e)}")
```

### PaymentDataCache Class
```python
class PaymentDataCache:
    def __init__(self):
        self._cache = {}
        self._ttl = 3600  # 1 hour
        
    def get_cached_data(self, key: str) -> Optional[Dict]:
        """Retrieve cached data if valid"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if datetime.now().timestamp() - timestamp < self._ttl:
                return data
            del self._cache[key]
        return None
        
    def set_cached_data(self, key: str, data: Dict):
        """Cache data with timestamp"""
        self._cache[key] = (data, datetime.now().timestamp())
        
    def clear_cache(self):
        """Clear all cached data"""
        self._cache.clear()
```

### PaymentDataValidator Class
```python
class PaymentDataValidator:
    def validate_payment_data(self, payment_data: Dict) -> bool:
        """Validate payment data structure and values"""
        required_fields = ['amount', 'payment_date', 'payment_method', 
                         'confirmation_number']
        
        # Check required fields
        if not all(field in payment_data for field in required_fields):
            return False
            
        # Validate amount
        if not isinstance(payment_data['amount'], (int, float)) or payment_data['amount'] <= 0:
            return False
            
        # Validate date
        if not isinstance(payment_data['payment_date'], datetime):
            return False
            
        # Validate confirmation number
        if not isinstance(payment_data['confirmation_number'], str):
            return False
            
        return True
        
    def validate_agreement_data(self, agreement_data: Dict) -> bool:
        """Validate agreement data structure and values"""
        required_fields = ['monthly_rent', 'start_date', 'end_date', 
                         'ref_tenantID', 'ref_propertyID']
        
        # Check required fields
        if not all(field in agreement_data for field in required_fields):
            return False
            
        # Validate rent amount
        if not isinstance(agreement_data['monthly_rent'], (int, float)) or agreement_data['monthly_rent'] <= 0:
            return False
            
        # Validate dates
        if not isinstance(agreement_data['start_date'], datetime) or \
           not isinstance(agreement_data['end_date'], datetime):
            return False
            
        # Validate date range
        if agreement_data['start_date'] >= agreement_data['end_date']:
            return False
            
        return True
```

## Notification System Implementation

### NotificationTemplates Class
```python
class NotificationTemplates:
    @staticmethod
    def late_payment_email(tenant_name: str, amount: float, due_date: datetime) -> str:
        return f"""
        Dear {tenant_name},
        
        This is a reminder that your rent payment of ${amount:.2f} was due on {due_date.strftime('%Y-%m-%d')}.
        Please process your payment as soon as possible.
        
        Best regards,
        Property Management
        """
        
    @staticmethod
    def payment_discrepancy_email(tenant_name: str, expected: float, actual: float) -> str:
        return f"""
        Dear {tenant_name},
        
        We noticed a discrepancy in your recent rent payment.
        Expected amount: ${expected:.2f}
        Received amount: ${actual:.2f}
        
        Please contact us to resolve this matter.
        
        Best regards,
        Property Management
        """
```

### NotificationManager Class
```python
class NotificationManager:
    def __init__(self):
        self.email_notifier = EmailNotifier()
        self.telegram_notifier = TelegramNotifier()
        self.preferences = NotificationPreferences()
        
    def send_notification(self, user_id: str, notification_type: str, 
                        template_data: Dict):
        """Send notification based on user preferences"""
        prefs = self.preferences.get_user_preferences(user_id)
        
        if prefs['notification_type'] in ['email', 'both']:
            self.email_notifier.send(
                prefs['email_address'],
                self._get_template(notification_type, template_data)
            )
            
        if prefs['notification_type'] in ['telegram', 'both']:
            self.telegram_notifier.send(
                prefs['telegram_chat_id'],
                self._get_template(notification_type, template_data)
            )
```

## Error Tracking Implementation

### ErrorTrackingManager Class
```python
class ErrorTrackingManager:
    def __init__(self):
        self.db = DatabaseConnection()
        
    def log_error(self, error_type: str, error_message: str, 
                 stack_trace: str, source_module: str, 
                 severity: str = 'medium'):
        """Log a new error"""
        try:
            cursor = self.db.cursor()
            query = """
                INSERT INTO Error_Logs (
                    id_Error_Log, error_type, error_message, 
                    stack_trace, source_module, severity, status
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, 'new'
                )
            """
            error_id = f"ERR_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            cursor.execute(query, (
                error_id, error_type, error_message, 
                stack_trace, source_module, severity
            ))
            self.db.commit()
            
            # Update statistics
            self._update_error_statistics(error_type)
            
        except Exception as e:
            logging.error(f"Failed to log error: {str(e)}")
            
    def update_error_status(self, error_id: str, status: str, 
                          resolution_notes: str = None):
        """Update error status and resolution notes"""
        try:
            cursor = self.db.cursor()
            query = """
                UPDATE Error_Logs 
                SET status = %s, resolution_notes = %s
                WHERE id_Error_Log = %s
            """
            cursor.execute(query, (status, resolution_notes, error_id))
            self.db.commit()
            
        except Exception as e:
            logging.error(f"Failed to update error status: {str(e)}")
```

## Configuration Implementation

### Settings Class
```python
class Settings:
    # Database settings
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'email_daemon')
    
    # Application settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Cache settings
    CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))
    CACHE_MAX_SIZE = int(os.getenv('CACHE_MAX_SIZE', 1000))
    
    @classmethod
    def get_all_settings(cls) -> Dict[str, Any]:
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_')
        }
```

## Test Implementation

### Test Structure
```
tests/
├── __init__.py
├── conftest.py
├── unit/
│   ├── __init__.py
│   ├── test_data_access.py
│   ├── test_payment_analyzer.py
│   └── test_notification_manager.py
├── integration/
│   ├── __init__.py
│   ├── test_payment_processing.py
│   └── test_error_tracking.py
└── performance/
    ├── __init__.py
    └── test_system_performance.py
```