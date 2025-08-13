import json
import boto3
import os
import time
import uuid
from decimal import Decimal

# Initialize AWS clients
aws_region = os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION') or 'us-east-1'
dynamodb = boto3.resource('dynamodb', region_name=aws_region)
sagemaker_runtime = boto3.client('sagemaker-runtime', region_name=aws_region)

# Environment variables
DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']
SAGEMAKER_ENDPOINT = os.environ['SAGEMAKER_ENDPOINT']

def lambda_handler(event, context):
    """
    Main Lambda handler for chat processing
    """
    try:
        # Parse request body
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event  # For direct invocation
        
        message = body.get('message', '').strip()
        session_id = body.get('session_id', str(uuid.uuid4()))
        
        # Validate required inputs for chat
        if not message:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'Message is required. Provide field "message".'})
            }
        
        # Generate AI response
        ai_response = get_ai_response(message)
        
        # Store conversation in DynamoDB
        store_conversation(session_id, message, ai_response)
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'response': ai_response,
                'session_id': session_id,
                'timestamp': int(time.time())
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }

def get_ai_response(message):
    """
    Get response from SageMaker endpoint using Hugging Face text-generation pipeline
    """
    try:
        # Prepare payload for HuggingFace text-generation model
        payload = {
            "inputs": message
        }
        
        # Call SageMaker endpoint
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=SAGEMAKER_ENDPOINT,
            ContentType='application/json',
            Body=json.dumps(payload)
        )
        
        # Parse response
        result = json.loads(response['Body'].read().decode())
        
        # HF text-generation typically returns a list of dicts with 'generated_text'
        if isinstance(result, dict):
            answer = result.get('generated_text') or result.get('answer') or ''
        elif isinstance(result, list) and len(result) > 0:
            first = result[0]
            if isinstance(first, dict):
                answer = first.get('generated_text') or first.get('answer') or ''
            else:
                answer = str(first)
        else:
            answer = ''
        
        return answer if answer else "I'm sorry, I don't have a response right now."
        
    except Exception as e:
        print(f"SageMaker error: {str(e)}")
        # Fallback response
        return "I'm experiencing some technical difficulties. Please try again in a moment."

def store_conversation(session_id, user_message, bot_response):
    """
    Store conversation in DynamoDB
    """
    try:
        table = dynamodb.Table(DYNAMODB_TABLE)
        
        conversation_id = f"{session_id}#{int(time.time())}"
        timestamp = int(time.time())
        
        table.put_item(
            Item={
                'conversation_id': conversation_id,
                'timestamp': timestamp,
                'session_id': session_id,
                'user_message': user_message,
                'bot_response': bot_response,
                'created_at': timestamp
            }
        )
        
    except Exception as e:
        print(f"DynamoDB error: {str(e)}")
        # Don't fail the request if storage fails