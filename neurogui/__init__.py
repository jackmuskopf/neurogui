import boto3
from neurogui.settings import settings

boto3.setup_default_session(**settings['AwsCredentials'])

