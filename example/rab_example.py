import asyncio
import traceback
from rabboni_multi_python_sdk import Rabboni

rabo = Rabboni(mode="BLE")


async def main():
    try:
        await rabo.connect()  # 根據 MAC 地址連接 Rabboni 裝置
        await rabo.read_data()  # 開始讀取數據
        print("Connected!")

        while True:  # 持續讀取並處理數據直到手動停止
            # 根據加速度計數據判斷裝置的放置狀態
            # print("Accx: ", rabo.Accx, "Accy: ", rabo.Accy, "Accz: ", rabo.Accz)
            if rabo.Accz > 0.9:
                print("平放")
            elif rabo.Accx > 0.9:
                print("直放")
            elif rabo.Accy > 0.9:
                print("橫放")
            elif rabo.Accz < -0.9:
                print("倒平放")
            await asyncio.sleep(0.1)  # add a small delay to prevent CPU overuse
    except KeyboardInterrupt:  # 當按下 Ctrl+C 中斷程式時處理
        print('Shut down!')
    except Exception as e:  # 當發生其他例外時處理
        print(f"Error: {e}")
        traceback.print_exc()
    finally:
        await rabo.stop()

# Run the main function
asyncio.run(main())