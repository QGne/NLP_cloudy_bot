"""
Configuration settings for ChatBot CLI
"""

import os

# API Gateway URL (will be set after deployment)
API_GATEWAY_URL = os.environ.get(
    'API_GATEWAY_URL', 
    'https://your-api-id.execute-api.us-east-1.amazonaws.com/prod'
)

# Request timeout in seconds
TIMEOUT = 30

# CLI settings
MAX_MESSAGE_LENGTH = 1000
RETRY_ATTEMPTS = 3