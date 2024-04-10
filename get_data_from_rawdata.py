# 定義函式來處理每個檔案
def process_file(input_filename, output_filename, attribute):
    # 打開原始檔案進行讀取
    with open(input_filename, 'r') as input_file:
        # 判斷是否已找到包含特定字串的行
        found = False

        # 創建一個空列表來存儲相應屬性的值
        attribute_values = []

        # 迭代每一行
        for line in input_file:
            # 如果找到包含特定字串的行，將 found 設置為 True，並從下一行開始讀取數據
            if attribute in line:
                found = True
                continue

            # 如果已找到特定字串的行，則將該行的數據添加到 attribute_values 中
            if found:
                data = line.strip().split(',')
                # 根據要查找的屬性，獲取相應位置的數字
                index = None
                if attribute == 'accX':
                    index = 0
                elif attribute == 'accY':
                    index = 1
                elif attribute == 'accZ':
                    index = 2
                elif attribute == 'gyroX':
                    index = 3
                elif attribute == 'gyroY':
                    index = 4
                elif attribute == 'gyroZ':
                    index = 5
                elif attribute == 'magX':
                    index = 6
                elif attribute == 'magY':
                    index = 7
                elif attribute == 'magZ':
                    index = 8

                # 將相應屬性的值添加到列表中
                if index is not None:
                    value = float(data[index])
                    attribute_values.append(value)

    # 將相應屬性的值寫入新的檔案中
    with open(output_filename, 'w') as output_file:
        # 將每個值寫入新的檔案中
        for value in attribute_values:
            output_file.write(str(value) + '\n')

# 主程式
if __name__ == "__main__":
    # 要查找的屬性列表
    attributes = ['accX', 'accY', 'accZ']

    # 迭代處理每個檔案和每個要查找的屬性
    for i in range(1, 273):
        for attribute in attributes:
            # 構建輸入檔案名稱和輸出檔案名稱
            input_filename = f"./train/up/original/{i}.txt"
            output_filename = f"./train/up/{attribute}/{i}.txt"

            # 處理當前檔案和屬性
            process_file(input_filename, output_filename, attribute)

    print("已處理所有檔案。")
