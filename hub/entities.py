class Device(object):
    def __init__(self, device_id, device_name, channels=[], loaded=False):
        self._device_id = device_id
        self._device_name = device_name
        self._channels = channels
        self._loaded = loaded

    @staticmethod
    def blank_string_for_nones(value):
        return value if value is not None else ""

    @property
    def device_id(self):
        return self._device_id

    @property
    def device_name(self):
        return self._device_name

    @property
    def channels(self):
        return self._channels

    @channels.setter
    def channels(self, channels):
        self._loaded = True
        self._channels = [c for c in channels if c.device_id == self._device_id]

    @property
    def loaded(self):
        return self._loaded

    @loaded.setter
    def loaded(self, loaded):
        self._loaded = loaded

    @property
    def channel_ids(self):
        return [Device.blank_string_for_nones(c.channel_id) for c in sorted(self.channels, key=lambda x: x.channel_id)]

    @property
    def channel_values(self):
        return [Device.blank_string_for_nones(c.current_value) for c in sorted(self.channels, key=lambda x: x.channel_id)]

    @property
    def channel_timestamps(self):
        return [Device.blank_string_for_nones(c.last_updated) for c in sorted(self.channels, key=lambda x: x.channel_id)]

    def __str__(self):
        return self._device_id

    def __repr__(self):
        return "Device(\"{}\", \"{}\", {}, loaded={})".format(self._device_id, self._device_name, self.channels, self.loaded)


class Channel(object):
    def __init__(self, channel_id, device, current_value=None, last_updated=None):
        self._channel_id = channel_id
        self._device = device
        self._current_value = current_value
        self._last_updated = last_updated

    @property
    def channel_id(self):
        return self._channel_id

    @property
    def device_id(self):
        return self._device.device_id

    @property
    def device(self):
        return self.device

    @property
    def current_value(self):
        return self._current_value

    @property
    def last_updated(self):
        return self._last_updated

    def __str__(self):
        return "Channel<{}:{}>".format(self._device.device_id, self._channel_id)

    def __repr__(self):
        return "Channel(\"{}\", \"{}\")".format(self._device.device_id, self._channel_id)