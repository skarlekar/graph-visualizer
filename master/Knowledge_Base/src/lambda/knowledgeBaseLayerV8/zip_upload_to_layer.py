import boto3
from botocore.config import Config
import argparse

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-d", "--dir_name", help="Directory name")
    parser.add_argument("-l", "--lambda_layer_name", help="Lambda layer name")

    args = parser.parse_args()

    dir_name = args.dir_name
    lambda_layer_name = args.lambda_layer_name
    
    # upload zip to lambda function
    lambda_config = Config(
        read_timeout=900,
        connect_timeout=900,
        retries={"max_attempts": 0}
    )
    
    client = boto3.client('lambda', region_name='us-east-1', config=lambda_config)
    
    zip_bytes = open(dir_name + '.zip', 'rb').read()
    
    response = client.publish_layer_version(
        LayerName=lambda_layer_name,
        Content={
            'ZipFile': zip_bytes
        },
        CompatibleRuntimes=[
            'python3.9'
        ],
        CompatibleArchitectures=[
            'x86_64',
        ]
    )
    

if __name__ == "__main__":
    main()
