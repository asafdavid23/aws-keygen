import json
import os
from utils import assume_role, get_logger

log_level = os.getenv('LOG_LEVEL', 'INFO')

logger = get_logger(log_level)

def lambda_handler(event, context):
    """
    AWS Lambda entry point. Assumes a role based on the provided JSON payload.
    """
    
    try:
        # parse the Incoming JSON payload
        payload = json.loads(event.get("body", "{}"))
        
        # Validate the payload
        account_id = payload.get("account_id")
        role_name = payload.get("role_name")
        
        if not account_id or not role_name:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Missing required parameters"})
            }
            
        # Assume the role
        credentials = assume_role(account_id, role_name)
        
        # Construct the response
        response_payload = {
            "AccessKeyId": credentials["AccessKeyId"],
            "SecretAccessKey": "****",  # Masked for security in logs
            "SessionToken": "****",     # Masked for security in logs
            "Expiration": credentials["Expiration"]
        }
        
        logger.info(f"Succesfully assumed role {role_name} in account {account_id}")
        
        return {
            "statusCode": 200,
            "body": json.dumps(response_payload)
        }
        
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Invalid JSON payload"})
        }
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal server error"})
        }
