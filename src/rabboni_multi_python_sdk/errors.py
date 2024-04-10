class DeviceNotFoundError(Exception):
    pass


class UnsupportedMacAddrError(Exception):
    pass


class UnsupportedModeError(Exception):
    pass


class DisconnectionException(Exception):
    pass


class ShutdownException(Exception):
    pass
