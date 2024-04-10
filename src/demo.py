import asyncio
import time
import random
from rabboni_multi_python_sdk import Rabboni
#import tensorflow as tf
import numpy as np
import os


# 載入預先訓練好的模型
#model = tf.keras.models.load_model("lstm_model_2")
#model.summary()

rabbo = Rabboni(mode="BLE")  # 先宣告一個物件

async def main():
    try:
        await rabbo.connect("D0:5D:F4:6F:3F:15")  # 連結上 rabboni,若沒插上會報錯
        await rabbo.read_config()
        await rabbo.set_config(acc_scale=8, gyr_scale=2000, rate=50, threshold=1000)
        await rabbo.read_config()
        print("Config:", rabbo.Config_Acc_Char, rabbo.Config_Gyr_Char, rabbo.Config_Data_Rate)
        await rabbo.read_data()

        while True:
            print("請移動設備...")
            await asyncio.sleep(3)  # 等待 3 秒

            # 獲取 accZ 和 sum_feature 數據並填充至長度 300
            accZ_data = rabbo.Accz_list[-300:]
            if len(accZ_data) < 300:
                accZ_data = np.pad(accZ_data, (300 - len(accZ_data), 0), mode='constant')
            sum_feature = [sum(accZ_data[k:k+100]) for k in range(201)]
            if len(sum_feature) < 300:
                sum_feature = np.pad(sum_feature, (300 - len(sum_feature), 0), mode='constant')

            # 將 accZ_data 和 sum_feature 組合成輸入特徵
            input_data = np.stack((accZ_data, sum_feature), axis=-1)
            input_data = np.expand_dims(input_data, axis=0)

            # 使用模型進行預測
            try:
                prediction = model.predict(input_data)
                predicted_label = np.argmax(prediction)
                if predicted_label == 0:
                    print("向左移動")
                elif predicted_label == 1:
                    print("向右移動")
                else:
                    print("靜止不動")
            except Exception as e:
                print("預測時發生錯誤:", str(e))

            repeat = input("要再次測量嗎? (y/N) ")
            if repeat.lower() != 'y':
                break
            rabbo.Accz_list.clear()

        await rabbo.stop()  # 停止運作

    except KeyboardInterrupt:  # 結束程式
        print("Shut down!")
        await rabbo.stop()  # 停止運作

# Run the main function
asyncio.run(main())