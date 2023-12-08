from boto3 import client

def get_s3_client():
    return client("s3")