#!/usr/bin/env python3
from requests import request, get
from requests.exceptions import HTTPError
from typing import Optional
import argparse
import sys

CONFIG = {
    'api_host': 'https://api.digitalocean.com/v2',
    'api_key': '',
    'ipv6': False,
    'ipcheck_endpoint': 'https://api4.ipify.org',
    'ipv6check_endpoint': 'https://api6.ipify.org',
    'domains': []
}


def get_request(url: str) -> str:
  try:
    res = get(url)
    res.raise_for_status()
    return res.text
  except Exception as e:
    sys.exit('GET {} failed:\n{}'.format(url, e))


def api_request(method: str, path: str, data: Optional[dict]) -> dict:
  headers = {
      'Accept': 'application/json',
      'Authorization': 'Bearer {}'.format(CONFIG['api_key'])}

  if data is not None:
    headers['Content-Type'] = 'application/json'

  try:
    res = request(method, CONFIG['api_host'] + path, headers=headers, json=data)
    res.raise_for_status()
    return res.json()
  except HTTPError as e:
    sys.exit('Failed to call digitalocean API (status {}):\n{}'.format(e.response.status_code, e.response.text))
  except Exception as e:
    sys.exit('Failed to call digitalocean API:\n{}'.format(e))


def update_records(domain: str, records, public_ip: str, public_ipv6: str) -> int:
  update_cnt = 0

  # Check if records should be updated
  to_update = []
  for record in records:
    if record['data'] != {'A': public_ip, 'AAAA': public_ipv6}[record['type']]:
      print('{:<30}{:<30}{:^30} update needed'.format(domain, record['name'], record['data']))
      to_update.append(record)
    else:
      print('{:<30}{:<30}{:^30} OK'.format(domain, record['name'], record['data']))

  # Update the records
  update_cnt = 0
  for record in to_update:
    data = {'type': record['type'], 'name': record['name'],
            'data': {'A': public_ip, 'AAAA': public_ipv6}[record['type']]}

    api_request('PUT', '/domains/{}/records/{}'.format(domain, record['id']), data)
    update_cnt += 1

  return update_cnt


def find_records(domain: str, subdomains: set) -> list:
  names_found = set()
  records_found = []

  records = api_request('GET', '/domains/{}/records'.format(domain), None)
  for record in records['domain_records']:
    if record['name'] in subdomains:
      if record['type'] == 'A':
        records_found.append(record)
      elif CONFIG['ipv6'] and record['type'] == 'AAAA':
        records_found.append(record)
      else:
        continue

      names_found.add(record['name'])

  # Warn about not found records
  for not_found in subdomains.difference(names_found):
    print('WARNING: Could not find A or AAAA record for subdomain {}'.format(not_found))

  return records_found


def read_config(path: str):
  with open(path, 'r') as file:
    for i, line in enumerate(file):
      if len(line) < 2:
        continue

      try:
        sep = line.index('=')
        key, value = line[:sep], line[sep+1:].rstrip().lower()

        if key == 'domain':
          sep = value.index(' ')

          domain = value[:sep]
          subdomains = [subdomain.strip() for subdomain in value[sep+1:].split(',')]
          CONFIG['domains'].append([domain, *subdomains])
        elif key in CONFIG:
          default_value = CONFIG[key]

          if type(default_value) == bool:
            CONFIG[key] = {'true': True, 'false': False}[value]
          else:
            CONFIG[key] = value
        else:
          raise Exception('invalid key {}'.format(key))
      except ValueError as e:
        sys.exit('ERROR: parsing config at line {}'.format(i+1))
      except Exception as e:
        sys.exit('ERROR: parsing config at line {}:\n{}'.format(i+1, e))

  if len(CONFIG['api_key']) == 0:
    sys.exit('ERROR: api_key not set in config')

  if len(CONFIG['domains']) == 0:
    sys.exit('ERROR: no domain names specified in config')


def main():
  parser = argparse.ArgumentParser(description='Update DigitalOcean DNS subdomain records with public IP')
  parser.add_argument('--config', help="Path to config file", type=str, default='dyndns.conf')
  args = parser.parse_args()
  read_config(args.config)

  ip = get_request(CONFIG['ipcheck_endpoint'])
  ipv6 = get_request(CONFIG['ipv6check_endpoint']) if CONFIG['ipv6'] else ''

  update_cnt = 0

  for domain in CONFIG['domains']:
    records = find_records(domain[0], set(domain[1:]))
    update_cnt += update_records(domain[0], records, ip, ipv6)

  print('\nUpdated {} records'.format(update_cnt))


if __name__ == '__main__':
  main()
