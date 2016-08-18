import requests
import json

import background_commands.api

DEFAULT_HEADERS = {'Content-Type': 'application/json', 'Accept': 'application/json'}


def test_connection(site):

    url = site.url
    headers = DEFAULT_HEADERS.copy()
    headers.update({'X-ApiKey': site.key})

    r = requests.get(background_commands.api.get_devices(url), headers=headers)
    r.raise_for_status()

    return r.json()


def get_page_of_devices(site, page):

    url = site.url
    headers = DEFAULT_HEADERS.copy()
    headers.update({'X-ApiKey': site.key})

    r = requests.get(background_commands.api.get_devices(url), headers=headers, params={'page':page})
    r.raise_for_status()

    return r.json()


def get_device(site, device_id):

    url = site.url
    headers = DEFAULT_HEADERS.copy()
    headers.update({'X-ApiKey': site.key})

    r = requests.get(background_commands.api.get_device(url, device_id), headers=headers)
    r.raise_for_status()

    return r.json()


def get_channel_readings(site, device_id, channel_id, start_iso=None, end_iso=None):

    url = site.url
    headers = DEFAULT_HEADERS.copy()
    headers.update({'X-ApiKey': site.key})

    url_params = {}
    if start_iso is not None:
        url_params['start'] = start_iso
    if end_iso is not None:
        url_params['end'] = end_iso

    r = requests.get(background_commands.api.get_readings(url, device_id, channel_id), headers=headers, params=url_params)
    r.raise_for_status()

    return r.json()


def post_channel_reading(site, device_id, channel_id, reading_j):

    url = site.url
    headers = DEFAULT_HEADERS.copy()
    headers.update({'X-ApiKey': site.key})

    r = requests.post(background_commands.api.get_readings(url, device_id, channel_id), headers=headers, data=json.dumps(reading_j))
    r.raise_for_status()


def put_device(site, device_id, channel_j):

    url = site.url
    headers = DEFAULT_HEADERS.copy()
    headers.update({'X-ApiKey': site.key})

    r = requests.put(background_commands.api.get_device(url, device_id), headers=headers, data=json.dumps(channel_j))
    r.raise_for_status()


def delete_channel_readings(site, device_id, channel_id, start, end):

    url = site.url
    headers = DEFAULT_HEADERS.copy()
    headers.update({'X-ApiKey': site.key})

    r = requests.delete(background_commands.api.get_readings(url, device_id, channel_id), headers=headers, params={'start': start, 'end': end})
    r.raise_for_status()
