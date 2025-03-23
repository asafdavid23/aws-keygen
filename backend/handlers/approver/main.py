import json
import time
import boto3
import requests  # If you plan to call an external API to check the approval status
import os

# Example of the API that stores the approval status
api_url = os.environ.get('APPROVAL_API_URL', '')

if not api_url:
    raise ValueError('Approval API URL is not set')


def get_approval_status_from_api():
    """
    Polls the approval status from an external API or service.
    Example: calling an API Gateway that tracks the admin's approval.
    """
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            # Example: The API returns a JSON with approval status
            approval_data = response.json()
            return approval_data.get('approved', False)  # Assuming the response has a 'approved' field
        else:
            print(f"Error calling the approval API: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error during approval status check: {e}")
        return None
    

# Lambda handler function
def lambda_handler(event, context):
    """
    Lambda function to wait for approval status. 
    This Lambda function will poll an external API or DynamoDB for approval.
    """
    # Retrieving the maximum number of retries and the current retry count from Step Functions input
    max_retries = event.get('maxRetries', 5)  # Maximum retries (for example, 5 retries)
    current_retry = event.get('currentRetry', 0)  # Current retry count

    # Check the approval status from the external API
    approval_status = get_approval_status_from_api()

    # If approval status is found and is True, return success
    if approval_status is not None and approval_status:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'approvalStatus': 'approved',  # Return approval status as 'approved'
                'approved': True
            })
        }

    # If we haven't reached the max retries, retry
    if current_retry < max_retries:
        print(f"Approval not yet received, retrying {current_retry + 1}/{max_retries}...")
        time.sleep(30)  # Wait for 30 seconds before retrying (this can be adjusted)
        return {
            'currentRetry': current_retry + 1,
            'maxRetries': max_retries
        }

    # If max retries reached and still no approval, return failure
    return {
        'statusCode': 200,
        'body': json.dumps({
            'approvalStatus': 'not_approved',  # Return failure status if not approved
            'approved': False
        })
    }