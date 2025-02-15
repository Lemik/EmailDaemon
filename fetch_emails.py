from googleapiclient.discovery import build
from auth import get_gmail_service

def fetch_emails():
    """Fetch recent emails from Gmail and return raw email data."""
    creds = get_gmail_service()
    service = build("gmail", "v1", credentials=creds)

    # Fetch the latest 10 messages
    results = service.users().messages().list(userId="me", maxResults=10).execute()
    messages = results.get("messages", [])

    if not messages:
        print("No new emails found.")
        return []

    email_data = []
    for msg in messages:
        msg_id = msg["id"]
        email = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
        email_data.append(email)

    return email_data






