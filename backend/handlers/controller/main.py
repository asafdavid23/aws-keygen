import json
import boto3
import uuid
from datetime import datetime
import os
import botocore
import logging

# Initialize the boto3 clients
sts_client = boto3.client('sts')
aws_region = sts_client.meta.region_name
aws_account_id = sts_client.get_caller_identity().get('Account')
sfn = boto3.client('stepfunctions')
state_machine_name = os.getenv('STATE_MACHINE_NAME')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

if not state_machine_name:
    raise Exception('STATE_MACHINE_NAME environment variable is not set.')

state_machine_arn = f'arn:aws:states:{aws_region}:{aws_account_id}:stateMachine:{state_machine_name}'


def lambda_handler(event, context):
    """
    Lambda handler to store the access request in DynamoDB.
    """
    
    # Parse the request body
    body = json.loads(event['body'])
    
    requester_name = body.get('requester_name', 'Unknown')
    requester_email = body.get('requester_email', 'Unknown')
    account_id = body.get('account_id', 'Unknown')
    role_name = body.get('role_name', 'Unknown')
    
    # Generate a unique request ID
    request_id = str(uuid.uuid4())
    
    # Get the current timestamp
    request_time = datetime.now().isoformat()
    
    step_function_input = {
        'request_id': request_id,
        'requester_name': requester_name,
        'requester_email': requester_email,
        'account_id': account_id,
        'role_name': role_name,
        'request_time': request_time
    }
    
    # Start the Step Function execution
    try:
        resp = sfn.start_execution(
            stateMachineArn=state_machine_arn,
            name=request_id,
            input=json.dumps(step_function_input)
        )
        
        # Poll the Step Function execution status
        execution_arn = resp['executionArn']
        
        while True:
            status_response = sfn.describe_execution(
                executionArn=execution_arn
            )
            
            status = status_response['status']
            
            if status == 'SUCCEEDED':
                result = status_response['output']
                break
            elif status == 'FAILED' or status == 'TIMED_OUT' or status == 'CANCELLED':
                error = status_response['output']
                
                return {
                    'statusCode': 500,
                    'body': json.dumps({
                        'message': 'An error occurred while executing the Step Function.',
                        'error': error
                    })
                }
                       
    except botocore.exceptions.ClientError as e:
        error_message = e.response['Error']['Message']
        logger.error(f"An error occurred: {error_message}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'An error occurred while starting the Step Function execution.',
                'error': error_message
            })
        }

    except botocore.exceptions.ParamValidationError as e:
        error_message = e.__str__()
        logger.error(f"An error occurred: {error_message}")
        
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Invalid input provided.',
                'error': error_message
            })
        }
    
    # Return a 200 response if successful
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Access request submitted successfully.',
            'step_function_output': result,
            'request_id': request_id
        })
    }
