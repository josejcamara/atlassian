# https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-permissions/#api-rest-api-3-mypermissions-get

import requests
from requests.auth import HTTPBasicAuth
import json

# ===================
# JIRA Cloud version
# ==================
COMPANYID = "mycompany"
USERNAME = "<your_username>"
USERTOKEN = "<your_personal_token>"
PROJECT_ID = "MYPROJECT"

auth = HTTPBasicAuth(USERNAME, USERTOKEN)

headers = {
   "Accept": "application/json"
}

url = f"https://{COMPANYID}.atlassian.net/rest/api/3/project/{PROJECT_ID}/role"
response = requests.request(
   "GET",
   url,
   headers=headers,
   auth=auth
)

print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
