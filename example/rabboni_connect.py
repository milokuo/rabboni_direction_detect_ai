import argparse
import asyncio

from rabboni_multi_python_sdk import Rabboni


async def scan_and_connect(rab: Rabboni):
    await rab.scan()
    await rab.connect_ex("F6:20:ED:F3:5B:F2")


async def print_services(rab: Rabboni):
    await asyncio.sleep(10)
    await rab.discover_services()


async def main(args: argparse.Namespace):
    rab = Rabboni(mode="BLE", debug=args.debug)
    t1 = asyncio.create_task(scan_and_connect(rab))
    t2 = asyncio.create_task(print_services(rab))
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
