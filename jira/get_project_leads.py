import requests
from requests.auth import HTTPBasicAuth
import json

# ===================
# JIRA Cloud version
# ==================
COMPANYID = "mycompany"
USERNAME = "<your_username>"
USERTOKEN = "<your_personal_token>"

auth = HTTPBasicAuth(USERNAME, USERTOKEN)

headers = {
   "Accept": "application/json"
}

url = f"https://{COMPANYID}.atlassian.net/rest/api/3/project?expand=lead"
response = requests.request(
   "GET",
   url,
   headers=headers,
   auth=auth
)

print('ProjectId, ProjectLead')
projectList = json.loads(response.text)
for project in projectList:
    print(project.get("key") + ", " + project['lead']['displayName'])

