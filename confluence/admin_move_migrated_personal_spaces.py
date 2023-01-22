import requests
import json
import csv
from requests.auth import HTTPBasicAuth
import os

BASE_URL = os.getenv('CONFLUENCE_CLOUD_BASE_URL') + "/wiki/rest/api/" 
USERNAME = os.getenv('CLOUD_ADMIN_USRNAME')
PASSWORD = os.getenv('CLOUD_ADMIN_USRPWD')

#
#
#
def call_api(op, action_call, data=None, verify_ssl=True, verbose=True):
    """ Call to the API, adding the headers and returning a json object """

    url_action = BASE_URL + action_call

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    if data != None:
        data = json.dumps(data)

    if verbose:
        print('>>>> REQUEST >>>>', url_action)
        if data != None:
            print(" ---data: ",data)

    response = requests.request(
        op,
        url_action,
        headers=headers,
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        verify=verify_ssl,
        data=data
    )    

    if verbose:
        print('<<<< RESPONSE <<<<', response.status_code, response.text)

    return (response.status_code, response.text)

#
#
#
def get_space_blogposts(spaceId):
    result = []
    status, response = call_api("GET", "space/" + spaceId + "/content/blogpost")
    blogposts_list = json.loads(response)['results']
    for post in blogposts_list:
        # print(post)
        result.append([post['id'], post['title'], post['_links']['webui'] ])
    #
    return result

#
#
#
def get_content_by_id(pageId):
    status, response = call_api("GET", "content/" + pageId)
    print(json.loads(response))

#
#
#
def move_blogpost_id(postId, targetSpaceId, position='append'):
    status, response = call_api("PUT", "content/" + postId + "/move/" + position + "/" + targetSpaceId)
    print(json.loads(response))

#
#
#
def copy_blogpost_id(pageId, targetSpaceId):
    data = {
        "copyAttachments": True,
        "copyDescendants": True,
        "destinationPageId": targetSpaceId
    }
    status, response = call_api("POST", "content/" + pageId + "/pagehierarchy/copy", data)
    js = json.loads(response)
    print(js)
    print('Check status in: ', os.getenv('CONFLUENCE_CLOUD_BASE_URL') + "/wiki" + js["links"]["status"])
    return js


#
#
#
def create_blogpost(spaceKey, title, body={}):
    data = {
        "space": { "key": spaceKey },
        "title": title,
        "type": "blogpost",
        "body": body
    }
    status, response = call_api("POST", "content", data=data)
    print(status)

    return json.loads(response)




###
###
###
# spaces_cloud = get_spaces_info(None, None, None)
# print(spaces_cloud)
spaceId = '~jjimenez'
# spaceId = '~62010c36506317006b072853'
spaceIdNew = '138293673'  # ManualPost Cloud
rs = get_space_blogposts(spaceId)
print(rs)
print("-------------")
for ln in rs:
    get_content_by_id(ln[0])
    print("=====")
    # move_blogpost_id(ln[0], spaceIdNew, position='after')
    copy_blogpost_id(ln[0], spaceIdNew)
    break


# create_blogpost(spaceId, "DEMO1")