import asyncio
import traceback
from rabboni_multi_python_sdk import Rabboni

rabo1 = Rabboni(mode="USB")
rabo2 = Rabboni(mode="BLE")

async def main():
    try:
        rabo1.connect()  # 根據 MAC 地址連接 Rabboni 裝置
        await rabo2.connect(mac_address="E7:0E:BB:FD:BE:CE")  # 根據 MAC 地址連接 Rabboni 裝置
        await rabo1.read_data()  # 開始讀取數據
        await rabo2.read_data()  # 開始讀取數據
        
        print("Connected!")
        cnt_1 = 0
        cnt_2 = 0
        while True:  # 持續讀取並處理數據直到手動停止
            # 根據加速度計數據判斷裝置的放置狀態
            #print("Accx: ", rabo1.Accx, "Accy: ", rabo1.Accy, "Accz: ", rabo1.Accz)
            #print("Accx: ", rabo2.Accx, "Accy: ", rabo2.Accy, "Accz: ", rabo2.Accz)
            
            if rabo1.Accz < 0.2:
                cnt_1 = cnt_1 + 1 
                print("\r左手放手"+str(cnt_1)+"下", end ="")
            if rabo2.Accz < 0.2:
                cnt_2 = cnt_2 + 1 
                print("\r右手放手"+str(cnt_2)+"下", end ="")
                
            await asyncio.sleep(0.2)  # add a small delay to prevent CPU overuse
    except KeyboardInterrupt:  # 當按下 Ctrl+C 中斷程式時處理
        print('Shut down!')
    except Exception as e:  # 當發生其他例外時處理
        print(f"Error: {e}")
        traceback.print_exc()
    finally:
        await rabo1.stop()
        await rabo2.stop()

# Run the main function
asyncio.run(main())