import os
import json
import requests
import csv
import pendulum
import argparse

# Create an ArgumentParser object
parser = argparse.ArgumentParser()

# Add an argument for the CSV file name
parser.add_argument('--csv_file', help='Name of the CSV file to write the data to')

# Parse the arguments
args = parser.parse_args()

if args.csv_file is None:
    print("Please provide a csv file name.")
    exit()

# IBM Cloud IAM API key
api_key = os.environ.get("IBM_CLOUD_API_KEY")

# Get all the API keys for the IBM Cloud account
headers = {"Content-Type": "application/json", "Accept": "application/json","Authorization": f"Bearer {api_key}"}
url = "https://iam.cloud.ibm.com/v1/apikeys"
response = requests.get(url, headers=headers)
data = json.loads(response.text)

# open csv file and write the data
with open(args.csv_file, mode='w') as file:
    csv_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(['Key name', 'Creation Time', 'Age', 'IBM Cloud Account'])
    for key in data['apikeys']:
        creation_time = key["created_at"]
        creation_datetime = pendulum.parse(creation_time)
        age = pendulum.now() - creation_datetime
        if age.in_seconds() > 30*24*60*60:
            csv_writer.writerow([key['name'], creation_datetime.to_datetime_string(), age, key['account_id']])
        else:
            print(f"Key {key['name']} is still valid.")
