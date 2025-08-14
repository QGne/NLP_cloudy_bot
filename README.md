# NLP_cloudy_bot

## Project Structure

```
NLP_cloudy_bot/
├── terraform/              # Infrastructure as Code
│   ├── main.tf             # Main Terraform configuration
│   ├── lambda.tf           # Lambda & API Gateway resources
│   ├── sagemaker.tf        # SageMaker model & endpoint
│   ├── dynamodb.tf         # Database configuration
│   └── variables.tf        # Configuration variables
├── backend/lambdas/         # Lambda function code
│   ├── chat_handler.py     # Main Lambda handler
│   └── requirements.txt    # Python dependencies
├── cli/                     # Command-line interface
│   ├── chatbot_cli.py      # Interactive CLI
│   ├── config.py           # CLI configuration
│   └── requirements.txt    # CLI dependencies
├── scripts/                 # Deployment automation
│   ├── deploy.sh           # Full deployment script
│   ├── cleanup.sh          # Resource cleanup
│   └── test_cli.sh         # CLI testing
├── tests/                   # Unit tests
└── .github/workflows/       # CI/CD pipelines
```

## Quick Start

### 1. Clone and Setup
```bash
# Clone the repository
git clone <https://github.com/QGne/NLP_cloudy_bot.git>
cd NLP_cloudy_bot

# Verify prerequisites
aws sts get-caller-identity  # Should return your AWS account info
terraform --version          # Should show v1.5+
python3 --version           # Should show v3.9+
```


### 2. Configure AWS Credentials
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key  
# Enter your default region (e.g., us-east-1)
# Enter output format (json)
```

### 3. Deploy the Application
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Deploy everything
./scripts/deploy.sh
```

### 4. Use the ChatBot
```bash
cd cli
python3 chatbot_cli.py
```

### Example Conversation:
```bash
🤖 ChatBot SaaS Prototype
========================================
Type 'exit' to quit, 'help' for commands
Session ID: a1b2c3d4...

> Hello, how are you today?
🤔 Thinking...
🤖 Bot: I'm doing well, thank you for asking! How can I help you today?

> What's the weather like?
🤔 Thinking...
🤖 Bot: I don't have access to real-time weather data, but I'd be happy to chat about other topics!

> exit
Goodbye! 👋
```

### 5. Run All Tests
```bash
# Install test dependencies
pip install pytest

# Run unit tests
python -m pytest tests/ -v

# Test CLI functionality
cd cli && python3 chatbot_cli.py --test-mode

# Test API directly
curl -X POST "https://your-api-url/prod/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","session_id":"test-123"}'
```


### 6. Cleanup
```bash
# Automated cleanup
./scripts/cleanup.sh

# Manual cleanup
cd terraform
terraform destroy
```

### 7. Quick Deploy
```bash
git clone <https://github.com/QGne/NLP_cloudy_bot.git> && cd NLP_cloudy_bot && ./scripts/deploy.sh
```
