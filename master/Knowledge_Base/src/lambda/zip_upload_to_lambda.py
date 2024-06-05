import boto3
from botocore.config import Config
import shutil
import argparse

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-d", "--dir_name", help="Directory name")
    parser.add_argument("-l", "--lambda_name", help="Lambda function name")

    args = parser.parse_args()

    dir_name = args.dir_name
    lambda_function_name = args.lambda_name
    
    # upload zip to lambda function
    lambda_config = Config(
        read_timeout=900,
        connect_timeout=900,
        retries={"max_attempts": 0}
    )
    
    client = boto3.client('lambda', region_name='us-east-1', config=lambda_config)
    
    zip_bytes = open(dir_name + '.zip', 'rb').read()
    
    response = client.update_function_code(
        FunctionName=lambda_function_name,
        ZipFile=zip_bytes,
        ImageUri='string',
        Publish=False,
        Architectures=[
            'x86_64',
        ]
    )
    

if __name__ == "__main__":
    main()