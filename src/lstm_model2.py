import os
import numpy as np
from keras.utils import pad_sequences
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout, Bidirectional
from keras.optimizers import Adam
from keras.callbacks import LearningRateScheduler

# 設置參數
data_dir = "rawdata"
num_samples = 200
window_size = 100
num_classes = 3
max_length = 300

# 加載數據
def load_data(data_dir):
    X_accX = []
    X_sum = []
    y = []
    for direction in ["left", "right", "motionless"]:
        if direction == "motionless":
            num_files = 3
        else:
            num_files = 6
        for i in range(1, num_files + 1):
            folder_path = os.path.join(data_dir, direction, f"type{i}")
            for j in range(1, 17):  # 循環讀取編號為1到16的txt檔案
                file_path = os.path.join(folder_path, f"{j}.txt")
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
                        y.append(0)
                    elif direction == "right":
                        y.append(1)
                    else:
                        y.append(2)
    return np.array(X_accX), np.array(X_sum), np.array(y)

# 創建LSTM模型
def create_model():
    model = Sequential()
    
    # 第一個雙向LSTM層,128個神經元,返回序列
    model.add(Bidirectional(LSTM(128, return_sequences=True), input_shape=(num_samples, 2)))
    model.add(Dropout(0.2))
    
    # 第二個雙向LSTM層,64個神經元
    model.add(Bidirectional(LSTM(64)))
    model.add(Dropout(0.2))
    
    # 全連接層,64個神經元,ReLU激活
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.2))
    
    # 輸出層,num_classes個神經元,softmax激活
    model.add(Dense(num_classes, activation='softmax'))
    
    # 定義Learning Rate Scheduler
    def scheduler(epoch, lr):
        if epoch < 10:
            return lr
        else:
            return lr * 0.1
    
    # 編譯模型
    opt = Adam(learning_rate=0.001)
    model.compile(loss='sparse_categorical_crossentropy', optimizer=opt, metrics=['accuracy'])
    
    return model, LearningRateScheduler(scheduler)

# 加載數據
X_accX, X_sum, y = load_data(data_dir)
X = np.stack((X_accX, X_sum), axis=-1)

# 創建模型
model, lr_scheduler = create_model()

# 訓練模型
model.fit(X, y, epochs=15, batch_size=32, validation_split=0.2, callbacks=[lr_scheduler])
model.summary()


def load_test_data(test_dir):
    X_accX_test = []
    X_sum_test = []
    y_test = []
    for direction in ["left", "right"]:
        for i in range(1, 9):  # 假設每個方向有8個測試檔案
            file_path = os.path.join(test_dir, direction, f"{i}.txt")
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
                X_accX_test.append(accX_data)
                X_sum_test.append(sum_feature)
                if direction == "left":
                    y_test.append(0)
                elif direction == "right":
                    y_test.append(1)
                else:
                    y_test.append(2)
    return np.array(X_accX_test), np.array(X_sum_test), np.array(y_test)

# 加載測試資料
X_accX_test, X_sum_test, y_test = load_test_data("test_data")
X_test = np.stack((X_accX_test, X_sum_test), axis=-1)

# 使用訓練好的模型進行預測
y_pred = model.predict(X_test)
y_pred_classes = np.argmax(y_pred, axis=1)

accuracy = np.mean(y_pred_classes == y_test)
print("測試準確率:", accuracy)

# 輸出每個樣本的預測結果
for i in range(len(y_test)):
    print(f"樣本 {i+1}:")
    print(f"真實標籤: {y_test[i]}")
    print(f"預測標籤: {y_pred_classes[i]}")
    print(f"預測機率: {y_pred[i]}")
    print()

save_option = input("要儲存模型嗎(y/N)")
if save_option == "y":
    model.save("lstm_model_2.1")