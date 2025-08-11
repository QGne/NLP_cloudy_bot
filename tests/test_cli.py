import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add CLI directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'cli'))

from chatbot_cli import ChatBotCLI

class TestChatBotCLI(unittest.TestCase):
    
    def setUp(self):
        self.cli = ChatBotCLI()
    
    def test_cli_initialization(self):
        """Test CLI initializes correctly"""
        self.assertIsNotNone(self.cli.session_id)
        self.assertIsNotNone(self.cli.api_url)
    
    @patch('requests.post')
    def test_send_message_success(self, mock_post):
        """Test successful message sending"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'response': 'Hello there!'}
        mock_post.return_value = mock_response
        
        response = self.cli.send_message("Hello")
        self.assertEqual(response, "Hello there!")
    
    @patch('requests.post')
    def test_send_message_error(self, mock_post):
        """Test message sending with error"""
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        response = self.cli.send_message("Hello")
        self.assertIn("Error: 500", response)
    
    @patch('requests.post')
    def test_send_message_timeout(self, mock_post):
        """Test message sending with timeout"""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()
        
        response = self.cli.send_message("Hello")
        self.assertIn("timed out", response)

if __name__ == '__main__':
    unittest.main()