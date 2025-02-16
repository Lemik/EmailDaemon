import logging

# Number of emails to fetch from Gmail
NUM_EMAILS_TO_FETCH = 10

# Logging configuration as a dictionary
LOGGING_CONFIG = {
    "level": logging.INFO,
    "format": "%(asctime)s - %(levelname)s - %(message)s",
}

# AWS MySQL Database Configuration
DB_CONFIG = {
    "host": "your-aws-endpoint",  # e.g., "database-1.xxxxxxx.us-east-1.rds.amazonaws.com"
    "user": "your-username",
    "password": "your-password",
    "database": "your-database-name",
    "port": 3306,  # Default MySQL port
}