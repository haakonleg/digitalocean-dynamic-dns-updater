#!/usr/bin/env python3
from requests import request, get
from requests.exceptions import HTTPError
from typing import Optional
import sys
import argparse

API_HOST = 'https://api.digitalocean.com/v2'


def public_ip() -> str:
    try:
        res = get('https://ifconfig.me/')
        res.raise_for_status()
        return res.text
    except Exception as e:
        sys.exit('Failed to retrieve public IP:\n{}'.format(e))


def api_request(method: str, path: str, data: Optional[dict], apikey: str) -> dict:
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer {}'.format(apikey)}

    if data is not None:
        headers['Content-Type'] = 'application/json'

    try:
        res = request(method, API_HOST + path, headers=headers, json=data)
        res.raise_for_status()
        return res.json()
    except HTTPError as e:
        sys.exit('Failed to call digitalocean API (status {}):\n{}'.format(e.response.status_code, e.response.text))
    except Exception as e:
        sys.exit('Failed to call digitalocean API:\n{}'.format(e))


def do_update(domain: str, apikey: str, subdomains: set):
    records = api_request('GET', '/domains/{}/records'.format(domain), None, apikey)
    ip = public_ip()

    # Find records that should be updated
    names_found = set()
    to_update = []
    for record in records['domain_records']:
        if record['type'] == 'A' and record['name'] in subdomains:
            names_found.add(record['name'])
            if record['data'] != ip:
                print('{:<20}{:^30}update needed'.format(record['name'], record['data']))
                to_update.append(record)
            else:
                print('{:<20}{:^30}OK'.format(record['name'], record['data']))

    # Warn about not found records
    for not_found in subdomains.difference(names_found):
        print('WARNING: Could not find an A record for subdomain {}'.format(not_found))

    # Update the records
    update_cnt = 0
    for record in to_update:
        data = {'type': 'A', 'name': record['name'], 'data': ip}
        api_request('PUT', '/domains/{}/records/{}'.format(domain, record['id']), data, apikey)
        update_cnt += 1

    print('Updated {} records'.format(update_cnt))


def main():
    parser = argparse.ArgumentParser(description='Update DigitalOcean DNS subdomain records with public IP')
    parser.add_argument('--domain', help='The domain to update', type=str)
    parser.add_argument('--apikey', help='DigitalOcean API token', type=str)
    parser.add_argument('subdomains', help='Subdomains to update (name of A record)', nargs='+', type=str)
    args = parser.parse_args()

    do_update(args.domain, args.apikey, set(args.subdomains))


if __name__ == '__main__':
    main()
