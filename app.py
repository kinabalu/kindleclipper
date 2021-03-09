#!/usr/bin/env python3

from jwt import (
    JWT,
    jwk_from_dict,
)
from datetime import datetime, timedelta, timezone
import json
import pprint
from bs4 import BeautifulSoup
import os
import requests
import click
import re

import settings

instance = JWT()


@click.group()
def cli():
    pass


@cli.command()
def jwk():
    """
    From the Amazon signin page, attempting to get jwk working
    """
    signing_key = jwk_from_dict({
        'kty': 'RSA',
        'e': 'AQAB',
        'n': 'gXXZV1VqZ6k_uQtyJNJy5q-qvKdqrXJNgKUO1aYc1UPBVqlhCP0GPxf-0GSo-LEtArgcbF8-j6_vSLSqztYxxF8og--rB8zAyZ8DXZaugX-UiJDQnoJL_HtXKuwIm9U7oEPoeD6H4ZDcfbsPj77xVn7UA2-a90N4aZqMC8EIfXIy1tqSbSPnxPOaiEmy8xGtG-L3RdCyc7TL0Swd_f0_DjRT6ip91IBlCmquoa-xJgZ9e44PVH4AwdyssiV4ZLEZ5yFcE0zcRb_62kx_TQptidbJ4nHocFVjmUW9YsrAWeKrBmOGZEjO4vbATYs1Yf4vgcH7Ix61EPR5sbDP4SlBWQ',
        'd': '...'})

    pprint.pprint(signing_key)


@cli.command()
def read():

    # https://read.amazon.com/notebook?asin=B082RS7N3X&contentLimitState=&=
    cookie = settings.AMAZON_COOKIE

    res = requests.get('https://read.amazon.com/notebook',
                       headers={
                           'Accept-Encoding': 'gzip, deflate',
                           'Content-Type': 'application/json; charset=UTF-8',
                           'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:87.0) Gecko/20100101 Firefox/87.0",
                           'Cookie': cookie
                       }
                       )

    print(res.text)


def parse_my_clippings():
    separator = '=========='

    highlight_re = r"^[^\d]*(\d*)[^\d]*([\d]*)-([\d]*) | Added on (.*)$"
    clippings = []
    with open(settings.MY_CLIPPINGS_PATH, 'r') as clippings_file:
        data = clippings_file.read()
        entries = data.split(separator + '\n')
        for entry in entries:
            lines = entry.split('\n')

            if len(lines) <= 1:
                continue

            book_title = lines[0].encode('ascii', 'ignore').decode()
            highlight_metadata = lines[1]

            metadata = {}
            metadata_type = None
            metadata_split = highlight_metadata.split('|')
            if highlight_metadata.find('Bookmark') > -1:
                metadata_type = 'bookmark'
                page_num_search = re.findall('\d+', metadata_split[0])
                page_num = int(page_num_search[0])
                range_search = re.findall('\d+', metadata_split[1])

                added_search = re.findall(
                    '\sAdded on\s(.*)', metadata_split[2])
                metadata['page'] = page_num
                metadata['location_1'] = int(range_search[0])
                metadata['date'] = added_search[0]

            if highlight_metadata.find('Highlight') > -1:
                metadata_type = 'highlight'
                highlight_detail = lines[3]

                page_num_search = re.findall('\d+', metadata_split[0])
                page_num = int(page_num_search[0])
                range_search = re.findall('\d+', metadata_split[1])

                added_search = re.findall(
                    '\sAdded on\s(.*)', metadata_split[2])
                metadata['page'] = page_num
                metadata['location_1'] = int(range_search[0])
                metadata['location_2'] = int(range_search[1])
                metadata['date'] = added_search[0]

            clippings.append({
                'title': book_title,
                'metadata': metadata,
                'type': metadata_type,
                'detail': highlight_detail
            })

    return clippings


@cli.command()
def my_clippings():
    clippings = parse_my_clippings()
    pprint.pprint(clippings)


@cli.command()
def login():
    signin_page_res = requests.get('https://www.amazon.com/ap/signin?openid.assoc_handle=amzn_kweb&openid.return_to=https%3A%2F%2Fread.amazon.com%2F&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&pageId=amzn_kcr',
                                   headers={
                                       'Accept-Encoding': 'gzip, deflate',
                                       'Content-Type': 'application/json; charset=UTF-8',
                                       'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:87.0) Gecko/20100101 Firefox/87.0",
                                   }
                                   )

    soup = BeautifulSoup(signin_page_res.text, 'html.parser')

    login_inputs = {}
    for input_tag in soup.find_all('input'):
        name = input_tag.get('name')
        value = input_tag.get('value')

        if not value and name not in ('email', 'password'):
            continue

        login_inputs[name] = value

    login_inputs['email'] = settings.AMAZON_USERNAME
    login_inputs['password'] = settings.AMAZON_PASSWORD

    pprint.pprint(login_inputs)
    login_res = requests.post('https://www.amazon.com/ap/signin',
                              headers={
                                  'Accept-Encoding': 'gzip, deflate',
                                  'Content-Type': 'application/json; charset=UTF-8',
                                  'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:87.0) Gecko/20100101 Firefox/87.0",
                              },
                              data=login_inputs
                              )
    print(login_res.text)


if __name__ == '__main__':
    cli()
