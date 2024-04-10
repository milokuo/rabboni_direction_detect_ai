import asyncio
import time
import random
from rabboni_multi_python_sdk import Rabboni
import tensorflow as tf
import numpy as np

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.get_logger().setLevel('ERROR')

# 載入預先訓練好的模型
model = tf.keras.models.load_model("lstm_model_2")
rabbo = Rabboni(mode="BLE")  # 先宣告一個物件

async def main():
    print("Current working directory:", os.getcwd())
    try:
        await rabbo.connect("E7:0E:BB:FD:BE:CE")  # 連結上 rabboni,若沒插上會報錯
        await rabbo.read_config()
        await rabbo.set_config(acc_scale=2, gyr_scale=2000, rate=50, threshold=1000)
        await rabbo.read_config()
        print("Config:", rabbo.Config_Acc_Char, rabbo.Config_Gyr_Char, rabbo.Config_Data_Rate)
        await rabbo.read_data()

        previous_prediction = None

        while True:
            # 獲取 accZ 數據並填充至長度 150
            accZ_data = rabbo.Accz_list
            if len(accZ_data) < 150:
                padded_data = np.pad(accZ_data, (150 - len(accZ_data), 0), mode='constant')
            else:
                padded_data = accZ_data[-150:]

            # 使用模型進行預測
            prediction = model.predict(np.array([padded_data]))

            # 只有在預測結果與上一次不同時才顯示輸出
            if prediction < 0.5 and previous_prediction != "向上移動":
                print("向上移動")
                previous_prediction = "向上移動"
            elif prediction >= 0.5 and previous_prediction != "向下移動":
                print("向下移動")
                previous_prediction = "向下移動"

            # 每 0.1 秒預測一次
            await asyncio.sleep(0.1)

    except KeyboardInterrupt:
        # 結束程式
        print("Shut down!")
        await rabbo.stop()  # 停止運作

# Run the main function
asyncio.run(main())