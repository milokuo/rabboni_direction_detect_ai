from typing import List
from dataclasses import dataclass


@dataclass
class RabboniCmd:
    length: int = 0
    command: int = 0
    data: int = 0

    def __repr__(self):
        return f'<RabboniCmd length: {self.length}, command: {self.command}, data: {self.data}>'

    @property
    def payload(self):
        cmd_init = [0x00 for i in range(33)]
        cmd_init[1] = self.length
        cmd_init[2] = self.command
        data_len = len(self.data)
        cmd_init[3:3+data_len] = self.data
        return cmd_init

    def to_bytes(self):
        return bytes(self.payload)

    def from_bytes(self, bytes_string):
        # print('from_bytes', bytes_string)
        bytes_list = list(bytes_string)
        self.length = bytes_list[0]
        self.command = bytes_list[1]
        self.data = bytes_list[2:2+self.length-1]


@dataclass
class RabboniCmdResponse:
    length: int = 0
    command: int = 0
    data: int = 0

    def __repr__(self):
        return f'<RabboniCmdResponse length: {self.length}, command: {self.command}, data: {self.data}>'

    @classmethod
    def from_bytes(cls, bytes_string):
        # print('from_bytes', bytes_string)
        bytes_list = list(bytes_string)
        resp_length = bytes_list[0]
        bytes_hex_list = ["{:02x}".format(bl) for bl in bytes_list]
        resp = cls()
        resp.length = bytes_hex_list[0]
        # resp.command = bytes_hex_list[1]
        resp.data = bytes_hex_list[1:1+resp_length]
        return resp

    @property
    def payload(self):
        return [self.command] + self.data


class RabboniCmdHelper(object):

    def __init__(self, cmd=RabboniCmd()):
        self._cmd = cmd

    def _setup_cmd(self, length: int, command: int, data: List[int]):
        self._cmd.length = length
        self._cmd.command = command
        self._cmd.data = data

    @property
    def connect_30_cmd(self):
        self._setup_cmd(0x02, 0x30, [0x0A])
        return self._cmd

    @property
    def read_config_cmd(self):
        self._setup_cmd(0x01, 0x49, [])
        return self._cmd

    @property
    def set_config_cmd(self):
        return self._cmd

    @set_config_cmd.setter
    def set_config_cmd(self, data: List[int]):
        self._setup_cmd(0x0E, 0x45, data)

    @property
    def fetch_status_48_cmd(self):
        self._setup_cmd(0x02, 0x48, [0x0A])
        return self._cmd

    @property
    def fetch_status_32_cmd(self):
        self._setup_cmd(0x02, 0x32, [0x0A])
        return self._cmd

    @property
    def reset_current_count_cmd(self):
        self._setup_cmd(0x02, 0x38, [0x0A])
        return self._cmd

    @property
    def reset_stored_count_cmd(self):
        self._setup_cmd(0x02, 0x36, [0x0A])
        return self._cmd

    @property
    def stop_cmd(self):
        self._setup_cmd(0x02, 0x33, [0x0A])
        return self._cmd

    def format_response(self, resp):
        rabboni_resp = RabboniCmdResponse.from_bytes(resp)
        # print('format_response', rabboni_resp)
        return rabboni_resp
