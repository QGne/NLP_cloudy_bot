import json
import boto3
import os
import time
import uuid
from decimal import Decimal
from botocore.config import Config

# Initialize AWS clients
aws_region = os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION') or 'us-east-1'
dynamodb = boto3.resource('dynamodb', region_name=aws_region)
sagemaker_runtime = boto3.client(
    'sagemaker-runtime',
    region_name=aws_region,
    config=Config(read_timeout=12, connect_timeout=3, retries={'max_attempts': 1, 'mode': 'standard'})
)

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
        
        message = body.get('message', '')
        session_id = body.get('session_id', str(uuid.uuid4()))
        
        if not message:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'Message is required'})
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
    Get response from SageMaker endpoint
    """
    try:
        # Prepare payload for an instruction-following model (text2text)
        payload = {
            "inputs": f"Instruction: {message}\n\nResponse:",
            "parameters": {
                "max_new_tokens": 128,
                "temperature": 0.1,
                "top_p": 0.9,
                "do_sample": False
            }
        }
        
        # Call SageMaker endpoint
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=SAGEMAKER_ENDPOINT,
            ContentType='application/json',
            Body=json.dumps(payload)
        )
        
        # Parse response
        result = json.loads(response['Body'].read().decode())
        
        # Handle HuggingFace text2text output
        ai_response = None
        if isinstance(result, list) and result:
            # HF pipeline for text2text usually returns list of dicts with 'generated_text'
            generated_text = result[0].get('generated_text') or result[0].get('summary_text') or ''
            ai_response = (generated_text or '').strip()
        elif isinstance(result, dict):
            ai_response = (result.get('generated_text') or result.get('text') or '').strip()
        
        if not ai_response:
            ai_response = "I'm here to help. Could you please rephrase your question?"
        
        return ai_response
        
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