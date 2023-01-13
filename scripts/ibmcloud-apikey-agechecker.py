import os
import json
import requests
import pendulum

# IBM Cloud IAM API key
api_key = os.environ.get("IBM_CLOUD_API_KEY")

# GitHub repository details
repo_owner = os.environ.get("GITHUB_USERNAME")
repo_name = os.environ.get("GITHUB_REPO_NAME")
github_token = os.environ.get("GITHUB_TOKEN")

# Get all the API keys for the IBM Cloud account
headers = {"Content-Type": "application/json", "Accept": "application/json","Authorization": f"Bearer {api_key}"}
url = "https://iam.cloud.ibm.com/v1/apikeys"
response = requests.get(url, headers=headers)
data = json.loads(response.text)

# Check age of each key and create GitHub issue if older than 30 days
for key in data['apikeys']:
    creation_time = key["created_at"]
    creation_datetime = pendulum.parse(creation_time)
    age = pendulum.now() - creation_datetime
    if age.in_seconds() > 30*24*60*60:
        issue_title = f"Expired API Key: {key['name']}"
        issue_body = f"The API key {key['name']} is older than 30 days. Please generate a new key.\n\nAPI Key Information:\n\n| Property | Value |\n| --- | --- |\n| Name | {key['name']} |\n| Created At | {creation_datetime.to_datetime_string()} |\n| IBM Cloud Account | {key['account_id']} |"
        headers = {"Authorization": f"Token {github_token}"}
        data = {"title": issue_title, "body": issue_body}
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
        response = requests.post(url, json=data, headers=headers)
    else:
        print(f"Key {key['name']} is still valid.")
