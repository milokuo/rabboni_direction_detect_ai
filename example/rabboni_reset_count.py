import asyncio
import argparse

from rabboni_multi_python_sdk import Rabboni


async def scan_and_connect(rab: Rabboni):
    await rab.scan()
    await rab.connect_ex("F6:20:ED:F3:5B:F2")


async def reset(rab: Rabboni):
    await asyncio.sleep(20)
    await rab.rst_count()


async def show_count(rab: Rabboni):
    for i in range(100):
        await asyncio.sleep(1)
        if rab.ble_client is not None:
            print("(Current, Stored) = ", rab.Cur_Cnt, rab.Store_Cnt)


async def main(args: argparse.Namespace):
    rab = Rabboni(mode="BLE", debug=args.debug)
    t1 = asyncio.create_task(scan_and_connect(rab))
    t2 = asyncio.create_task(show_count(rab))
    t3 = asyncio.create_task(reset(rab))
    await t1
    await t2
    await t3


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="debug mode")
    args = parser.parse_args()
    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        print("Bye~~")
