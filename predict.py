import os
import numpy as np
import tensorflow as tf

# 載入預先訓練好的模型
model = tf.keras.models.load_model("accZ_model_lstm")

def predict_files(directory):
    files = os.listdir(directory)
    for file in files:
        if file.endswith(".txt"):
            file_path = os.path.join(directory, file)
            with open(file_path, 'r') as f:
                # 讀取浮點數數據並將其轉換為 numpy array
                accZ_data = np.array([float(line.strip()) for line in f.readlines()])

            # 檢查數據的長度是否超出所需的填充長度，如果是則截斷數據
            if len(accZ_data) > 150:
                accZ_data = accZ_data[-150:]

            # 填充數據以確保每個樣本都是相同的長度（150個浮點數）
            padded_data = np.pad(accZ_data, (150 - len(accZ_data), 0), mode='constant')
            # print("data: ", padded_data)

            # 使用模型進行預測
            prediction = model.predict(np.array([padded_data]))

            if prediction < 0.5:
                print(f"File {file}: 向上移動")
            else:
                print(f"File {file}: 向下移動")

# 指定要預測的資料夾路徑
data_dir = "./train/up/accZ"

# 執行預測
predict_files(data_dir)