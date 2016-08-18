import datetime
import pytz


class StatusMessage:
    CATEGORY_INFO = "info"
    CATEGORY_ERROR = "error"
    CATEGORY_WARNING = "warning"
    CATEGORY_SUCCESS = "success"

    def __init__(self, message, category=CATEGORY_INFO):
        self._message = message
        self._category = category
        self._timestamp = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)

    @property
    def message(self):
        return self._message

    @property
    def category(self):
        return self._category

    @property
    def timestamp(self):
        return self._timestamp


class StateUpdate(StatusMessage):
    KEY_CONNECTION_STATE = "connection_state"
    KEY_BASE_URI = "base_uri"
    KEY_DEVICE_PAGES = "number_of_device_pages"
    KEY_DEVICE_LIST = "list_of_device_ids"
    KEY_DEVICE_PAGE_LOADED = "most_recently_loaded_page_of_devices"

    STATE_CONNECTION_DISCONNECTED = 'disconnected'
    STATE_CONNECTION_CONNECTED = 'connected'
    STATE_CONNECTION_CONNECTING = 'connecting'
    STATE_CONNECTION_DISCONNECTING = 'disconnecting'
    STATE_CONNECTION_FAILED = 'failed'

    def __init__(self, message, global_state, category="info"):
        StatusMessage.__init__(self, message, category=category)
        self._global_state = global_state

    @property
    def global_state(self):
        return self._global_state


class DeviceUpdate(StatusMessage):
    def __init__(self, message, loaded_device, category="info"):
        StatusMessage.__init__(self, message, category=category)
        self._loaded_device = loaded_device

    @property
    def loaded_device(self):
        return self._loaded_device


class Command:
    # from background_commands import commands
    def __init__(self, operation, data):
        self._operation = operation
        self._data = data

    @property
    def data(self):
        return self._data

    @property
    def operation(self):
        return self._operation
