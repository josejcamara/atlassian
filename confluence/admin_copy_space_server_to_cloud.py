#!/usr/bin/env python
"""
Copy a page from one wiki to another

"""

# https://pypi.org/project/atlassian-python-api/
from atlassian import Confluence
import os
import click
import getpass

from dotenv import load_dotenv
load_dotenv() # Take environment variables from .env

import warnings
warnings.filterwarnings('ignore')

SERVER_VERSION_URL = os.getenv('SERVER_CONFLUENCE_BASE_URL')
CLOUD_VERSION_URL = os.getenv('CLOUD_CONFLUENCE_BASE_URL')
USER = os.getenv('SERVER_ADMIN_USRNAME')
EMAIL = os.getenv('SERVER_CLOUD_USRNAME')

# TODO : add dest title override

@click.command()
@click.option('--api-key', default=None)
@click.option('--dest-space', default='~62010c36506317006b072853')
@click.option('--dest-title', default=None)
@click.argument('src_page_id')
def main(src_page_id, api_key, dest_space, dest_title):
    cf_src = Confluence(url=SERVER_VERSION_URL, username=USER, password=getpass.getpass(f"Enter Confluence Server (Source) password for {USER}: "), verify_ssl=False)
    cf_dest = Confluence(CLOUD_VERSION_URL, username=EMAIL, password=api_key, cloud=True)

    src_page = cf_src.get_page_by_id(src_page_id, expand='version,body.storage')

    if dest_title is None:
        dest_title = 'TEMPORARY PAGE - ' + src_page['title']
    body = src_page['body']['storage']['value']

    dest_page = cf_dest.create_page(dest_space, dest_title, body, parent_id=None, type='page', representation='storage')

    print(f"Created new page {dest_page['id']} {dest_page['title']}")

    return dest_page

if __name__ == '__main__':
    main()
