import requests
from typing import Dict, Any
from ..core.config import Config
from ..core.exceptions import NotificationError

class TelegramNotifier:
    def __init__(self):
        self.config = Config()
        self.bot_token = self.config.get('TELEGRAM_BOT_TOKEN')
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send(self, chat_id: str, message: str, data: Dict[str, Any] = None) -> None:
        """
        Send a Telegram notification.
        
        Args:
            chat_id: Telegram chat ID
            message: Message to send
            data: Additional data to include in the message
        """
        try:
            # Prepare message
            full_message = message
            if data:
                full_message += "\n\nAdditional Information:\n"
                for key, value in data.items():
                    full_message += f"{key}: {value}\n"

            # Send message
            response = requests.post(
                f"{self.api_url}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": full_message,
                    "parse_mode": "HTML"
                }
            )
            response.raise_for_status()
        except Exception as e:
            raise NotificationError(f"Failed to send Telegram notification: {str(e)}")

    def send_with_keyboard(self, chat_id: str, message: str, keyboard: list, data: Dict[str, Any] = None) -> None:
        """
        Send a Telegram notification with a custom keyboard.
        
        Args:
            chat_id: Telegram chat ID
            message: Message to send
            keyboard: List of keyboard buttons
            data: Additional data to include in the message
        """
        try:
            # Prepare message
            full_message = message
            if data:
                full_message += "\n\nAdditional Information:\n"
                for key, value in data.items():
                    full_message += f"{key}: {value}\n"

            # Send message with keyboard
            response = requests.post(
                f"{self.api_url}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": full_message,
                    "parse_mode": "HTML",
                    "reply_markup": {
                        "keyboard": keyboard,
                        "resize_keyboard": True,
                        "one_time_keyboard": True
                    }
                }
            )
            response.raise_for_status()
        except Exception as e:
            raise NotificationError(f"Failed to send Telegram notification with keyboard: {str(e)}") 