import requests
import json
from requests.auth import HTTPBasicAuth
import getpass
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================
# CONFLUENCE Server version
# ==========================
CONFLUENCE_BASE_URL = os.getenv('SERVER_CONFLUENCE_BASE_URL')
ADMIN_USRNAME = os.getenv('SERVER_ADMIN_USRNAME')
ADMIN_USRPWD=getpass.getpass(f'Enter pasword for {ADMIN_USRNAME}: ')

def getAllSpacesIds():
    # REST API 
    # https://docs.atlassian.com/ConfluenceServer/rest/7.4.7/#api/space
    url_action = f"{CONFLUENCE_BASE_URL}/rest/api/space?limit=9999"

    headers = {
        "Accept": "application/json"
    }

    response = requests.request(
        "GET",
        url_action,
        headers=headers,
        auth = HTTPBasicAuth(ADMIN_USRNAME, ADMIN_USRPWD),
        verify=False
    )

    spaceIdList = []
    allSpaces = json.loads(response.text)
    for space in allSpaces['results']:
        spaceKey = space['key']
        if not spaceKey.startswith("~"): continue # Ignore NON Personal spaces
        spaceIdList.append(spaceKey)

    return spaceIdList


def isWritableSpace(spaceKey):
    # SOAP API (Couldn't find similar in REST)
    # https://docs.atlassian.com/atlassian-confluence/6.6.0/com/atlassian/confluence/rpc/soap/ConfluenceSoapService.html#getSpacePermissionSets-java.lang.String-java.lang.String-
    url_action = f"{CONFLUENCE_BASE_URL}/rpc/json-rpc/confluenceservice-v2?os_authType=basic"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.request(
        "POST",
        url_action,
        headers=headers,
        auth = HTTPBasicAuth(ADMIN_USRNAME, ADMIN_USRPWD),
        verify=False,
        data='{ "jsonrpc" : "2.0", "method" : "getSpacePermissionSets", "params" : ["'+spaceKey+'"], "id": "'+spaceKey+'"  }'
    )

    spaceInfo = json.loads(response.text) #, sort_keys=True, indent=4, separators=(",", ": "))
    for lnr in spaceInfo['result']:
        for lns in lnr['spacePermissions']:
            if lns['userName'] in ('user1','user2'): continue   # Leavers
            if (lns['groupName'] == 'confluence-administrators'): continue # Confluence admin still can do everything
            if lnr['type'] not in ('VIEWSPACE','EXPORTPAGE') and (lns['userName']!=None or lns['groupName']!=None):
                # print(spaceKey, lnr['type'], lns['userName'], lns['groupName'] )
                return True
    return False

if __name__ == '__main__':
    targetFilename = 'onprem_writable_spaces.txt'
    spaceIdList = getAllSpacesIds()
    with open(targetFilename,'w') as f:
        for spaceId in spaceIdList:
            if isWritableSpace(spaceId):
                f.write(spaceId)
                f.write('\n')
    print(f'Result saved in {targetFilename}')
