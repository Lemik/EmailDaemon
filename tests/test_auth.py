import os
import unittest
import pickle
import google.auth.exceptions 
from unittest.mock import patch, MagicMock
from auth.auth import get_gmail_service, authenticate_new_user

# Paths for testing
TEST_TOKEN_FILE = "test_token.pickle"

class TestAuth(unittest.TestCase):

    @patch("auth.auth.os.path.exists", return_value=True)
    @patch("auth.auth.pickle.load")
    def test_load_existing_credentials(self, mock_pickle_load, mock_os_path_exists):
        """Test loading existing credentials from token.pickle"""
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_pickle_load.return_value = mock_creds

        creds = get_gmail_service()
        self.assertIsNotNone(creds)
        self.assertTrue(creds.valid)

    @patch("auth.auth.os.path.exists", return_value=False)
    @patch("auth.auth.authenticate_new_user")
    def test_authenticate_when_no_token(self, mock_authenticate, mock_os_path_exists):
        """Test authentication is triggered when token is missing"""
        mock_authenticate.return_value = MagicMock()
        creds = get_gmail_service()
        self.assertIsNotNone(creds)
        mock_authenticate.assert_called_once()

    @patch("auth.auth.pickle.load")
    @patch("auth.auth.os.path.exists", return_value=True)
    @patch("auth.auth.google.auth.transport.requests.Request")
    def test_refresh_token_if_expired(self, mock_request, mock_os_path_exists, mock_pickle_load):
        """Test token refresh logic"""
        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = "dummy_refresh_token"

        mock_pickle_load.return_value = mock_creds

        creds = get_gmail_service()
        self.assertTrue(mock_creds.refresh.called)

    @patch("auth.auth.authenticate_new_user")  # Ensure this is patched
    @patch("auth.auth.pickle.load")
    @patch("auth.auth.os.path.exists", return_value=True)
    @patch("auth.auth.google.auth.transport.requests.Request")
    def test_refresh_token_failure(self, mock_request, mock_os_path_exists, mock_pickle_load, mock_authenticate):
        """Test that authentication is retried if token refresh fails"""
        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = "dummy_refresh_token"
        mock_creds.refresh.side_effect = google.auth.exceptions.RefreshError("Refresh Failed")  # Simulate failure

        mock_pickle_load.return_value = mock_creds

        get_gmail_service()
        mock_authenticate.assert_called_once()  # Ensure re-authentication is triggered


    @patch("auth.auth.pickle.dump")
    @patch("auth.auth.InstalledAppFlow.from_client_secrets_file")
    def test_authenticate_new_user_success(self, mock_flow, mock_pickle_dump):
        """Test successful authentication and saving credentials"""
        mock_creds = MagicMock()
        mock_flow.return_value.run_local_server.return_value = mock_creds

        creds = authenticate_new_user()
        self.assertIsNotNone(creds)
        mock_pickle_dump.assert_called_once()

if __name__ == "__main__":
    unittest.main()
