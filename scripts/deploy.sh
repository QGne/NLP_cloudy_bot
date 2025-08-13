#!/bin/bash

set -e  # Exit on any error

echo "🚀 Deploying ChatBot SaaS Prototype..."
echo "====================================="

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Step 1: Package Lambda function
echo "📦 Packaging Lambda function..."
cd backend/lambdas
zip -r ../../terraform/chat_handler.zip . -x "*.pyc" "*__pycache__*"
cd ../../

# Step 2: Deploy infrastructure with Terraform
echo "🏗️  Deploying infrastructure..."
cd terraform

terraform init
terraform validate
terraform plan -out=tfplan
terraform apply tfplan

# Get outputs
API_GATEWAY_URL=$(terraform output -raw api_gateway_url)
LAMBDA_FUNCTION_NAME=$(terraform output -raw lambda_function_name)

echo "✅ Infrastructure deployed successfully!"
echo "📊 Deployment Information:"
echo "   API Gateway URL: $API_GATEWAY_URL"
echo "   Lambda Function: $LAMBDA_FUNCTION_NAME"

cd ..

# Step 3: Update CLI configuration
echo "⚙️  Updating CLI configuration..."
sed -i.bak "s|https://your-api-id.execute-api.us-east-1.amazonaws.com/prod|$API_GATEWAY_URL|g" cli/config.py

# Step 4: Wait for SageMaker endpoint to be ready
echo "⏳ Waiting for SageMaker endpoint to be ready..."
ENDPOINT_NAME=$(cd terraform && terraform output -raw sagemaker_endpoint_name)

while true; do
    STATUS=$(aws sagemaker describe-endpoint --endpoint-name $ENDPOINT_NAME --query 'EndpointStatus' --output text)
    echo "   Endpoint status: $STATUS"
    
    if [ "$STATUS" = "InService" ]; then
        break
    elif [ "$STATUS" = "Failed" ]; then
        echo "❌ SageMaker endpoint deployment failed"
        exit 1
    fi
    
    sleep 30
done

echo "✅ SageMaker endpoint is ready!"

# Step 5: Warm up SageMaker via Lambda to avoid cold-start timeouts
echo "🔥 Warming up endpoint via Lambda..."
WARMUP_PAYLOAD='{"message":"warmup","session_id":"warmup"}'
aws lambda invoke \
  --function-name "$LAMBDA_FUNCTION_NAME" \
  --payload "$WARMUP_PAYLOAD" \
  --cli-binary-format raw-in-base64-out \
  warmup_response.json >/dev/null 2>&1 || true
cat warmup_response.json || true
rm -f warmup_response.json || true

# Step 6: Test deployment
echo "🧪 Testing deployment..."
cd cli
python3 chatbot_cli.py --test-mode

if [ $? -eq 0 ]; then
    echo "✅ Deployment test passed!"
    echo ""
    echo "🎉 Deployment Complete!"
    echo "======================================"
    echo "To use the CLI: cd cli && python3 chatbot_cli.py"
    echo "API Gateway URL: $API_GATEWAY_URL"
else
    echo "❌ Deployment test failed!"
    exit 1
fi