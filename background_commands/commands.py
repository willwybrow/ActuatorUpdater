# all commands here must take the following parameters
from thread_helpers.queueables import StateUpdate, StatusMessage, DeviceUpdate
from background_commands import exceptions


def no_op(command_thread, data):
    return StatusMessage("No operation", category=StatusMessage.CATEGORY_INFO)


def shut_down_command_thread(command_thread, data):
    command_thread.site = None
    command_thread.quit()


def disconnect_from_site(command_thread, data):
    command_thread.site = None
    new_global_state = {StateUpdate.KEY_CONNECTION_STATE: StateUpdate.STATE_CONNECTION_DISCONNECTED}
    state_update = StateUpdate("Disconnected!", new_global_state, category=StatusMessage.CATEGORY_SUCCESS)
    return state_update


def connect_to_site(command_thread, site):
    from background_commands import connection
    from hub.entities import Device
    import requests

    command_thread.message_ui_thread(StatusMessage("Attempting to connect...", category=StatusMessage.CATEGORY_INFO))
    try:
        devices_and_pagination = connection.test_connection(site)
        new_global_state = {StateUpdate.KEY_CONNECTION_STATE: StateUpdate.STATE_CONNECTION_CONNECTED}
        if 'pagination' in devices_and_pagination:
            if 'last' in devices_and_pagination['pagination']:
                new_global_state[StateUpdate.KEY_DEVICE_PAGES] = devices_and_pagination['pagination']['last']
            if 'devices' in devices_and_pagination:
                new_global_state[StateUpdate.KEY_DEVICE_LIST] = [Device(d['id'], d['name']) for d in
                                                                 devices_and_pagination['devices']]
                if 'page' in devices_and_pagination['pagination']:
                    new_global_state[StateUpdate.KEY_DEVICE_PAGE_LOADED] = devices_and_pagination['pagination'][
                        'page']
        command_thread.site = site
        state_update = StateUpdate("Connected to {}!".format(site.url), new_global_state,
                                   category=StatusMessage.CATEGORY_SUCCESS)
        return state_update
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
        state_update = StateUpdate("Failed to connect to {}: {}".format(site.url, e),
                                   {StateUpdate.KEY_CONNECTION_STATE:
                                        StateUpdate.STATE_CONNECTION_FAILED},
                                   category=StatusMessage.CATEGORY_ERROR)
        command_thread.message_ui_thread(state_update)
    except AttributeError as e:
        state_update = StateUpdate("Failed to connect: {}".format(e),
                                   {StateUpdate.KEY_CONNECTION_STATE:
                                        StateUpdate.STATE_CONNECTION_FAILED},
                                   category=StatusMessage.CATEGORY_ERROR)
        command_thread.message_ui_thread(state_update)


def load_device_list(command_thread, data):
    from background_commands import connection
    from hub.entities import Device
    import requests

    if command_thread.site is None:
        raise exceptions.NotConnected("Not connected to a site!")
    command_thread.message_ui_thread(StatusMessage("Loading device list...", category=StatusMessage.CATEGORY_INFO))
    page = 0
    max_pages = 1
    try:
        device_list = []
        while page < max_pages:
            page += 1
            command_thread.message_ui_thread(StatusMessage("Loading device page {}/{}".format(page, max_pages)))
            devices_and_pagination = connection.get_page_of_devices(command_thread.site, page)
            if 'pagination' in devices_and_pagination:
                if 'last' in devices_and_pagination['pagination']:
                    max_pages = devices_and_pagination['pagination']['last']
                if 'devices' in devices_and_pagination:
                    device_list.extend([Device(d['id'], d['name']) for d in devices_and_pagination['devices']])
                    if 'page' in devices_and_pagination['pagination']:
                        page = devices_and_pagination['pagination']['page']
            new_global_state = {StateUpdate.KEY_DEVICE_PAGE_LOADED: page,
                                StateUpdate.KEY_DEVICE_PAGES: max_pages,
                                StateUpdate.KEY_DEVICE_LIST: device_list}
            state_update = StateUpdate("Loaded {} device(s)!".format(len(device_list)), new_global_state,
                                       category=StatusMessage.CATEGORY_SUCCESS)
            command_thread.message_ui_thread(state_update)
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
        state_update = StateUpdate("Failed to connect to {}: {}".format(command_thread.site.url, e),
                                   {StateUpdate.KEY_CONNECTION_STATE:
                                        StateUpdate.STATE_CONNECTION_FAILED},
                                   category=StatusMessage.CATEGORY_ERROR)
        command_thread.message_ui_thread(state_update)
    except AttributeError as e:
        state_update = StateUpdate("Failed to connect: {}".format(e),
                                   {StateUpdate.KEY_CONNECTION_STATE:
                                        StateUpdate.STATE_CONNECTION_FAILED},
                                   category=StatusMessage.CATEGORY_ERROR)
        command_thread.message_ui_thread(state_update)
    except exceptions.NotConnected as e:
        state_update = StateUpdate("Failed: {}".format(e),
                                   {StateUpdate.KEY_CONNECTION_STATE:
                                        StateUpdate.STATE_CONNECTION_DISCONNECTED},
                                   category=StatusMessage.CATEGORY_ERROR)
        command_thread.message_ui_thread(state_update)


def load_device(command_thread, data):
    from background_commands import connection
    from hub.entities import Device, Channel
    if command_thread.site is None:
        raise exceptions.NotConnected("Not connected to a site!")
    device_id = data
    try:
        j_dev = connection.get_device(command_thread.site, device_id)
        device = Device(j_dev['id'], j_dev.get('name', j_dev['id']))
        channels = []
        for j_chan in j_dev.get('channels', []):
            channels.append(Channel(j_chan['id'], device, current_value=j_chan.get('currentValue'),
                                    last_updated=j_chan.get('updatedAt')))
        device.channels = channels
        device_update = DeviceUpdate("Loaded device {}".format(device_id), device)
        return device_update
    except KeyError as e:
        status_update = StatusMessage("Failed: {}".format(e), category=StatusMessage.CATEGORY_ERROR)
        command_thread.message_ui_thread(status_update)


def start_actuating(command_thread, data):
    command_thread.device_list = data
    command_thread.start_actuating()


def stop_actuating(command_thread, data):
    command_thread.device_list = None
    command_thread.stop_actuating()