from Tkinter import LEFT, RIGHT, Y, BOTH, BOTTOM, TOP, X, NS, N, S, Menu, StringVar, Variable, Button, Listbox, SINGLE, END
from ttk import Frame, Style

import frames.widgets
import frames.connection_window
import frames.status_window
from background_commands import commands

import strings

from thread_helpers.queueables import StatusMessage, StateUpdate, Command


class ComplexVar(Variable):
    def __init__(self, *args, **kwargs):
        Variable.__init__(self, *args, **kwargs)
        self._ultra_true_var = None

    def set(self, value):
        Variable.set(self, value)
        self._ultra_true_var = value

    @property
    def ultra_true(self):
        return self._ultra_true_var


class MainWindow(Frame):

    def __init__(self, parent, command_queue, status_queue, site_settings):
        from strings import APPLICATION_NAME
        Frame.__init__(self, parent)

        self.parent = parent

        self._status_history = []
        self._history_messages = StringVar()
        self._history_window = None

        self._global_state = {
            StateUpdate.KEY_DEVICE_PAGES: StringVar(),
            StateUpdate.KEY_DEVICE_PAGE_LOADED: StringVar(),
            StateUpdate.KEY_DEVICE_LIST: ComplexVar()
        }
        self._ui_string_variables = [StateUpdate.KEY_DEVICE_PAGES, StateUpdate.KEY_DEVICE_PAGE_LOADED]
        self._ui_list_variables = [StateUpdate.KEY_DEVICE_LIST]

        self._loaded_devices = {}

        self._actuate_device_list = ComplexVar()
        self._actuate_device_list.set(tuple())

        self.parent.title(APPLICATION_NAME)
        self.style = Style()
        self.style.theme_use("default")

        self.pack(fill=BOTH, expand=1)

        self._menu_bar = Menu(self.parent)
        self.parent.config(menu=self._menu_bar)
        self._command_menu = Menu(self._menu_bar, tearoff=0)
        self._command_menu.add_command(label=strings.MENU_DISCONNECTED, command=self.open_connection_window)
        self._command_menu.add_command(label="Status message history", command=self.open_status_window)
        self._menu_bar.add_cascade(label="Connection", menu=self._command_menu)

        self._command_queue = command_queue
        self._status_queue = status_queue
        self._site_settings = site_settings

        self.status = frames.widgets.StatusBar(self)
        self.status.pack(side=BOTTOM, fill=X)
        self._status_queue.put(StatusMessage("hi all", "success"))

        self.content_frame = Frame(self)
        self.content_frame.pack(side=BOTTOM, fill=BOTH, expand=1)

        self.device_list_panel = frames.widgets.DeviceListPanel(self.content_frame, self._global_state,
                                                                self.load_all_devices, self.select_device)
        # self.device_list_panel.grid(column=0, row=0, sticky=N+S)
        self.device_list_panel.pack(side=LEFT, fill=Y)  # , expand=1)

        self.current_device_panel = frames.widgets.CurrentDevicePanel(self.content_frame, None, self.select_channel)
        # self.current_device_panel.grid(column=1, row=0)
        self.current_device_panel.pack(side=LEFT, fill=BOTH, expand=1)

        self.panel_three = Frame(self.content_frame)
        # self.panel_three.grid(column=2, row=0)
        self.panel_three.pack(side=RIGHT, fill=Y)
        self.click_to_start_button = Button(self.panel_three, text="Start actuating")
        self.click_to_start_button.pack(side=TOP)
        self.click_to_start_button.bind("<Button-1>", self.click_to_start)
        self.click_to_stop_button = Button(self.panel_three, text="Stop actuating")
        self.click_to_stop_button.pack(side=TOP)
        self.click_to_stop_button.bind("<Button-1>", self.click_to_stop)
        self.add_device_to_actuator_list_button = Button(self.panel_three, text=">>>Select device")
        self.add_device_to_actuator_list_button.pack(side=TOP)
        self.add_device_to_actuator_list_button.bind("<Button-1>", self.add_device_to_actuator_list)
        self.delete_device_from_actuator_list_button = Button(self.panel_three, text="<<<Deselect device")
        self.delete_device_from_actuator_list_button.pack(side=TOP)
        self.delete_device_from_actuator_list_button.bind("<Button-1>", self.delete_device_from_actuator_list)
        self.actuator_list = Listbox(self.panel_three, selectmode=SINGLE, height=20, exportselection=0, listvariable=self._actuate_device_list)
        self.actuator_list.pack(side=TOP, expand=1, fill=X)

        self.consume_status_updates()

        self.parent.bind("<Escape>", self._quit)

    def add_device_to_actuator_list(self, event):
        device = self.get_current_device()
        if device is not None and device not in self._actuate_device_list.ultra_true:
            self._actuate_device_list.set(tuple(list(self._actuate_device_list.ultra_true) + [device]))

    def delete_device_from_actuator_list(self, event):
        try:
            # print self.actuator_list.curselection()
            selected_index = int(self.actuator_list.curselection()[0])
            self._actuate_device_list.set(tuple(list(self._actuate_device_list.ultra_true)[:selected_index] + list(self._actuate_device_list.ultra_true)[selected_index+1:]))
            # self.actuator_list.delete(selected_index)
        except Exception as e:
            # print e
            pass

    def record_status_history(self, status):
        self._status_history.append(status)
        self._history_messages.set("\n".join(["{}:\t{}".format(s.timestamp.isoformat(), s.message) for s in self._status_history]))

    def load_all_devices(self, *args, **kwargs):
        self.add_status_update(StatusMessage("Loading device list!"))
        self.issue_command(Command(commands.load_device_list, None))

    def select_device(self, event):
        # print("Selecting device...")
        listbox = event.widget
        try:
            selected_index = listbox.curselection()[0]
            device_list = self._global_state[StateUpdate.KEY_DEVICE_LIST].ultra_true
            device = device_list[int(selected_index)]
            # print("Selected device {}".format(device.device_id))
            self.view_device(device)
        # except IndexError:
        #     listbox.focus_get()
        except Exception as e:
            # print e
            pass

    def click_to_start(self, event):
        self.issue_command(Command(commands.start_actuating, [(d if d.device_id not in self._loaded_devices else self._loaded_devices[d.device_id]) for d in self._actuate_device_list.ultra_true]))

    def click_to_stop(self, event):
        self.issue_command(Command(commands.stop_actuating, None))

    def select_channel(self, event):
        # print("Selecting channel...")
        listbox = event.widget
        # load channel values

    def view_device(self, device):
        if device is None:
            self.current_device_panel.switch_to_device(None)
        elif device.device_id not in self._loaded_devices:
            self.add_status_update(StatusMessage("Loading device {}".format(device.device_id)))
            self.issue_command(Command(commands.load_device, device.device_id))
            self.current_device_panel.switch_to_device(device)
        else:
            self.current_device_panel.switch_to_device(self._loaded_devices[device.device_id])

    def get_current_device(self):
        device = self.current_device_panel.get_current_device()
        return device

    def open_connection_window(self):
        if (StateUpdate.KEY_CONNECTION_STATE not in self._global_state or
                self._global_state[StateUpdate.KEY_CONNECTION_STATE] == StateUpdate.STATE_CONNECTION_DISCONNECTED or
                self._global_state[StateUpdate.KEY_CONNECTION_STATE] == StateUpdate.STATE_CONNECTION_FAILED):
            self.modal(frames.connection_window.ConnectionWindow(self, self._site_settings))
        elif self._global_state[StateUpdate.KEY_CONNECTION_STATE] == StateUpdate.STATE_CONNECTION_CONNECTED:
            self.disconnect_from_site()

    def open_status_window(self):
        if self._history_window is None:
            self._history_window = frames.status_window.StatusWindow(self, self._history_messages)

    def close_status_window(self):
        self._history_window.destroy()
        self._history_window = None

    def issue_command(self, command):
        if not isinstance(command, Command):
            raise Exception("Can't issue this command!")
        self._command_queue.put(command)

    def add_status_update(self, status_message):
        if not isinstance(status_message, StatusMessage):
            raise Exception("Can't message this!")
        self._status_queue.put(status_message)

    def modal(self, child, geometry='500x700+200+200'):
        child.geometry(geometry)
        child.transient(self)
        child.grab_set()
        self.wait_window(child)
        return child

    def consume_status_updates(self):
        import Queue
        while not self._status_queue.empty():
            try:
                status = self._status_queue.get()
                self.record_status_history(status)
                if hasattr(status, 'global_state'):
                    self.update_global_state(status.global_state)
                if hasattr(status, 'loaded_device'):
                    # print("A device has been loaded in the background!")
                    self.update_loaded_device(status.loaded_device)
                self.status.set("%s", status.message)
            except Queue.Empty:
                break
        self.after(100, self.consume_status_updates)

    def connect_to_site(self, site):
        self.add_status_update(StatusMessage("Connecting to {}".format(site.url)))
        self.update_global_state({StateUpdate.KEY_CONNECTION_STATE: StateUpdate.STATE_CONNECTION_CONNECTING})
        self.issue_command(Command(commands.connect_to_site, site))

    def disconnect_from_site(self):
        # self.device_list_panel.list_box_with_scroll_bar_panel.list_box.delete(0, END)
        self.click_to_stop(None)  # stop actuating
        self.issue_command(Command(commands.disconnect_from_site, None))
        self.view_device(None)
        self._actuate_device_list.set(tuple())
        self.update_global_state({StateUpdate.KEY_CONNECTION_STATE: StateUpdate.STATE_CONNECTION_DISCONNECTED,
                                  StateUpdate.KEY_DEVICE_LIST: tuple()})
        # self.parent.file_new(self.parent)

    def update_global_state(self, global_state):
        if global_state is not None:
            keys_to_delete = [k for k,v in global_state.iteritems() if v is None]
            for key_to_delete in keys_to_delete:
                if key_to_delete in self._ui_string_variables:
                    self._global_state[key_to_delete] = ""
                elif key_to_delete in self._ui_list_variables:
                    self._global_state[key_to_delete] = tuple([])
                elif key_to_delete in self._global_state.keys():
                    del self._global_state[key_to_delete]
            keys_to_keep = [k for k,v in global_state.iteritems() if v is not None]
            for key_to_keep in keys_to_keep:
                if key_to_keep in self._ui_string_variables:
                    self._global_state[key_to_keep].set(global_state[key_to_keep])
                elif key_to_keep in self._ui_list_variables:
                    self._global_state[key_to_keep].set(tuple(global_state[key_to_keep]))
                else:
                    self._global_state[key_to_keep] = global_state[key_to_keep]
        """
        if StateUpdate.KEY_CONNECTION_STATE not in self._global_state or self._global_state[StateUpdate.KEY_CONNECTION_STATE] in [StateUpdate.STATE_CONNECTION_FAILED, StateUpdate.STATE_CONNECTION_DISCONNECTED]:
            try:
                self._menu_bar.entryconfig(strings.MENU_DISCONNECTED, state="normal")
            except Exception as e:
                print e
        else:
            try:
                # self._menu_bar.entryconfig(strings.MENU_DISCONNECTED, state="disabled")
                self._menu_bar.entryconfig(strings.MENU_DISCONNECTED, state="disabled")
            except Exception as e:
                print e

        """
        # print self._global_state

    def update_loaded_device(self, loaded_device):
        # print(loaded_device.__repr__())
        self._loaded_devices[loaded_device.device_id] = loaded_device
        self.current_device_panel.loaded_device(loaded_device)

    def _quit(self, event):
        self.issue_command(Command(commands.shut_down_command_thread, None))
        try:
            self._site_settings.write_to_file()
        except:
            pass
        self.parent.destroy()
