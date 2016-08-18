from frames.main_window import MainWindow
from command_thread import CommandThread

from threading import Thread
from Queue import Queue
from settings import site_settings

from Tkinter import Tk, TOP, BOTH
from ttk import Style


def main():
    command_queue = Queue()
    status_queue = Queue()

    def file_new(r):
        if hasattr(r, "app"):
            r.app.destroy()
        r.app = MainWindow(root, command_queue, status_queue, site_settings)
        r.app.pack(side=TOP, fill=BOTH, expand=1)

    root = Tk()
    root.style = Style()
    # win: ('winnative', 'clam', 'alt', 'default', 'classic', 'xpnative')
    # ('clam', 'alt', 'default', 'classic')
    root.style.theme_use("classic")
    root.geometry("800x600+300+300")
    root.file_new = file_new
    file_new(root)
    # root.app = MainWindow(root, command_queue, status_queue, site_settings)
    # root.app.pack(side=TOP, fill=BOTH, expand=1)

    command_thread = CommandThread(command_queue, status_queue)
    # command_thread = Thread(target=ct.run)
    command_thread.daemon = True

    command_thread.start()

    root.mainloop()

    command_thread.quit()
    command_thread.join()

    print("Exiting...")


if __name__ == '__main__':
    main()
