import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
import os
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout, Bidirectional
from keras.optimizers import Adam
from keras.callbacks import LearningRateScheduler

# 設定隨機種子以確保可重複性
np.random.seed(42)
tf.random.set_seed(42)

# 定義資料路徑
data_dir = "./train"
up_dir = os.path.join(data_dir, "up")
up_dir = os.path.join(up_dir, "accZ")
down_dir = os.path.join(data_dir, "down")
down_dir = os.path.join(down_dir, "accZ")

# 讀取資料並處理為模型適用的格式
def load_data(directory, label):
    data = []
    labels = []
    files = os.listdir(directory)
    for file in files:
        with open(os.path.join(directory, file), 'r') as f:
            # 讀取浮點數數據並將其轉換為 numpy array
            accZ_data = np.array([float(line.strip()) for line in f.readlines()])
            if len(accZ_data) < 150:
                # 填充數據以確保每個樣本都是相同的長度（150個浮點數）
                padded_data = np.pad(accZ_data, (150 - len(accZ_data), 0), mode='constant')
            else:
                accZ_data = accZ_data[-150:]
            data.append(padded_data)
            labels.append(label)
    return np.array(data), np.array(labels)

# 載入資料
up_data, up_labels = load_data(up_dir, 0)
down_data, down_labels = load_data(down_dir, 1)

# 合併資料及標籤
data = np.concatenate((up_data, down_data), axis=0)
labels = np.concatenate((up_labels, down_labels), axis=0)

# 隨機打亂資料及標籤的順序
indices = np.arange(data.shape[0])
np.random.shuffle(indices)
data = data[indices]
labels = labels[indices]

up_count = sum(labels == 0)
down_count = sum(labels == 1)
print(f"Number of 'up' inputs: {up_count}")
print(f"Number of 'down' inputs: {down_count}")

# 建立模型
model = models.Sequential([
    layers.Input(shape=(150, 1)),  # 輸入形狀為 (150, 1)
    layers.LSTM(64, return_sequences=True),  # 返回完整序列
    layers.LSTM(32),  # 返回最後一個輸出
    layers.Dense(1, activation='sigmoid')  # 輸出層，使用 sigmoid 函數輸出概率值
])

# 編譯模型
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# 訓練模型
model.fit(data.reshape(-1, 150, 1), labels, epochs=10, batch_size=64, validation_split=0.2)

# 保存模型
model.save("accZ_model_lstm")