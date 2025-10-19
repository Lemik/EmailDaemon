import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
from ..core.config import Config
from ..core.exceptions import NotificationError

class EmailNotifier:
    def __init__(self):
        self.config = Config()
        self.smtp_server = self.config.get('SMTP_SERVER')
        self.smtp_port = self.config.get('SMTP_PORT')
        self.smtp_username = self.config.get('SMTP_USERNAME')
        self.smtp_password = self.config.get('SMTP_PASSWORD')
        self.sender_email = self.config.get('SENDER_EMAIL')

    def send(self, to: str, subject: str, message: str, data: Dict[str, Any] = None) -> None:
        """
        Send an email notification.
        
        Args:
            to: Recipient email address
            subject: Email subject
            message: Email message
            data: Additional data to include in the email
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to
            msg['Subject'] = subject

            # Prepare email body
            body = message
            if data:
                body += "\n\nAdditional Information:\n"
                for key, value in data.items():
                    body += f"{key}: {value}\n"

            msg.attach(MIMEText(body, 'plain'))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
        except Exception as e:
            raise NotificationError(f"Failed to send email notification: {str(e)}")

    def send_html(self, to: str, subject: str, html_content: str, data: Dict[str, Any] = None) -> None:
        """
        Send an HTML email notification.
        
        Args:
            to: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            data: Additional data to include in the email
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = to
            msg['Subject'] = subject

            # Attach HTML content
            msg.attach(MIMEText(html_content, 'html'))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
        except Exception as e:
            raise NotificationError(f"Failed to send HTML email notification: {str(e)}") 