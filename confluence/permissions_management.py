import requests
import json
from requests.auth import HTTPBasicAuth

# =========================
# CONFLUENCE Cloud version
# =========================
COMPANYID = "mycompany"
ADMIN_USRNAME = "<your_username>"
ADMIN_USRPWD = "<your_personal_token>"

CONFLUENCE_CLOUD_BASE_URL = f"https://{COMPANYID}.atlassian.net/"

PERMISSIONS_MAP = {
    # "SETPAGEPERMISSIONS": None,
    "REMOVEPAGE": ['delete','page'],
    "EDITBLOG": ['create','blogpost']
}

def get_Permissions_Cloud(spaceKey):
    # https://community.atlassian.com/t5/Confluence-questions/REST-API-call-to-get-Confluence-space-permissions/qaq-p/1171861
    url_action = f"{CONFLUENCE_CLOUD_BASE_URL}/wiki/rest/api/space/{spaceKey}?expand=permissions"

    headers = {
        "Accept": "application/json"
    }

    response = requests.request(
        "GET",
        url_action,
        headers=headers,
        auth = HTTPBasicAuth(ADMIN_USRNAME, ADMIN_USRPWD)
    )

    jsonResponse = json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": "))
    return jsonResponse

def set_Permissions_Cloud(spaceKey):
    perms_to_apply = []
    with open(f"GIC.txt") as json_file:
        perm_list = json.load(json_file)
        for perm in perm_list:
            # print(perm)
            permType = perm.get('type',None)
            if permType not in PERMISSIONS_MAP:
                continue
            operation = PERMISSIONS_MAP[permType]
            for perm_row in perm.get('spacePermissions',[]):
                user = perm_row.get('userName', None) 
                group = perm_row.get('groupName', None) 

                perms_to_apply.append({
                    "subject": {
                        "type": "user" if user != None else "group",
                        "identifier": user if user != None else group
                    },
                    "operation": {
                        "key": operation[0],
                        "target": operation[1]
                    },
                })

            break  # /////

    url_action = f"{CONFLUENCE_CLOUD_BASE_URL}/wiki/rest/api/space/{spaceKey}/permission"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = json.dumps(perms_to_apply)

    response = requests.request(
        "POST",
        url_action,
        data=payload,
        headers=headers
    )

    print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))

# wiki/rest/api/space/{spaceKey}/permission
pjKey = 'MYPROJECT'
print(get_Permissions_Cloud(pjKey))
# set_Permissions_Cloud(pjKey)