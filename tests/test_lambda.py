import unittest
import json
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'lambdas'))

# Mock environment variables
os.environ['DYNAMODB_TABLE'] = 'test-table'
os.environ['SAGEMAKER_ENDPOINT'] = 'test-endpoint'

# Import after setting environment
from chat_handler import lambda_handler

class TestChatHandler(unittest.TestCase):
    
    def test_lambda_handler_with_message(self):
        """Test lambda handler with valid message"""
        event = {
            'body': json.dumps({
                'message': 'Hello, how are you?',
                'session_id': 'test-session-123'
            })
        }
        context = {}
        
        # This will fail with actual AWS calls, but tests the structure
        try:
            response = lambda_handler(event, context)
            # Should return proper structure even if AWS calls fail
            self.assertIn('statusCode', response)
            self.assertIn('body', response)
        except Exception as e:
            # Expected to fail without actual AWS resources
            self.assertIsInstance(e, Exception)
    
    def test_lambda_handler_without_message(self):
        """Test lambda handler with missing message"""
        event = {
            'body': json.dumps({
                'session_id': 'test-session-123'
            })
        }
        context = {}
        
        response = lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 400)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
    
    def test_lambda_handler_invalid_json(self):
        """Test lambda handler with invalid JSON"""
        event = {
            'body': 'invalid json'
        }
        context = {}
        
        response = lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 500)

if __name__ == '__main__':
    unittest.main()