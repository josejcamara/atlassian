"""
Fix Jira macros in a migrated page

Requires BeautifulSoup and click

"""

from cgi import print_arguments
from atlassian import Confluence
import sys, os
import re
import datetime as dt
import click
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv() # Take environment variables from .env

LINK_TO_FIX = 'my.server.domain'

# ===================
# JIRA Cloud version
# ===================
CONFLUENCE_URL=os.getenv('CONFLUENCE_CLOUD_BASE_URL')

@click.command()
@click.argument('email')    # myuser
@click.argument('api_key')  # WDI8MSlEU9StuhlgDxfM3EA9
# @click.argument('page_id')
def cli(email, api_key):
    space = "RCHPR"
    cf = Confluence(CONFLUENCE_URL, email, password=api_key, cloud=True)


    MAX_PAGES = 500
    iloop = 0
    links_found = 0

    while True:
        retrieved = 0
        spacePages = cf.get_all_pages_from_space(space, start=iloop*MAX_PAGES, limit=MAX_PAGES, status=None, expand=None, content_type='page')
        iloop +=1
        for pg in spacePages:
            retrieved += 1
            # if pg['id'] not in ('24253508', '133432997'): continue  #####
            # print(dir(pg))
            # print(pg.keys())
            # continue
            page_id = pg['id']

            page = cf.get_page_by_id(page_id, expand='body.storage')
            print(','.join([pg['id'], '"'+pg['title']+'"', page['_links']['self']]))
            # print(dir(page))
            # print('------')
            # print(page['_links']['self'])
            # break

            storage = page['body']['storage']['value']
            soup = BeautifulSoup(storage, 'lxml')

            # Find all Jira macros
            for macro in soup.find_all(lambda tag: tag.name == 'a' and LINK_TO_FIX in tag.attrs.get('href','')):
                links_found += 1
                print(' ,,,', macro.attrs['href'])
                # fix_macro(macro)

            # break

            #     # find the server_id, is it the old or new one?
            #     print(f"Fixing macro {macro['ac:macro-id']}")
            #     tag = macro.find(lambda tag: tag['ac:name']=='serverId')
            #     if tag.string == NEW_SERVER_ID:
            #         print('Macro is already fixed')
            #     else:
            #         fix_macro(macro)
            #         print('Fixing')

            # new_body = str(soup)
            # cf.update_page(page['id'], page['title'], body=new_body)
            # print('Page fixed')
            # break

        if retrieved < MAX_PAGES or iloop>1000: 
            break

    print('>>> TOTAL PAGES:', (iloop-1)*MAX_PAGES + retrieved)
    print('>>> TOTAL LINKS:', links_found)

OLD_LINK = os.getenv('SERVER_CONFLUENCE_BASE_URL') + '/display'
NEW_LINK = os.getenv('CLOUD_CONFLUENCE_BASE_URL') + '/wiki/spaces'
def fix_macro(macro):
    print('BEFORE', macro)
    # href = macro.attrs['href']
    # if href.startswith('https://LINK_TO_FIX/pages/viewpage.action?pageId='):
    #     pass


    # macro.attrs['href'] = macro.attrs['href'].replace(OLD_LINK, NEW_LINK)
    # print('AFTER', macro)
    # print(tag)
    # tag = macro.find(lambda tag: tag['ac:name']=='serverId')
    # tag.string = NEW_SERVER_ID

    # tag = macro.find(lambda tag: tag['ac:name']=='server')
    # tag.string = NEW_SERVER_NAME


    # print('Fixing', macro)


if __name__ == '__main__':
    cli()
