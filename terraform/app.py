import os
import boto3
import requests
import zipfile
import io
import json
import logging
import pandas as pd
from botocore.exceptions import BotoCoreError, ClientError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_file_to_s3(file_data, file_name, bucket_name):
    s3 = boto3.client('s3')
    try:
        response = s3.upload_fileobj(file_data, bucket_name, file_name, ExtraArgs={'ContentType': "text/csv"})
        logger.info(f"Response from s3.upload_fileobj: {response}")
    except (BotoCoreError, ClientError) as error:
        logger.error(f"Error uploading file to S3: {error}")
        raise

def download_and_upload_file():
    # Get a reference to the S3 client
    s3 = boto3.client('s3')

    # The name of the bucket
    bucket_name = os.environ['BUCKET_NAME']

    # URL of the zip file
    url = "https://www.zipshare.com/fileDownload/eyJhcmNoaXZlSWQiOiJhZDhlMTQ3OC1hMGI0LTRiOGYtOTdiZC1mMTZjZjM3M2Y3YmIiLCJlbWFpbCI6Im1iaW9tYmFuaXN0ZWZlbkBnbWFpbC5jb20ifQ=="

    try:
        # Download the zip file
        response = requests.get(url)
        response.raise_for_status()  # Verify that the request was successful

        # Create a ZipFile object from the response
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # For each file in the zip archive
            for filename in z.namelist():
                # If the file is a .csv
                if filename.endswith('.csv'):
                    # Read the file data from the zip archive
                    file_data = io.BytesIO(z.read(filename))

                    # Read the first 1000 lines of the file into a DataFrame
                    df = pd.read_csv(file_data, nrows=1000)

                    # Convert the DataFrame back into a CSV file object
                    csv_file = io.StringIO()
                    df.to_csv(csv_file, index=False)
                    csv_file.seek(0)  # Go back to the start of the file object

                    # Set the name attribute to the filename
                    csv_file.name = filename

                    # Upload the file to S3
                    upload_file_to_s3(csv_file, csv_file.name, bucket_name)

    except (requests.RequestException, zipfile.BadZipFile) as error:
        logger.error(f"Error during download or extraction: {error}")
        raise

def lambda_handler(event, context):
    # Call the function to download and upload the file
    download_and_upload_file()

    return {
        'statusCode': 200,
        'body': json.dumps('CSV files have been downloaded and uploaded to S3 successfully!')
    }
