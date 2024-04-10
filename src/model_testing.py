import tensorflow as tf
import numpy as np
import os
from keras.utils import pad_sequences

# 設置參數
data_dir = "test data"
num_samples = 200
window_size = 100
max_length = 300

# 載入預先訓練好的模型
model = tf.keras.models.load_model("lstm_model_2.1")
model.summary()

# 加載測試資料
def load_test_data(data_dir):
    X_accX = []
    X_sum = []
    y_true = []
    for direction in ["left", "right", "motionless"]:
        for i in range(1, 9):
            file_path = os.path.join(data_dir, direction, f"{i}.txt")
            with open(file_path, "r") as f:
                lines = f.readlines()
                accX_data = []
                data_start = False
                for line in lines:
                    if not data_start and "accX, accY, accZ" not in line:
                        continue
                    if "accX, accY, accZ" in line:
                        data_start = True
                        continue
                    values = line.strip().split(", ")
                    accX = float(values[0])
                    accX_data.append(accX)
                accX_data = accX_data[-max_length:]  # 取最後 max_length 筆資料
                accX_data = pad_sequences([accX_data], dtype='float', maxlen=max_length, padding='pre', truncating='pre')[0]  # 在讀取資料時進行padding
                accX_data = accX_data[-num_samples:]
                sum_feature = [sum(accX_data[k:k+window_size]) for k in range(max_length-window_size)]  # 修改sum_feature的計算方式
                X_accX.append(accX_data)
                X_sum.append(sum_feature)
                if direction == "left":
                    y_true.append(0)
                elif direction == "right":
                    y_true.append(1)
                else:
                    y_true.append(2)
    X_accX = np.array(X_accX)
    X_sum = np.array(X_sum)
    y_true = np.array(y_true)
    return X_accX, X_sum, y_true

# 加載測試資料
X_accZ, X_sum, y_true = load_test_data(data_dir)
X_test = np.stack((X_accZ, X_sum), axis=-1)

# 使用模型進行預測
y_pred = model.predict(X_test)
y_pred_labels = np.argmax(y_pred, axis=1)

# 計算模型在測試資料上的準確率
accuracy = np.mean(y_pred_labels == y_true)
print("測試準確率:", accuracy)

# 輸出每個測試樣本的預測結果
for i in range(len(y_true)):
    print("樣本:", i+1)
    print("真實標籤:", y_true[i])
    print("預測標籤:", y_pred_labels[i])
    print("預測概率:", y_pred[i])
    print()