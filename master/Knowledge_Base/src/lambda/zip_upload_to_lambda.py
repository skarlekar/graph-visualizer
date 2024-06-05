import boto3
from botocore.config import Config
import shutil
import sys

def main():
    dir_name = sys.argv[1]
    lambda_function_name = sys.argv[2]
    
    # zip directory
    shutil.make_archive(dir_name, 'zip', dir_name)
    
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
        Publish=False,
        Architectures=[
            'x86_64',
        ]
    )
    

if __name__ == "__main__":
    main()
