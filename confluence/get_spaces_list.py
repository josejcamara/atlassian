from lib2to3.pytree import convert
import requests
import json
import csv
from requests.auth import HTTPBasicAuth
import os

IS_CLOUD = True

BASE_URL_CLOUD = os.getenv('CLOUD_CONFLUENCE_BASE_URL') + "/wiki/rest/api/"
USERNAME_CLOUD = os.getenv('CLOUD_ADMIN_USRNAME')
TOKEN_CLOUD = os.getenv('CLOUD_ADMIN_USRPWD')

BASE_URL_SERVER = os.getenv('SERVER_CONFLUENCE_BASE_URL') + "/rest/api/"
USERNAME_SERVER = os.getenv('SERVER_ADMIN_USRNAME')
PASSWORD_SERVER = os.getenv('SERVER_ADMIN_USRPWD')


BASE_URL = BASE_URL_CLOUD
USERNAME = USERNAME_CLOUD
PASSWORD =  TOKEN_CLOUD

if not IS_CLOUD:
    BASE_URL = BASE_URL_SERVER
    USERNAME = USERNAME_SERVER
    PASSWORD =  PASSWORD_SERVER


#
#
#
def call_api(action_call, base_url, username, password, verify_ssl=True, verbose=False):
    """ Call to the API, adding the headers and returning a json object """

    url_action = base_url + action_call

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    if verbose:
        print('>>>> REQUEST >>>>', url_action)

    response = requests.request(
        "GET",
        url_action,
        headers=headers,
        auth=HTTPBasicAuth(username, password),
        verify=verify_ssl
    )    

    if verbose:
        print('<<<< RESPONSE <<<<', response.status_code, response.text)

    return (response.status_code, response.text)


def get_spaces_info(base_url, username, password, limit=999, verify_ssl=True):

    status, response = call_api('space?type=personal&limit='+str(limit), base_url, username, password, verify_ssl=verify_ssl)

    site_attachment_volume = 0 

    spacesList = []
    space_key_results = json.loads(response)['results']
    for space in space_key_results:
        space_attachment_volume = 0 
    
        status, response = call_api("space/" + space["key"] + "/content?expand=history.lastUpdated", base_url, username, password, verify_ssl=verify_ssl)

        print("Space Key: " + space["key"] + ' => ' + space['name'])
        page_json = json.loads(response)
        last_updated = "0"
        page_results = page_json["page"]["results"]
        for page in page_results:
            page_attachment_volume = 0
            pageUpdated = page["history"]["lastUpdated"]["when"]
            if pageUpdated > last_updated:
                last_updated = pageUpdated

            status, response = call_api("content/" + page["id"] + "/child/attachment", base_url, username, password, verify_ssl=verify_ssl)

            attachment_results = json.loads(response)["results"]
            for attachment in attachment_results:
                page_attachment_volume += int(json.dumps(attachment["extensions"]["fileSize"]))

            space_attachment_volume += page_attachment_volume

        spacesList.append([space['name'], space['key'], len(page_results), last_updated, str(round(space_attachment_volume/1000.0/1000.0,2))])

    return spacesList


spaces_cloud = get_spaces_info(BASE_URL_CLOUD, USERNAME_CLOUD, TOKEN_CLOUD)
print(spaces_cloud)
dict_cloud = { spaces_cloud[i][0]: spaces_cloud[i] for i in range(len(spaces_cloud)) } 

spaces_server = get_spaces_info(BASE_URL_SERVER, USERNAME_SERVER, PASSWORD_SERVER, verify_ssl=False)

for i in range(len(spaces_server)):
    pages_in_cloud = 'N/A'
    space_key_cloud = 'N/A'
    user_name = spaces_server[i][0]
    if user_name in dict_cloud:
        pages_in_cloud = dict_cloud[user_name][2]
        space_key_cloud = dict_cloud[user_name][1]

    spaces_server[i].extend([pages_in_cloud, space_key_cloud])



# Save to CSV
# output_filename = '/Users/Jose.Jimenez/Desktop/personal_spaces_' + ('cloud' if IS_CLOUD else 'server') + '.csv'
# output_filename = output_filename + ('cloud' if IS_CLOUD else 'server')
output_filename = os.path.join(os.path.expanduser('~'), 'Desktop', 'spaces_server_vs_cloud.csv')
with open(output_filename ,'w') as f:
    write = csv.writer(f)
    write.writerow(['UserName','UserKey','NumPagesServer', 'LastUpdatedServer', 'TotalMbytesServer', 'NumPagesCloud', 'IdCloud'])
    write.writerows(spaces_server)

print('Result saved on: ' + output_filename)
