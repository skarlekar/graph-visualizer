import requests
import os


def bulk_load_csv_to_neptune(file_name):
    host = os.getenv("NEPTUNE_HOST")
    port = 8182
    region = 'us-east-1'
    iamRoleArn = os.getenv("IAM_ROLE_ARN")
    url = f"https://{host}:{port}/loader"

    payload = {
        "source": f"s3://kg-input-data/{file_name}",
        "format": "csv",
        "iamRoleArn": iamRoleArn,
        "region": region,
    }

    # Send the POST request
    response = requests.post(url, json=payload)
    return response

def main(file_name):
    response = bulk_load_csv_to_neptune(file_name=file_name)
    if response.status_code == 200:
        print("Bulk load completed.")
    else:
        print(f"Request failed with status code {response.status_code}")

if __name__ == '__main__':
    file_names_to_upload = ['property_vertex.csv', 'loan_vertext.csv', 'property_loan_edges.csv']
    for file_name in file_names_to_upload:
        main(file_name=file_name)
    print("Completed")