class CommandException(Exception):
    # check subclasses of this for acceptable error messages to send up
    pass


class NotConnected(CommandException):
    pass
