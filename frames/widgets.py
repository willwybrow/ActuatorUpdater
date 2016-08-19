from Tkinter import SUNKEN, X, Y, E, W, LEFT, RIGHT, BOTH, VERTICAL, BOTTOM, TOP, EW, SINGLE, END, Listbox, Scrollbar
from ttk import Frame, Label, Button
from thread_helpers.queueables import StateUpdate


class StatusBar(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self, relief=SUNKEN, anchor=W)
        self.label.pack(fill=X)

    def set(self, fmt, *args):
        self.label.config(text=fmt % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()


class AddEditDeletePanel(Frame):

    def __init__(self, master, add_bind=None, edit_bind=None, delete_bind=None):
        Frame.__init__(self, master)
        self.add_button = Button(self, text="Add")
        self.add_button.pack(side=LEFT, expand=1, fill=X)
        if add_bind is not None:
            self.add_button.bind("<Button-1>", add_bind)
        self.edit_button = Button(self, text="Edit")
        self.edit_button.pack(side=LEFT, expand=1, fill=X)
        if edit_bind is not None:
            self.edit_button.bind("<Button-1>", edit_bind)
        self.delete_button = Button(self, text="Delete")
        self.delete_button.pack(side=LEFT, expand=1, fill=X)
        if delete_bind is not None:
            self.delete_button.bind("<Button-1>", delete_bind)


class OkCancelPanel(Frame):

    def __init__(self, master, ok_bind=None, cancel_bind=None):
        Frame.__init__(self, master)
        self.cancel_button = Button(self, text="Cancel")
        self.cancel_button.pack(side=RIGHT)
        if cancel_bind is not None:
            self.cancel_button.bind("<Button-1>", cancel_bind)
        self.ok_button = Button(self, text="OK")
        self.ok_button.pack(side=RIGHT)
        if ok_bind is not None:
            self.ok_button.bind("<Button-1>", ok_bind)


class DeviceListPanel(Frame):
    def __init__(self, master, global_state, load_devices_bind, list_box_bind):
        Frame.__init__(self, master)

        """
        TODO: create a frame with a label and button, pack it on the bottom filling X
        The button loads the next page, or maybe the rest of the pages, the label says
        loaded x/y pages

        Next, create a frame and pack it with a scrollbar and a listbox. use the guide
        from here: http://effbot.org/tkinterbook/listbox.htm to create the scrollbar's
        power over the listbox.

        """

        self.list_box_with_scroll_bar_panel = ListBoxWithScrollBarPanel(self, global_state, list_box_bind)
        self.list_box_with_scroll_bar_panel.pack(side=TOP, fill=BOTH, expand=1)
        self.page_indicator_panel = PageIndicatorPanel(self, global_state, load_devices_bind)
        self.page_indicator_panel.pack(side=TOP, fill=X)


class ListBoxWithScrollBarPanel(Frame):
    def __init__(self, master, global_state, list_box_bind):
        Frame.__init__(self, master)

        self.scroll_bar = Scrollbar(self, orient=VERTICAL)
        self.list_box = Listbox(self, yscrollcommand=self.scroll_bar.set, listvariable=global_state[StateUpdate.KEY_DEVICE_LIST], selectmode=SINGLE, height=20)
        self.list_box.bind("<<ListboxSelect>>", list_box_bind)
        self.scroll_bar.config(command=self.list_box.yview)
        self.scroll_bar.pack(side=RIGHT, fill=Y)
        self.list_box.pack(side=RIGHT, fill=BOTH, expand=1)


class PageIndicatorPanel(Frame):
    def __init__(self, master, global_state, load_devices_bind):
        Frame.__init__(self, master)

        self.page_label = Label(self, text="Page:")
        self.current_page_label = Label(self, textvariable=global_state[StateUpdate.KEY_DEVICE_PAGE_LOADED])
        self.slash_label = Label(self, text="/")
        self.max_pages_label = Label(self, textvariable=global_state[StateUpdate.KEY_DEVICE_PAGES])

        self.page_label.pack(side=LEFT)
        self.current_page_label.pack(side=LEFT)
        self.slash_label.pack(side=LEFT)
        self.max_pages_label.pack(side=LEFT)

        self.load_remaining_devices_button = Button(self, text="Load all")
        self.load_remaining_devices_button.bind("<Button-1>", load_devices_bind)
        self.load_remaining_devices_button.pack(side=RIGHT)


class TripleListBoxWithScrollBarPanel(Frame):
    def __init__(self, master, list_box_bind):
        Frame.__init__(self, master)

        self.common_bind = list_box_bind

        self.scroll_bar = Scrollbar(self, orient=VERTICAL)
        self.list_box_channel_id = Listbox(self, yscrollcommand=self.sync_yview_id, selectmode=SINGLE, height=20, exportselection=0)
        self.list_box_channel_id.bind("<<ListboxSelect>>", self.sync_selection)

        self.list_box_channel_value = Listbox(self, yscrollcommand=self.sync_yview_value, selectmode=SINGLE, height=20, exportselection=0)
        self.list_box_channel_value.bind("<<ListboxSelect>>", self.sync_selection)

        self.list_box_channel_timestamp = Listbox(self, yscrollcommand=self.sync_yview_timestamp, selectmode=SINGLE, height=20, exportselection=0)
        self.list_box_channel_timestamp.bind("<<ListboxSelect>>", self.sync_selection)
        self.scroll_bar.config(command=self.sync_scroll)
        self.scroll_bar.pack(side=RIGHT, fill=Y)
        self.list_box_channel_timestamp.pack(side=RIGHT, fill=BOTH, expand=1)
        self.list_box_channel_value.pack(side=RIGHT, fill=BOTH, expand=1)
        self.list_box_channel_id.pack(side=RIGHT, fill=BOTH, expand=1)

    def sync_scroll(self, *args):
        apply(self.list_box_channel_id.yview, args)
        apply(self.list_box_channel_value.yview, args)
        apply(self.list_box_channel_timestamp.yview, args)

    def set_scroll_bar(self, *args):
        self.scroll_bar.set(*args)

    def sync_listbox_yview(self, source_listbox=None, *args):
        if source_listbox is None:
            return
        for l in [self.list_box_channel_id, self.list_box_channel_value, self.list_box_channel_timestamp]:
            if source_listbox.yview() != l.yview():
                l.yview_moveto(*args)

    def sync_yview_id(self, *args):
        for l in [self.list_box_channel_value, self.list_box_channel_timestamp]:
            if self.list_box_channel_id.yview() != l.yview():
                l.yview_moveto(args[0])
        self.set_scroll_bar(*args)

    def sync_yview_value(self, *args):
        for l in [self.list_box_channel_id, self.list_box_channel_timestamp]:
            if self.list_box_channel_value.yview() != l.yview():
                l.yview_moveto(args[0])
        self.set_scroll_bar(*args)

    def sync_yview_timestamp(self, *args):
        for l in [self.list_box_channel_value, self.list_box_channel_id]:
            if self.list_box_channel_timestamp.yview() != l.yview():
                l.yview_moveto(args[0])
        self.set_scroll_bar(*args)

    def sync_selection(self, event):
        for listbox in [self.list_box_channel_id, self.list_box_channel_value, self.list_box_channel_timestamp]:
            if listbox == event.widget:
                pass
            else:
                try:
                    selected_index = int(event.widget.curselection()[0])
                    listbox.selection_clear(0, END)
                    listbox.selection_set(selected_index)
                    listbox.activate(selected_index)
                except (IndexError, ValueError) as e:
                    pass
        self.common_bind(event)


class CurrentDevicePanel(Frame):
    def __init__(self, master, device, list_box_bind):
        Frame.__init__(self, master)

        self._device = device

        self.label_device_id = Label(self, text="Your device will load here")
        self.label_device_id.pack(side=TOP, fill=X)

        self.tri_panel = TripleListBoxWithScrollBarPanel(self, list_box_bind)
        self.tri_panel.pack(side=TOP, fill=BOTH, expand=1)

    def get_current_device(self):
        return self._device

    def switch_to_device(self, device):
        # Note: device may not be loaded!
        self._device = device
        try:
            self.populate_fields_from_device()
        except (AttributeError, KeyError, NameError) as e:
            pass  # print e

    def populate_fields_from_device(self):
        # print("using {}".format(self._device.__repr__()))
        self.label_device_id.config(text="")
        self.tri_panel.list_box_channel_id.delete(0, END)
        self.tri_panel.list_box_channel_value.delete(0, END)
        self.tri_panel.list_box_channel_timestamp.delete(0, END)

        if self._device is not None:
            self.label_device_id.config(text="{} has {} channels".format(self._device.device_id, len(self._device.channels)))
            self.tri_panel.list_box_channel_id.insert(END, *self._device.channel_ids)
            self.tri_panel.list_box_channel_value.insert(END, *self._device.channel_values)
            self.tri_panel.list_box_channel_timestamp.insert(END, *self._device.channel_timestamps)

    def loaded_device(self, device):
        # print("A device has been loaded")
        # print("If this device {} is currently on-screen, we need to update all our fields right away".format(device))
        if self._device is not None and device.device_id == self._device.device_id:
            # print("It is!")
            # print("New device has channels:")
            # print(device.channels)
            # print("Old device has channels:")
            # print(self._device.channels)
            # print("Previous device = {}. \nnew device = {}".format(self._device.__repr__(), device.__repr__()))
            self._device = device
            # print(self._device.channels)
            self.populate_fields_from_device()
