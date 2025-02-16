import os
import pickle
import logging
import google.auth.exceptions
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from config import LOGGING_CONFIG

# Define Gmail API Scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",  # Read emails
    "https://www.googleapis.com/auth/gmail.modify",    # Modify emails (mark read/unread, move labels)
    "https://www.googleapis.com/auth/gmail.labels"     # Manage labels (folders)
]

# Configure logging from config.py
logging.basicConfig(**LOGGING_CONFIG)
logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)

# File paths
TOKEN_FILE = "token.pickle"
CLIENT_SECRET_FILE = "client_secret.json"

def get_gmail_service():
    """Authenticate and return the Gmail API service."""
    creds = None

    # Load saved credentials if available
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    # If credentials are missing or expired, refresh or request new login
    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())  # Refresh token
                logging.info("🔄 Token refreshed successfully.")
            else:
                raise google.auth.exceptions.RefreshError  # Force re-login if refresh fails
        except google.auth.exceptions.RefreshError:
            logging.warning("🔑 Token refresh failed. Re-authenticating via Google OAuth...")
            creds = authenticate_new_user()

    return creds


def authenticate_new_user():
    """Initiate a new authentication flow and save credentials."""
    try:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        creds = flow.run_local_server(port=0)

        # Save new credentials
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)
        logging.info("✅ New credentials saved successfully.")

    except Exception as e:
        logging.error(f"🚨 Authentication failed: {e}")
        return None

    return creds
