import boto3
import logging
import os

sts_client = boto3.client('sts')

log_level = os.getenv('LOG_LEVEL', 'INFO')


def get_logger(log_level):
    
    """
    Returns a logger instance
    """

    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    return logger


def assume_role(account_id: str, role_name: str, session_name: str = "AssumeRoleSession"):
    """
    Assumes an IAM role in the given AWS account and returns temporary credentials.
    """
    
    role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
    
    try:
        resp = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName=session_name
        )
        
        credentials = resp['Credentials']
        
        return {
            "AccessKeyId": credentials['AccessKeyId'],
            "SecretAccessKey": credentials['SecretAccessKey'],
            "SessionToken": credentials['SessionToken'],
            "Expiration": credentials['Expiration'].isoformat()
        }
    
    except Exception as e:
        logger = get_logger(log_level)
        logger.error(f"Failed to assume role: {e}")
        raise e
