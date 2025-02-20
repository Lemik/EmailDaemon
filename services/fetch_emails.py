from googleapiclient.discovery import build
from auth.auth import get_gmail_service
from config import NUM_EMAILS_TO_FETCH

def fetch_emails():
    creds = get_gmail_service()
    service = build("gmail", "v1", credentials=creds)

    # Use Gmail's search query to fetch only unread messages
    query = "is:unread -is:starred"

    # Fetch the latest NUM_EMAILS_TO_FETCH messages
    results = service.users().messages().list(userId="me", maxResults=NUM_EMAILS_TO_FETCH, q=query).execute()
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






