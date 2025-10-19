# EmailDaemon Project Structure

## Overview
EmailDaemon is a Python application that monitors email payments, analyzes payment patterns, and sends notifications. The project follows a modular architecture with clear separation of concerns.

## Directory Structure

```
EmailDaemon/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration management
│   │   ├── constants.py       # Application constants and enums
│   │   └── exceptions.py      # Custom exception classes
│   │
│   ├── email/
│   │   ├── __init__.py
│   │   ├── fetcher.py         # Email fetching functionality
│   │   ├── parser.py          # Email content parsing
│   │   └── processor.py       # Email processing logic
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   └── access/
│   │       ├── __init__.py
│   │       ├── payment_access.py    # Payment data access
│   │       ├── agreement_access.py  # Agreement data access
│   │       └── cache.py             # Data caching
│   │
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── payment_analyzer.py      # Payment analysis
│   │   ├── historical_analyzer.py   # Historical trend analysis
│   │   └── pattern_recognizer.py    # Pattern recognition
│   │
│   └── notifications/
│       ├── __init__.py
│       ├── notification_manager.py  # Notification orchestration
│       ├── email_notifier.py        # Email notifications
│       ├── telegram_notifier.py     # Telegram notifications
│       └── preferences.py           # Notification preferences
│
├── tests/                      # Test directory
│   ├── __init__.py
│   ├── test_email_fetcher.py
│   ├── test_payment_analyzer.py
│   └── ...
│
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
└── MAP.md                      # This file
```

## Module Descriptions

### Core Module
- `config.py`: Manages application configuration using environment variables
- `constants.py`: Defines application-wide constants and enums
- `exceptions.py`: Custom exception classes for error handling

### Email Module
- `fetcher.py`: Handles email fetching using IMAP
- `parser.py`: Parses email content to extract payment information
- `processor.py`: Processes emails and coordinates with other modules

### Data Access Module
- `payment_access.py`: Database operations for payment records
- `agreement_access.py`: Database operations for rental agreements
- `cache.py`: Implements data caching for performance optimization

### Analysis Module
- `payment_analyzer.py`: Analyzes payment timeliness and amounts
- `historical_analyzer.py`: Analyzes historical payment trends
- `pattern_recognizer.py`: Identifies payment patterns and anomalies

### Notifications Module
- `notification_manager.py`: Manages notification delivery
- `email_notifier.py`: Sends email notifications
- `telegram_notifier.py`: Sends Telegram notifications
- `preferences.py`: Manages user notification preferences

## Key Features
1. Email Monitoring
   - Automated email fetching
   - Payment information extraction
   - Payment processing

2. Payment Analysis
   - Timeliness analysis
   - Amount verification
   - Pattern recognition
   - Historical trend analysis

3. Notifications
   - Multi-channel support (Email, Telegram)
   - Customizable notification preferences
   - Bulk notification handling

4. Data Management
   - Efficient database access
   - Caching for performance
   - Error handling and logging

## Dependencies
- Python 3.8+
- mysql-connector-python
- python-telegram-bot
- python-dotenv
- requests
- imaplib (standard library)
- smtplib (standard library) 