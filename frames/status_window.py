# -*- coding: utf-8 -*-
from Tkinter import Toplevel, Listbox, Button, END, BOTTOM, TOP, BOTH, SW, LEFT, SINGLE, X, Message


class StatusWindow(Toplevel):
    def __init__(self, parent, status_variable):
        Toplevel.__init__(self, parent)

        self.parent = parent

        self._message = Message(self, anchor=SW, justify=LEFT, textvariable=status_variable, width=9000)
        self._message.pack(fill=BOTH, expand=1)

        self.bind("<Escape>", self.cancel)
        self.protocol("WM_DELETE_WINDOW", self.kill_self)

    def cancel(self, event):
        self.parent.close_status_window()

    def kill_self(self):
        self.parent.close_status_window()
