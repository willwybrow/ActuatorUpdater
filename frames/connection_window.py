# -*- coding: utf-8 -*-
from Tkinter import Toplevel, Listbox, Button, END, BOTTOM, TOP, BOTH, SINGLE, X, Entry, Label, StringVar, W, E, NSEW
from thread_helpers.queueables import StatusMessage, StateUpdate
from settings import Site, SettingsError

from frames.widgets import AddEditDeletePanel, OkCancelPanel


class ConnectionWindow(Toplevel):
    def __init__(self, parent, site_settings):
        Toplevel.__init__(self, parent)
        self.transient(parent)

        self.parent = parent

        self._site_settings = site_settings

        self._listbox = Listbox(self, selectmode=SINGLE, height=20)
        self._listbox.pack(side=TOP, fill=BOTH, expand=1)

        self._dismiss_button_panel = OkCancelPanel(self, self.ok, self.cancel)
        self._dismiss_button_panel.pack(side=BOTTOM, fill=X)

        self._list_control_panel = AddEditDeletePanel(self, add_bind=self.open_site_editor, edit_bind=self.open_site_editor, delete_bind=self.remove_selected_site)
        self._list_control_panel.pack(side=BOTTOM, fill=X)

        self._sites = {site.url: site for site in self._site_settings.get_sites()}

        self._listbox.bind("<Double-Button-1>", self.ok)

        self.bind("<Escape>", self.cancel)

        self.populate_site_listbox()

    def populate_site_listbox(self):
        self._listbox.delete(0, END)
        for site in self._site_settings.get_sites():
            self._listbox.insert(END, u"{} — {}".format(site.url, site.key))

    def ok(self, event):
        try:
            selected_index = self._listbox.curselection()[0]
            site_to_connect = self._site_settings.get_sites()[int(selected_index)]
            self.parent.connect_to_site(site_to_connect)
            self.destroy()
        except IndexError:
            self.parent.add_status_update(StatusMessage("Please select a site to view!", category=StatusMessage.CATEGORY_ERROR))
            self._listbox.focus_get()

    def cancel(self, event):
        self.destroy()

    def open_site_editor(self, event):
        site_to_connect = None
        try:
            selected_index = self._listbox.curselection()[0]
            site_to_connect = self._site_settings.get_sites()[int(selected_index)]
        except IndexError:
            self._listbox.focus_get()
            if event.widget.cget("text") == "Edit":
                return

        child = AddEditConnectionWindow(self, site_to_connect)
        child.geometry('+200+200')
        child.grab_set()
        self.wait_window(child)

    def remove_selected_site(self, event):
        site_to_connect = None
        try:
            selected_index = self._listbox.curselection()[0]
            site_to_connect = self._site_settings.get_sites()[int(selected_index)]
            return self.remove_site(site_to_connect)
        except IndexError:
            self._listbox.focus_get()
            return

    def add_or_edit_site(self, new_site):
        # new_site = Site(url, key)
        for site in self._site_settings.get_sites():
            if site.url == new_site.url:
                self._site_settings.remove_site(site)
                break
        try:
            self._site_settings.add_site(new_site)
        except SettingsError as e:
            return None
        self.populate_site_listbox()
        return new_site

    def remove_site(self, site):
        for s in self._site_settings.get_sites():
            if s.url == site.url:
                self._site_settings.remove_site(site)
                break
        self.populate_site_listbox()


class AddEditConnectionWindow(Toplevel):
    def __init__(self, parent, site):
        Toplevel.__init__(self, parent)
        self.transient(parent)
        self.parent = parent

        self._url = StringVar()
        self._key = StringVar()

        self._url_label = Label(self, text="URL:")
        self._url_label.grid(column=0, row=0)
        self._url_entry = Entry(self, textvariable=self._url, width=50)
        self._url_entry.grid(column=1, row=0)

        self._key_label = Label(self, text="Key:")
        self._key_label.grid(column=0, row=1)
        self._key_entry = Entry(self, textvariable=self._key, width=50)
        self._key_entry.grid(column=1, row=1)

        if site is not None:
            self._url.set(site.url)
            self._key.set(site.key)

        self._cancel_button = Button(self, text="Cancel")
        self._cancel_button.bind("<Button-1>", self.cancel)
        self._cancel_button.grid(column=1, row=2, sticky=W)

        self._ok_button = Button(self, text="OK")
        self._ok_button.bind("<Button-1>", self.ok)
        self._ok_button.grid(column=0, row=2, sticky=E)

        self.bind("<Escape>", self.cancel)

    def validate(self):
        url = self._url.get().strip()
        key = self._key.get().strip()
        if len(url.strip()) == 0:
            self._url_entry.focus_set()
            return
        if len(key.strip()) == 0:
            self._key_entry.focus_set()
            return
        site = Site(url, key)
        return site

    def ok(self, event):
        site = self.validate()
        # print(site)
        if site is not None:
            site = self.parent.add_or_edit_site(site)
        if site is not None:
            self.parent.focus_set()
            self.destroy()

    def cancel(self, event):
        self.parent.focus_set()
        self.destroy()
