import logging
from googleapiclient.discovery import build
from auth.auth import get_gmail_service
from config import LOGGING_CONFIG

# Configure logging from config.py
logging.basicConfig(**LOGGING_CONFIG)

def mark_email_read(email_id):
    creds = get_gmail_service()
    service = build("gmail", "v1", credentials=creds)
    
    service.users().messages().modify(
        userId="me",
        id=email_id,
        body={"removeLabelIds": ["UNREAD"]}
    ).execute()
    logging.info(f"📩 Email {email_id} marked as read.")

def mark_email_unread(email_id):
    creds = get_gmail_service()
    service = build("gmail", "v1", credentials=creds)
    
    service.users().messages().modify(
        userId="me",
        id=email_id,
        body={"addLabelIds": ["UNREAD"]}
    ).execute()
    logging.info(f"📩 Email {email_id} marked as unread.")

def move_email_to_folder(email_id: str, folder_name:str):
    creds = get_gmail_service()
    service = build("gmail", "v1", credentials=creds)
    
    # Get existing labels
    labels = service.users().labels().list(userId="me").execute().get("labels", [])
    
    # Check if the label exists, if not create it
    label_id = None
    for label in labels:
        if label["name"].lower() == folder_name.lower():
            label_id = label["id"]
            break
    
    if not label_id:
        label = service.users().labels().create(
            userId="me",
            body={"name": folder_name, "labelListVisibility": "labelShow", "messageListVisibility": "show"}
        ).execute()
        label_id = label["id"]
        logging.info(f"📂 Folder '{folder_name}' created.")
    
    # Move email to the label (folder)
    service.users().messages().modify(
        userId="me",
        id=email_id,
        body={"addLabelIds": [label_id]}
    ).execute()
    logging.info(f"📩 Email {email_id} moved to '{folder_name}'.")

def remove_inbox_label(email_id: str):
    creds = get_gmail_service()
    service = build("gmail", "v1", credentials=creds)
    
    # Get existing labels
    labels = service.users().labels().list(userId="me").execute().get("labels", [])
    
    # Check if the label exists
    label_id = None
    for label in labels:
        if label["name"].lower() == "inbox":
            label_id = label["id"]
            break
    
    # Remove email to the label (folder)
    service.users().messages().modify(
        userId="me",
        id=email_id,
        body={"removeLabelIds": [label_id]}
    ).execute()
    logging.info(f"📩 Email {email_id} removed from inbox.")

def mark_email_starred(email_id):
    creds = get_gmail_service()
    service = build("gmail", "v1", credentials=creds)

    service.users().messages().modify(
        userId="me",
        id=email_id,
        body={"addLabelIds": ["STARRED"]}
    ).execute()
    logging.info(f"⭐ Email {email_id} marked as starred.")

if __name__ == "__main__":
    test_email_id = "YOUR_EMAIL_ID_HERE"
    mark_email_read(test_email_id)
    mark_email_unread(test_email_id)
    move_email_to_folder(test_email_id, "Important")
