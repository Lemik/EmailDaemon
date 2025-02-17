from aifc import Error
import unittest
from unittest.mock import patch, MagicMock
from db.mySql_db_manipulations import connect_to_db, insert_email_data


class TestDB(unittest.TestCase):

    @patch("mysql.connector.connect")
    def test_connenction_to_db_successful(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection 

        connection = connect_to_db()
        self.assertIsNotNone(connection)
        mock_connect.assert_called_once()
        print("✅ test_connect_to_db_success passed! ")

    @patch("mysql.connector.connect")
    def test_connection_to_db_failed(self, mock_connect):
        """Test database connection failure."""
        mock_connect.side_effect = Exception("Database connection failed!")  

        try:
            with self.assertLogs(level="ERROR") as log:  
                connection = connect_to_db()
                print(f"after connection : {log}")
                self.assertIsNone(connection) 
        except Error as e:
            print(f"Except: {e}")

        self.assertIn("❌ Error connecting to MySQL:", log.output[0]) 
        print("✅ test_connection_to_db_failed passed!")


    @patch("mysql.connector.connect")
    def test_insert_email_data_success(self, mock_connect):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()

        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        insert_email_data(
            id="12345",
            sender_name="John Doe",
            send_date="2025-01-01 14:49:00",
            send_amount=2600.00,
            currency="CAD",
            sender_message="January Rent",
            reference_number="C1A4fAtTkYRv",
            recipient_name="Jane Smith",
            recipient_email="jane@example.com",
            status_message="Completed",
            recipient_bank_name="RBC Royal Bank",
            recipient_account_ending="7686",
            view_in_browser_link="https://etransfer.ca/verify"
        )
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
        print("✅ test_insert_email_data_success passed!")

    @patch("mysql.connector.connect")
    def test_insert_email_data_failure(self, mock_connect):
        """Test insertion failure due to database error."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        
        # Simulate an error when executing query
        mock_cursor.execute.side_effect = Exception("Database insert failed!")
        
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        with self.assertLogs(level="ERROR"):
            insert_email_data(
                id="12345",
                sender_name="John Doe",
                send_date="2025-01-01 14:49:00",
                send_amount=2600.00,
                currency="CAD",
                sender_message="January Rent",
                reference_number="C1A4fAtTkYRv",
                recipient_name="Jane Smith",
                recipient_email="jane@example.com",
                status_message="Completed",
                recipient_bank_name="RBC Royal Bank",
                recipient_account_ending="7686",
                view_in_browser_link="https://etransfer.ca/verify"
            )

        print("✅ test_insert_email_data_failure passed!")


if __name__ == "__main__":
    unittest.main()