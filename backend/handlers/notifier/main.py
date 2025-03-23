import json
import os
from utils import get_logger, send_notification

log_level = os.getenv('LOG_LEVEL', 'INFO')
logger = get_logger(log_level)

def lambda_handler(event, context):
    """
    Lambda handler to send a notification to the SNS topic.
    """
    
    try:
        # get the payload from API Gateway
        payload = json.loads(event['body'])
        account_id = payload['account_id']
        role_name = payload['role_name']
        
        if not account_id or not role_name:
            return {
                'statusCode': 400,
                'body': json.dumps('Please provide account_id and role_name in the request body.')
            }
            
        # Notify admins of the access request
        send_notification(account_id, role_name)
        
        # return a 200 response if successful
        return {
            'statusCode': 200,
            'body': json.dumps('Notification sent successfully.')
        }
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps('An error occurred while sending the notification.')
        }