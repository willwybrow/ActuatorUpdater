def get_devices(base_uri):
    if base_uri.endswith('/'):
        base_uri = base_uri.strip('/')
    return "{}/api/devices/".format(base_uri)


def get_device(base_uri, device_id):
    if base_uri.endswith('/'):
        base_uri = base_uri.strip('/')
    return "{}/api/devices/{}".format(base_uri, device_id)


def get_readings(base_uri, device_id, channel_id):
    if base_uri.endswith('/'):
        base_uri = base_uri.strip('/')
    return "{}/api/devices/{}/channels/{}/readings/".format(base_uri, device_id, channel_id)
