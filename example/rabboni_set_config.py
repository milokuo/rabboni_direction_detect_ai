import asyncio
import argparse

from rabboni_multi_python_sdk import Rabboni, convert_acc


async def scan_and_connect(rab: Rabboni):
    await rab.scan()
    # await rab.connect_ex("F6:20:ED:F3:5B:F2", callback=rabboni_callback)
    await rab.connect_ex("CA:8A:6C:38:5A:B2")


async def setup_config(rab: Rabboni):
    await asyncio.sleep(5)
    value = await rab.set_sensor_config(acc_scale=2, gyr_scale=250, rate=10, threshold=3000)
    print("Config set: ", value)


def rabboni_callback(sender, data):
    acc_val = 16
    value_data = bytes(data).hex()
    acc_list = [convert_acc(value_data[:4], acc_val),  convert_acc(value_data[4:8], acc_val),
                convert_acc(value_data[8:12], acc_val)]
    acc_val_x = acc_list[0]
    acc_val_y = acc_list[1]
    acc_val_z = acc_list[2]
    print({'acc_x': acc_val_x, 'acc_y': acc_val_y, 'acc_z': acc_val_z})


async def main(args: argparse.Namespace):
    rab = Rabboni(mode="BLE", debug=args.debug)
    t1 = asyncio.create_task(scan_and_connect(rab))
    t2 = asyncio.create_task(setup_config(rab))
    await t1
    await t2


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="debug mode")
    args = parser.parse_args()
    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        print("Bye~~")
