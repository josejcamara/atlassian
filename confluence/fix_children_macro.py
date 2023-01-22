"""
Fix Jira macros in a migrated page

Requires BeautifulSoup and click

"""

from atlassian import Confluence
import sys, os
import re
import datetime as dt
import click
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv() # Take environment variables from .env

# ===================
# JIRA Cloud version
# ===================
CONFLUENCE_URL=os.getenv('CLOUD_CONFLUENCE_BASE_URL')
OLD_SERVER_ID = os.getenv('OLD_SERVER_ID')
NEW_SERVER_ID = os.getenv('NEW_SERVER_ID')
NEW_SERVER_NAME = 'System JIRA'

@click.command()
@click.argument('email')
@click.argument('api_key')
@click.argument('page_id')
def cli(email, api_key, page_id):
    cf = Confluence(CONFLUENCE_URL, email, password=api_key, cloud=True)

    page = cf.get_page_by_id(page_id, expand='body.storage')
    storage = page['body']['storage']['value']
    soup = BeautifulSoup(storage, 'lxml')

    # print(soup)
    # exit(-1)
    # Their PageId = 11966812, 23166980 -> 23168278
    # My PageId = 75628731

    # Find all Jira macros
    for macro in soup.find_all(lambda tag: tag.name == 'ac:structured-macro' and tag.attrs['ac:name'] == 'children'):
        # find the server_id, is it the old or new one?
        print(f"Fixing macro {macro['ac:macro-id']}")
        print(macro)
        # tag = macro.find(lambda tag: tag['ac:name']=='serverId')
        # if tag.string == NEW_SERVER_ID:
        #     print('Macro is already fixed')
        # else:
        #     fix_macro(macro)
        #     print('Fixing')

    # new_body = str(soup)
    # cf.update_page(page['id'], page['title'], body=new_body)
    # print('Page fixed')

def fix_macro(macro):
    tag = macro.find(lambda tag: tag['ac:name']=='serverId')
    tag.string = NEW_SERVER_ID

    tag = macro.find(lambda tag: tag['ac:name']=='server')
    tag.string = NEW_SERVER_NAME


if __name__ == '__main__':
    cli()
