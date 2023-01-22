""" 
    Permissions management for the Confluence Server version
    For example:
        - Set Read-Only mode
"""
import os
import getpass
import json
import requests
import urllib3
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===================
# OnPrem version
# ===================
load_dotenv() # Take environment variables from .env
CONFLUENCE_BASE_URL = os.getenv('CONFLUENCE_PREM_BASE_URL')
#----------
ADMIN_USRNAME = getpass.getpass('Admin username: ')
ADMIN_USRPWD = getpass.getpass('Password: ')


def get_id_all_spaces(include_personal=False):
    """
        Get all spaces in the server (REST api)
        # https://docs.atlassian.com/ConfluenceServer/rest/7.4.7/#api/space
    """
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

    space_id_list = []
    all_spaces = json.loads(response.text)
    for space in all_spaces['results']:
        space_key = space['key']
        # Ignore Personal spaces ?
        if not include_personal and space_key.startswith("~"):
            continue 

        space_id_list.append(space_key)

    return space_id_list


def is_writable_space(space_info, ignore_users=None, ignore_groups=None):
    """ Check if a space has write access for any user """
    type_permissions_view_only = ['VIEWSPACE','EXPORTPAGE']

    for lnr in space_info:
        for lns in lnr['spacePermissions']:
            is_assigneed = lns['userName'] is not None or lns['groupName'] is not None
            if ignore_users is not None and lns['userName'] in ignore_users:
                continue   # Leavers
            if ignore_groups is not None and lns['groupName'] in ignore_groups:
                continue    # Admins
            if lnr['type'] not in type_permissions_view_only and is_assigneed:
                return True
    return False

def get_granted_entities(space_info, ignore_users=None, ignore_groups=None):
    """ Returns the list of entities (user/groups) having any permission in the space """
    entities = []
    if ignore_users is None:
        ignore_users = []
    if ignore_groups is None:
        ignore_groups = []

    for lnr in space_info:
        for lns in lnr['spacePermissions']:
            username, groupname = lns['userName'], lns['groupName']
            if username is not None and username not in ignore_users:
                entities.append(username)

            if groupname is not None and groupname not in ignore_groups:
                entities.append(groupname)

    return set(entities)

def get_space_permission_sets(space_key, verbose=False):
    """
        Get the space permissionSet (SOAP api - Couldn't find similar in REST)
        # https://docs.atlassian.com/atlassian-confluence/6.6.0/com/atlassian/confluence/rpc/soap/ConfluenceSoapService.html#getSpacePermissionSets-java.lang.String-java.lang.String-
    """
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
        data='{ "jsonrpc" : "2.0", "method" : "getSpacePermissionSets", "params" : ["'+space_key+'"], "id": "'+space_key+'"  }'
    )

    space_info = json.loads(response.text)
    if verbose:
        print(json.dumps(space_info, sort_keys=True, indent=4, separators=(",", ": ")))

    return space_info['result']

def set_readonly_mode(space_id, verbose=False):
    """
        Set all the spaces in read-only mode
        Data-Center has its own option: https://confluence.atlassian.com/doc/using-read-only-mode-for-site-maintenance-952624304.html
        but it looks like for Server we need to change the permissions for every single space
    """

    leavers = ['pdeepak','cinches']
    admins = ['confluence-administrators']
    permissions_to_remove = [
        'REMOVEOWNCONTENT',
        'EDITSPACE', 'REMOVEPAGE',
        'EDITBLOG', 'REMOVEBLOG',
        'CREATEATTACHMENT', 'REMOVEATTACHMENT',
        'COMMENT', 'REMOVECOMMENT',
        'SETSPACEPERMISSIONS', 'SETPAGEPERMISSIONS',
        'REMOVEMAIL',
        'EXPORTSPACE'
    ]

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }


    space_info = get_space_permission_sets(space_id) #, verbose=True)

    if is_writable_space(space_info, ignore_users=leavers, ignore_groups=admins):
        if verbose:
            print(space_id, 'is writable. Fixing...' )  # Log: Space changing

        user_groups_in_the_space = get_granted_entities(space_info, ignore_groups=admins)

        for entity_to_remove in user_groups_in_the_space:
            if verbose:
                print('    Disabling', entity_to_remove)  # Log: Space changing
            for permission_id in permissions_to_remove:
                url_action = f"{CONFLUENCE_BASE_URL}/rpc/json-rpc/confluenceservice-v2?os_authType=basic"
                response = requests.request(
                    "POST",
                    url_action,
                    headers=headers,
                    auth = HTTPBasicAuth(ADMIN_USRNAME, ADMIN_USRPWD),
                    verify=False,
                    data='{ "jsonrpc" : "2.0", "method" : "removePermissionFromSpace", "params" : ["'+permission_id+'", "'+entity_to_remove+'", "'+space_id+'"], "id": "'+space_id+'"  }'
                )

                if response.status_code != 200:
                    print(">>> ERROR:: removePermissionFromSpace", permission_id, entity_to_remove)
                    print(response.status_code)
                    print(response.text)

                # space_info = json.loads(response.text)

        return True

    # It was not writable
    return False

#
# == MAIN ==
#
if __name__ == '__main__':

    control = 0
    for id_space in get_id_all_spaces(include_personal=True):
        # if control >= 10:
        #     # For testing purposes
        #     break

        if set_readonly_mode(id_space, verbose=True):
            control += 1
