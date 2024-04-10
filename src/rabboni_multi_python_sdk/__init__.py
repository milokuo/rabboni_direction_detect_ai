import logging
import asyncio
import sys
print(sys.version)
from bleak import BleakScanner, BleakClient

from .command import RabboniCmdHelper
from .constants import (
    ACC_FSR_CHAR,
    GYRO_FSR_CHAR,
    DATA_RATE,
    ACC_FSR_CHAR_MAP,
    GYRO_FSR_CHAR_MAP,
    DATA_RATE_MAP,
)
from .errors import (
    DeviceNotFoundError,
    UnsupportedMacAddrError,
    UnsupportedModeError,
    DisconnectionException,
    ShutdownException,
)

logger = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s | %(levelname)s \t | %(message)s")
sh = logging.StreamHandler()
sh.setFormatter(formatter)
logger.addHandler(sh)


NOTIFY_UUID = "00001601-0000-1000-8000-00805f9b34fb"
BATTERY_UUID = "00002a19-0000-1000-8000-00805f9b34fb"
READ_CONFIG_UUID = "00001704-0000-1000-8000-00805f9b34fb"
CONFIG_UUID = "0000fff6-0000-1000-8000-00805f9b34fb"
CONFIG_NOTIFY_UUID = "0000fff7-0000-1000-8000-00805f9b34fb"
SET_CONFIG_RES_UUID = "00001705-0000-1000-8000-00805f9b34fb"


def convert_acc(acc, acc_scale, precision=3):
    x = int(acc, 16)
    x = twos_comp(x, 16)
    x = float(x)
    # print('convert_acc', acc, x, acc_scale, x*(acc_scale)/32768)
    return round(x * (acc_scale) / 32768, precision)  # x*16/32768


def convert_gyr(gyr, gyr_scale, precision=3):
    x = int(gyr, 16)
    x = twos_comp(x, 16)
    x = float(x)
    # print('convert_gyr', x, gyr_scale)
    return round(x * gyr_scale / 32768, precision)


def cal_trigger(acc_list):
    trigger_val = pow(acc_list[0], 2) + pow(acc_list[1], 2) + pow(acc_list[2], 2)
    # print(f'cal_trigger: {trigger_val}')
    return trigger_val > 2.5


def twos_comp(val, bits):
    if (val & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)  # compute negative value
    return float(val)


class Rabboni:
    def __init__(self, mode="BLE", debug=False):
        self.mode = mode
        self.ble_devices = None
        self.rab_ble_devices = []
        self.ble_client = None
        self.ble_services = []
        self.exit_flag = False
        self.reading_data = False
        self.fetch_battery = False
        self.reading_config = False
        self.setting_config = False
        self.resetting_count = False
        self._cmd_helper = RabboniCmdHelper()
        #
        self.Status = 0
        self.Accx = 0.0
        self.Accy = 0.0
        self.Accz = 0.0
        self.Gyrx = 0.0
        self.Gyry = 0.0
        self.Gyrz = 0.0
        self.Accx_list = []
        self.Accy_list = []
        self.Accz_list = []
        self.Gyrx_list = []
        self.Gyry_list = []
        self.Gyrz_list = []
        self.Cur_Cnt = 0
        self.Store_Cnt = 0
        self.Cnt_list = []
        self.Config = ""
        self.Config_Acc_Char = 0
        self.Config_Gyr_Char = 0
        self.Config_Data_Rate = 0

        if debug:
            logger.setLevel(logging.DEBUG)

    async def scan(self, verbose=False):
        self.ble_devices = await BleakScanner.discover()

        if verbose:
            logger.debug(f"Scan BLE Devices self.ble_devices={self.ble_devices}")
            return self.ble_devices
        else:
            self.rab_ble_devices = []
            for ble_device in self.ble_devices:
                if ble_device.name == "RABBONI":
                    self.rab_ble_devices.append(ble_device)
            logger.debug(f"Scan Rabboni BLE Devices = {self.rab_ble_devices}")
            return self.rab_ble_devices

    def print_device(self, verbose=True):
        if verbose:
            print(self.ble_devices)
        else:
            print(self.rab_ble_devices)

    async def connect(self, mac_address=None):
        """
        連接到指定的 BLE 裝置。
        :param mac_address: 要連接的裝置的 MAC 地址。如果未指定，則進行掃描尋找裝置。
        """
        if not mac_address:
            # 如果沒有提供 MAC 地址，則進行掃描以尋找可用的 Rabboni 裝置
            devices = await BleakScanner.discover()
            # logger.debug(f"Discovered devices: {devices}")
            for device in devices:
                if device.name is not None and "RABBONI" in device.name:
                    mac_address = device.address
                    break
            else:
                raise DeviceNotFoundError("未找到 Rabboni 裝置。")

        # 使用 BleakClient 進行連接
        self.ble_client = BleakClient(mac_address)
        try:
            await self.ble_client.connect()
            print(f"已連接到 {mac_address}")
        except Exception as e:
            print(f"連接到裝置 {mac_address} 時發生錯誤: {e}")
            raise

    async def discover_services(self):
        logger.debug(f"Discover Services: {self.ble_client.services}")
        for service in self.ble_client.services:
            logger.debug(f"Service: {service}")
            for char in service.characteristics:
                logger.debug(
                    f"\tChar: {char.uuid} (Handle: {char.handle}): {char.description}, {char.properties}"
                )
        return self.ble_services

    async def read_data(self, timeout=None):
        if not self.ble_client:
            print("Device is not connected.")
            return

        # 訂閱加速度計特徵的通知
        await self.ble_client.start_notify(NOTIFY_UUID, self._data_callback)

    async def read_config(self):
        if not self.ble_client:
            print("Device is not connected.")
            return

        # 訂閱加速度計特徵的通知
        await self.ble_client.start_notify(CONFIG_NOTIFY_UUID, self._config_callback)

        # Write the command to read the configuration
        reading_cmd = bytearray([self._cmd_helper.read_config_cmd.command])
        logger.debug(f"reading_cmd: {reading_cmd}")
        await self.ble_client.write_gatt_char(CONFIG_UUID, reading_cmd)

    async def set_config(self, acc_scale=2, gyr_scale=250, rate=10, threshold=2000):
        if not self.ble_client:
            print("Device is not connected.")
            return

        # 訂閱加速度計特徵的通知
        await self.ble_client.start_notify(CONFIG_NOTIFY_UUID, self._config_callback)

        # Write command
        config_data = [0x00 for i in range(14)]
        config_data[0:2] = [ACC_FSR_CHAR[acc_scale], GYRO_FSR_CHAR[gyr_scale]]
        config_data[3:5] = [1, 1]
        config_data[8] = DATA_RATE[rate]
        config_data[12:14] = [threshold // 256, threshold % 256]  # 2500 => [9, 196]
        self._cmd_helper.set_config_cmd = config_data
        setting_cmd = bytearray(
            [self._cmd_helper.set_config_cmd.command]
            + self._cmd_helper.set_config_cmd.data
        )
        logger.debug(f"setting_cmd: {setting_cmd}")
        await self.ble_client.write_gatt_char(CONFIG_UUID, setting_cmd)

    async def stop(self):
        if self.ble_client:
            self.reading_data = False
            await self.ble_client.stop_notify(NOTIFY_UUID)
            logger.debug(f"Done shutting down {self.name} notification.")

    async def disconnect(self):
        """Rabboni 裝置斷開連線"""
        logger.debug(f"Disconnecting to device {self.name}.")
        await self.ble_client.disconnect()
        self.ble_client = None

    ### 以下為 ex functions ###

    async def connect_ex(self, mac_address: str = None, callback=None):
        """建立 Rabboni 裝置連線"""
        if self.mode == "USB":
            pass
        elif self.mode == "BLE":
            logger.debug(f"Scanned Rabboni BLE Devices = {self.rab_ble_devices}")
            for ble_device in self.rab_ble_devices:
                # logger.warning(f"ble_device = {dir(ble_device)}")
                if ble_device.address == mac_address:
                    self.ble_client = BleakClient(
                        ble_device,
                        timeout=5.0,
                        disconnected_callback=self._disconnect_callback,
                    )
                    try:
                        logger.info(f"Connecting {self.ble_client}")
                        await self.ble_client.connect()
                        await self._notify_and_record(callback)
                    except DisconnectionException as e:
                        logger.warning(e)
                        self.exit_flag = True
                    except ShutdownException as e:
                        logger.warning(e)
                        self.exit_flag = True
                    except Exception as e:
                        logger.warning(e)
                        self.exit_flag = True
                        pass
                else:
                    raise UnsupportedMacAddrError(f"{mac_address} 為不支援的 MAC 地址")

    async def get_battery_level(self):
        """獲取 Rabboni 裝置電池狀態"""
        if self.ble_client is None:
            raise DeviceNotFoundError("No Rabboni connected.")

        self.fetch_battery = True
        data = await self.ble_client.read_gatt_char(BATTERY_UUID)
        battery_level = int(bytes(data).hex(), 16)
        logger.debug(f"battery_level: {battery_level}")
        self.fetch_battery = False
        return battery_level

    async def rst_count(self):
        """重置 Rabboni 裝置紀錄數"""
        if self.ble_client is None:
            raise DeviceNotFoundError("No Rabboni connected.")

        reset_current_cmd = bytearray(
            [self._cmd_helper.reset_current_count_cmd.command]
        )
        reset_stored_cmd = bytearray([self._cmd_helper.reset_stored_count_cmd.command])
        self.resetting_count = True
        await self.ble_client.write_gatt_char(CONFIG_UUID, reset_current_cmd)
        await self.ble_client.write_gatt_char(CONFIG_UUID, reset_stored_cmd)
        config_value = await self.ble_client.read_gatt_char(SET_CONFIG_RES_UUID)
        logger.debug(f"reset_count config_value: {config_value}")
        self.resetting_count = False
        return config_value

    async def get_sensor_config(self):
        reading_cmd = bytearray([self._cmd_helper.read_config_cmd.command])
        logger.debug(f"reading_cmd: {reading_cmd}")

        self.reading_config = True
        await self.ble_client.write_gatt_char(CONFIG_UUID, reading_cmd)
        config_value = await self.ble_client.read_gatt_char(READ_CONFIG_UUID)
        logger.debug(f"config_value: {config_value}")
        logger.debug(self._cmd_helper.format_response(config_value))
        self.reading_config = False
        return config_value

    async def set_sensor_config(
        self, acc_scale=2, gyr_scale=250, rate=10, threshold=2000
    ):
        if self.ble_client is None:
            raise DeviceNotFoundError("No Rabboni connected.")

        config_data = [0x00 for i in range(14)]
        config_data[0:2] = [ACC_FSR_CHAR[acc_scale], GYRO_FSR_CHAR[gyr_scale]]
        config_data[3:5] = [1, 1]
        config_data[8] = DATA_RATE[rate]
        config_data[12:14] = [threshold // 256, threshold % 256]  # 2500 => [9, 196]
        self._cmd_helper.set_config_cmd = config_data
        setting_cmd = bytearray(
            [self._cmd_helper.set_config_cmd.command]
            + self._cmd_helper.set_config_cmd.data
        )
        logger.debug(f"setting_cmd: {setting_cmd}")

        self.setting_config = True
        await self.ble_client.write_gatt_char(CONFIG_UUID, setting_cmd)
        config_value = await self.ble_client.read_gatt_char(SET_CONFIG_RES_UUID)
        logger.debug(f"set_sensor_config config_value: {config_value}")
        self.setting_config = False
        return config_value

    async def _notify_and_record(self, callback=None):
        logger.debug("Connected: {0}".format(self.ble_client.is_connected))
        logger.debug("Starting notification.")
        if callback is not None:
            await self.ble_client.start_notify(NOTIFY_UUID, callback)
        else:
            await self.ble_client.start_notify(NOTIFY_UUID, self._data_callback)
            await self.ble_client.start_notify(
                CONFIG_NOTIFY_UUID, self._config_callback
            )

        while not self.exit_flag:
            if self.fetch_battery:
                await self.get_battery_level()
            elif self.reading_config:
                await self.get_sensor_config()
            elif self.setting_config:
                await self.set_sensor_config()
            elif self.resetting_count:
                await self.rst_count()
            else:
                await asyncio.sleep(1)

        await self.disconnect()

    def _config_callback(self, sender, data):
        # logger.info(f"sender: {sender}, data: {data}")
        value_data = bytes(data).hex()
        # logger.info(f"config_callback sender: {sender}, value_data: {value_data}")
        self.Config = value_data
        if value_data[0:2] == "49":
            self.Config_Acc_Char = ACC_FSR_CHAR_MAP[int(value_data[2:4], 16)]
            self.Config_Gyr_Char = GYRO_FSR_CHAR_MAP[int(value_data[4:6], 16)]
            self.Config_Data_Rate = DATA_RATE_MAP[int(value_data[18:20], 16)]

    def _data_callback(self, sender, data):
        # logger.info(f"sender: {sender}, data: {data}")
        value_data = bytes(data).hex()
        # logger.info(f'rab_callback sender: {sender}, value_data: {value_data}')
        # logger.info(f'rab_callback kwargs: {kwargs}')
        self.Accx = convert_acc(value_data[:4], 2)
        self.Accy = convert_acc(value_data[4:8], 2)
        self.Accz = convert_acc(value_data[8:12], 2)
        self.Gyrx = convert_gyr(value_data[12:16], 2)
        self.Gyry = convert_gyr(value_data[16:20], 2)
        self.Gyrz = convert_gyr(value_data[20:24], 2)
        self.Cur_Cnt = int(value_data[24:28], 16)
        self.Store_Cnt = int(value_data[28:], 16)
        self.Accx_list.append(self.Accx)
        self.Accy_list.append(self.Accy)
        self.Accz_list.append(self.Accz)
        self.Gyrx_list.append(self.Gyrx)
        self.Gyry_list.append(self.Gyry)
        self.Gyrz_list.append(self.Gyrz)
        self.Cnt_list.append(self.Cur_Cnt)

        # logger.info(f"Accx: {self.Accx}, Accy: {self.Accy}, Accz: {self.Accz}")
        # logger.info(f"Curr_Cnt: {self.Cur_Cnt}, Store_Cnt: {self.Store_Cnt}")

        # trigger = cal_trigger(acc_list)
        # logger.info(f'trigger: {trigger}')
        # print(
        #     {
        #         "name": self.name,
        #         "acc": acc_list,
        #         "gyr": gyr_list,
        #         "trigger": trigger,
        #         "count": [cur_count, stored_count],
        #     }
        # )

    def _disconnect_callback(self, client):
        logger.warning(f"Client {client} got disconnected!")
        self.exit_flag = True
