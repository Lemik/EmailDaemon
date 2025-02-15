from fetch_emails import fetch_emails
from parse_emails import parse_email

if __name__ == "__main__":
    emails = fetch_emails()
    for email in emails:
        parsed_data = parse_email(email)
        print(f"\n ID: {parsed_data['msg_id']}")
        print(f"📩 Email from: {parsed_data['Sender']}")
        print(f"📜 Subject: {parsed_data['Subject']}")
        print("📊 Extracted Transaction Details:")
        for key, value in parsed_data['Email_details'].items():
            print(f"{key}: {value}")
        print("🔗 E-Transfer Links:")
        if parsed_data["E-Transfer Links"]:
                print(f'   {parsed_data["E-Transfer Links"][0]}')
        else:
            print("   No e-transfer links found.")
        print("---\n")