import json
import boto3
import logging
import os

# Initialize boto3 clients
sns_client = boto3.client('sns')
sts_client = boto3.client('sts')

log_level = os.getenv('LOG_LEVEL', 'INFO')
sns_topic_name = os.getenv('TOPIC_NAME', 'default-topic')
aws_region = sts_client.meta.region_name
aws_account_id = sts_client.get_caller_identity().get('Account')
sns_topic_arn = f'arn:aws:sns:{aws_region}:{aws_account_id}:{sns_topic_name}'


def get_logger(log_level: str):
    """
    Set up the logger with the log level specified in the environment variable LOG_LEVEL.
    """
    logger = logging.getLogger()
    logger.setLevel(log_level)
    return logger


def send_notification(account_id: str, role_name: str):
    """
    Send a notification to the SNS topic to notify admins of an access request.
    """
    
    message = f"Access request for admin role in account {account_id} for role {role_name}. Please approve or reject."
    subject = "Administrator Access Request"
    response = sns_client.publish(
        TopicArn=sns_topic_arn,
        Message=message,
        Subject=subject
    )
    logger = get_logger(log_level)
    logger.info(f"Notification sent to admins: {response}")
    return response