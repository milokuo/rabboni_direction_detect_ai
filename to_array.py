# 讀取檔案
file_path = "./train/up/accZ/2.txt"  # 請替換為您的檔案路徑
with open(file_path, 'r') as file:
    lines = file.readlines()

# 處理每一行數字
numbers = []
for line in lines:
    try:
        num = float(line.strip())
        numbers.append(num)
    except ValueError:
        print(f"警告: 無法解析行 '{line.strip()}' 為數字")

# 輸出Python陣列
print(f"Python陣列: {numbers}")