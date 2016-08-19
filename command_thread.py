from threading import Thread
import Queue
from thread_helpers.queueables import StateUpdate, StatusMessage, DeviceUpdate
from background_commands import connection, exceptions
import requests

from hub.entities import Device, Channel


class ActuatingThread(Thread):
    def __init__(self, site, status_queue, device_list):
        Thread.__init__(self)
        self._quitting = False
        self._device_list = device_list
        self._exclude_because_of_errors = []
        self._site = site
        self._status_queue = status_queue
        self._status_queue.put(StatusMessage("Actuating Thread initialised!"))

        self._actuator_list = []

    def quit(self):
        self._status_queue.put(StatusMessage("Actuator thread should quit..."))
        self._quitting = True

    def is_quitting(self):
        return self._quitting

    def run(self):
        self._status_queue.put(StatusMessage("Actuator initialised! Monitoring {} devices...".format(len(self._device_list) if self._device_list is not None else 0)))
        while not self._quitting:
            if self._device_list is None:
                device_list = []
                page = 0
                max_pages = 1
                try:
                    while page < max_pages:
                        page += 1
                        # self._status_queue.put(StatusMessage("Loading device page {}/{}".format(page, max_pages)))
                        devices_and_pagination = connection.get_page_of_devices(self._site, page)
                        if 'pagination' in devices_and_pagination:
                            if 'last' in devices_and_pagination['pagination']:
                                max_pages = devices_and_pagination['pagination']['last']
                            if 'devices' in devices_and_pagination:
                                device_list.extend(
                                    [Device(d['id'], d['name']) for d in devices_and_pagination['devices']])
                                if 'page' in devices_and_pagination['pagination']:
                                    page = devices_and_pagination['pagination']['page']
                        new_global_state = {StateUpdate.KEY_DEVICE_PAGE_LOADED: page,
                                            StateUpdate.KEY_DEVICE_PAGES: max_pages,
                                            StateUpdate.KEY_DEVICE_LIST: device_list}
                        state_update = StateUpdate("Loaded {} device(s)!".format(len(device_list)), new_global_state,
                                                   category=StatusMessage.CATEGORY_SUCCESS)
                        self._status_queue.put(state_update)
                    self._device_list = device_list
                except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
                    state_update = StateUpdate("Failed to connect to {}: {}".format(self._site.url, e),
                                               {StateUpdate.KEY_CONNECTION_STATE:
                                                StateUpdate.STATE_CONNECTION_FAILED},
                                               category=StatusMessage.CATEGORY_ERROR)
                    self._status_queue.put(state_update)
                except AttributeError as e:
                    state_update = StateUpdate("Failed to connect: {}".format(e),
                                               {StateUpdate.KEY_CONNECTION_STATE:
                                                StateUpdate.STATE_CONNECTION_FAILED},
                                               category=StatusMessage.CATEGORY_ERROR)
                    self._status_queue.put(state_update)
                except exceptions.NotConnected as e:
                    state_update = StateUpdate("Failed: {}".format(e),
                                               {StateUpdate.KEY_CONNECTION_STATE:
                                                StateUpdate.STATE_CONNECTION_DISCONNECTED},
                                               category=StatusMessage.CATEGORY_ERROR)
                    self._status_queue.put(state_update)
            device_list = []
            for device in self._device_list:
                device_id = device.device_id
                if self._quitting:
                    break
                if device_id in self._exclude_because_of_errors:
                    continue
                if not device.loaded:
                    try:
                        j_dev = connection.get_device(self._site, device_id)
                        device = Device(j_dev['id'], j_dev.get('name', j_dev['id']))
                        channels = []
                        for j_chan in j_dev.get('channels', []):
                            channels.append(Channel(j_chan['id'], device, current_value=j_chan.get('currentValue'),
                                                    last_updated=j_chan.get('updatedAt')))
                        device.channels = channels
                        device_update = DeviceUpdate("Loaded device {}".format(device_id), device)
                        self._status_queue.put(device_update)
                    except KeyError as e:
                        status_update = StatusMessage("Failed: {}".format(e), category=StatusMessage.CATEGORY_ERROR)
                        self._status_queue.put(status_update)
                j_put = {'id': device.device_id, 'name': device.device_name}
                dt_bounds = {}
                for channel in device.channels:
                    channel_id = channel.channel_id
                    if channel_id.startswith("Actuator-8"):
                        try:
                            j_read = connection.get_channel_readings(self._site, device_id, channel_id)
                            if 'datapoints' in j_read and len(j_read['datapoints']):
                                for dp in sorted(j_read['datapoints'], key=lambda x: x['at']):
                                    if 'channels' not in j_put:
                                        j_put['channels'] = []
                                    if channel_id not in dt_bounds:
                                        dt_bounds[channel_id] = {'max': dp['at'], 'min': dp['at']}
                                    else:
                                        dt_bounds[channel_id]['max'] = max(dt_bounds[channel_id]['max'], dp['at'])
                                        dt_bounds[channel_id]['min'] = max(dt_bounds[channel_id]['min'], dp['at'])
                                    # try:
                                    #     connection.post_channel_reading(self._site, device_id, channel_id.replace("Actuator-8", "Sensor-0"), dp)
                                    # except Exception as e:
                                    #     print e
                                    self._status_queue.put(StatusMessage("Discovered pending actuator write {}".format(dp)))
                                    dp['id'] = channel_id.replace("Actuator-8", "Sensor-0")
                                    j_put['channels'].append(dp)
                        except Exception as e:
                            # self._exclude_because_of_errors.append(device.device_id)  # to add in future
                            # "It will be skipped in future!"
                            self._status_queue.put(StatusMessage("Error actuating device {}: {}.".format(device_id, e)))
                            break
                if 'channels' in j_put and len(j_put['channels']) > 0:
                    self._status_queue.put(StatusMessage("Doing a PUT device:\n{}".format(j_put)))
                    connection.put_device(self._site, device_id, j_put)
                for channel_id, bounds in dt_bounds.iteritems():
                    self._status_queue.put(StatusMessage("Deleting readings for channel {}:{} from {} to {}".format(device_id, channel_id, bounds['min'], bounds['max'])))
                    connection.delete_channel_readings(self._site, device_id, channel_id, bounds['min'], bounds['max'])
                device_list.append(device)
            self._device_list = device_list
        self._status_queue.put(StatusMessage("Actuating Thread terminated!"))


class CommandThread(Thread):
    def __init__(self, command_queue, status_queue):
        Thread.__init__(self)
        self._command_queue = command_queue
        self._status_queue = status_queue
        self._quitting = False

        self._site = None
        self._actuating = False
        self._actuating_thread = None

        self._device_list = None

    def quit(self):
        self._quitting = True

    def run(self):
        # print("Launching background thread!")
        while not self._quitting:
            if self._site is not None:
                if self._actuating:
                    if self._actuating_thread is None or not self._actuating_thread.isAlive():
                        self._status_queue.put(StatusMessage("Actuating Thread should be running but it's not!"))
                        self._actuating_thread = ActuatingThread(self._site, self._status_queue, self._device_list)
                        self._actuating_thread.daemon = True
                        self._actuating_thread.start()
                else:
                    if self._actuating_thread is not None and self._actuating_thread.isAlive() and not self._actuating_thread.is_quitting():
                        self._status_queue.put(StatusMessage("Telling the Actuating Thread to quit!"))
                        self._actuating_thread.quit()
            while not self._command_queue.empty():
                try:
                    command = self._command_queue.get()
                    self.parse_and_execute_command(command)
                except Queue.Empty as e:
                    break
                except Exception as e:
                    self._status_queue.put(StatusMessage("Exception on command {}".format(e)))

    def message_ui_thread(self, status):
        self._status_queue.put(status)

    @property
    def site(self):
        return self._site

    @site.setter
    def site(self, site):
        self._site = site

    @property
    def device_list(self):
        return self._device_list

    @device_list.setter
    def device_list(self, device_list):
        self._device_list = device_list

    def start_actuating(self):
        if self._actuating is False:
            self._status_queue.put(StatusMessage("Starting actuator thread now!"))
            self._actuating = True

    def stop_actuating(self):
        if self._actuating:
            self._status_queue.put(StatusMessage("Stopping actuator thread now!"))
            self._actuating = False

    def parse_and_execute_command(self, command):
        from background_commands import exceptions
        try:
            result_status = command.operation(self, command.data)
            if result_status is not None:
                self.message_ui_thread(result_status)
        except exceptions.CommandException as e:
            error_status = StatusMessage("Error in command: {}".format(e), StatusMessage.CATEGORY_ERROR)
            self.message_ui_thread(error_status)
