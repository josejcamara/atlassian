#
# https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-group/#api-wiki-rest-api-group-user-delete
#

import os
import csv
import json
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv() # Take environment variables from .env

INPUT_FILENAME = './export-users-to-delete.csv'

# Atlassian > Administration > Product Access > Confluence
# (This are the groups taking licenses. Any user in these groups count in the licenses)
APP_ROLES = {
    'administrators': '',
    'confluence-administrators': '',
    'confluence-users': '',
    'sec-wiki_user': '',
    'site-admins': ''
}

# ===================
# Cloud version
# ===================
COMPANY_ID = os.getenv('CLOUD_COMPANY_ID')
USERNAME = os.getenv('ADMIN_USRNAME')
USERTOKEN = os.getenv('ADMIN_USRPWD')

AUTH = HTTPBasicAuth(USERNAME, USERTOKEN)

HEADERS = {
    "Accept": "application/json"
}

AUTH = HTTPBasicAuth(USERNAME, USERTOKEN)

def get_app_groups_ids(params='rest/api/group?limit=999'):
    """ Populate the groups Ids for the app group names """
    url = f"https://{COMPANY_ID}.atlassian.net/wiki/" + params

    response = requests.request(
        "GET",
        url,
        headers=HEADERS,
        auth=AUTH
    )
    res = json.loads(response.text)
    is_last = res['size'] < res['limit']

    for group in res['results']:
        if group['name'] in APP_ROLES:
            APP_ROLES[group['name']] = group['id']

    if not is_last:
        get_app_groups_ids(res['_links']['next'])    


def get_memberships_for_user(user_id):
    """ Returns the groups that a user is a member of """
    url = f"https://{COMPANY_ID}.atlassian.net/wiki/rest/api/user/memberof"

    query = {
        'accountId': user_id
    }

    response = requests.request(
        "GET",
        url,
        headers=HEADERS,
        params=query,
        auth=AUTH
    )

    res_obj = json.loads(response.text)
    res = res_obj["results"]

    res_dc = {}
    for group in res:
        res_dc[group['name']] = group['id']

    return res_dc


def remove_user_from_group(user_id, group_id):
    """ Remove the group from the user group list """
    url = f"https://{COMPANY_ID}.atlassian.net/wiki/rest/api/group/userByGroupId"

    query = {
        'groupId': group_id,
        'accountId': user_id
    }

    response = requests.request(
        "DELETE",
        url,
        headers=HEADERS,
        params=query,
        auth=AUTH
    )

    if not response.ok:
        print("ERROR!!", response)
        print(response.text)
        exit(1)

def main():
    """ Main action to perform """
    # Populate APP_ROLES
    get_app_groups_ids()

    # Read csv with users to remove from groups
    csv_row_user_id = 0
    csv_row_user_name = 1
    csv_row_user_email = 2
    csv_row_user_status = 3
    csv_row_user_last_seen = 7
    csv_never_accessed_value = 'Never'

    total_disabled = 0
    count_rows = 0
    with open(INPUT_FILENAME, encoding='UTF8') as csv_to_remove:
        spamreader = csv.reader(csv_to_remove)
        next(spamreader)  # Skip header
        for row in spamreader:
            user_id = row[csv_row_user_id]
            user_name = row[csv_row_user_name]
            user_email = row[csv_row_user_email]
            user_status = row[csv_row_user_status]
            last_seen_confluence = row[csv_row_user_last_seen]
            # If the user has already accessed, keep their permissions
            if not last_seen_confluence.startswith(csv_never_accessed_value):
                continue
            print(user_email, ' - ', user_status, ' - ', last_seen_confluence)  # Log, user analysed
            count_rows += 1

            user_groups = get_memberships_for_user(user_id)
            is_disabled = False

            for group_name, group_id in APP_ROLES.items():
                if group_name in user_groups:
                    is_disabled = True
                    print('    Removing', user_name, 'from', group_name)    # Log, group removed
                    remove_user_from_group(user_id, group_id)

            if is_disabled:
                print('')   # Log, separation between users
                total_disabled += 1

            # # CONTROL - TO REMOVE
            # if count_rows > 100:
            #     print('STOPPED for control at row: ', count_rows)
            #     break


    print('TOTAL LICENSES FREE:', total_disabled)   # Log, Final result

#
# === MAIN ===
#
if __name__ == '__main__':
    main()
