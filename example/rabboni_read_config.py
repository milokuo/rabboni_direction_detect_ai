import asyncio
import argparse

from rabboni_multi_python_sdk import Rabboni, convert_acc


async def scan_and_connect(rab: Rabboni):
    await rab.scan()
    # await rab.connect_ex("F6:20:ED:F3:5B:F2", callback=rabboni_callback)
    await rab.connect_ex("CA:8A:6C:38:5A:B2")


async def read_config(rab: Rabboni):
    await asyncio.sleep(5)
    value = await rab.get_sensor_config()
    print("Config: ", value)


async def main(args: argparse.Namespace):
    rab = Rabboni(mode="BLE", debug=args.debug)
    t1 = asyncio.create_task(scan_and_connect(rab))
    t2 = asyncio.create_task(read_config(rab))
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
