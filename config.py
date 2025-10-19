import logging

# Number of emails to fetch from Gmail
NUM_EMAILS_TO_FETCH = 10


# Logging configuration as a dictionary
LOGGING_CONFIG = {
    "level": logging.INFO,
    "format": "%(asctime)s - %(levelname)s - %(message)s",
}

# AWS MySQL Database Configuration
PROD_DB_CONFIG = {
    "host": "aws-db1-llhub.cvp7hosorzpj.us-west-2.rds.amazonaws.com",  # e.g., "database-1.xxxxxxx.us-east-1.rds.amazonaws.com"
    "user": "admin",
    "password": "mFZ3P#h3#XCC!uLmedwi",
    "database": "TEST",
    "port": 3306,  # Default MySQL port
}

# Test Database Configuration
TEST_DB_CONFIG = {
    "host": "localhost",
    "user": "llhub",
    "password": "llhub",
    "database": "llhub",
    "port": 3306,
}

DEBUG = True