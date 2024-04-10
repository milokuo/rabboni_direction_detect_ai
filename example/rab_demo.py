    import asyncio
    import time
    import random
    from rabboni_multi_python_sdk import Rabboni

    rabbo = Rabboni(mode="BLE")  # 先宣告一個物件


    async def main():
        try:
            await rabbo.connect("E8:88:BD:57:24:64")  # 連結上 rabboni，若沒插上會報錯
            await rabbo.read_config()
            await asyncio.sleep(2)
            # print("Config:", rabbo.Config, rabbo.Config_Acc_Char, rabbo.Config_Gyr_Char, rabbo.Config_Data_Rate)
            await rabbo.set_config(acc_scale=16, gyr_scale=2000, rate=50, threshold=10000)  ## 設定加速度跟陀螺儀的最大範圍與取樣頻率跟 count threshold
            await rabbo.read_config()
            await asyncio.sleep(2)
            print("Config:", rabbo.Config_Acc_Char, rabbo.Config_Gyr_Char, rabbo.Config_Data_Rate)
            await rabbo.read_data()

            max = rabbo.Config_Acc_Char**2 * 3

            # 找出加速度值目前測量最大範圍，三軸做平方相加
            threshold = random.randint(int(max * 0.5), max)
            # 在 max*0.5 與 max 間 隨機取值 當作要超越目標
            # 設max*0.5 是因為太小則太容易贏，若要調整難度上升則 將0.5加大

            print("Power threshold : ", threshold)
            print("You have 3 seconds!")

            print("Ready..Go!")
            await asyncio.sleep(3)  # 暫停三秒
            print("GO!")  # 開始甩Rabboni

            tStart = time.time()  # 計時開始 會存下目前的時間給tStart!
            power = 0
            one_cnt = 0  # 為了倒數秒數時只顯示一次，下段會用到
            two_cnt = 0  # 為了倒數秒數時只顯示一次，下段會用到
            three_cnt = 0  # 為了倒數秒數時只顯示一次，下段會用到

            while True:
                # 以下的 time.time()- tStart 代表 目前時間與開始時間相減
                ##判斷是否超過三秒遊戲時間
                if time.time() - tStart >= 3:  ##超過三秒
                    print("Time's Up!")
                    await rabbo.stop()  # 停止運作
                    break
                elif time.time() - tStart >= 2 and one_cnt == 0:  ## 超過兩秒
                    print("1!")
                    one_cnt = 1
                elif time.time() - tStart >= 1 and two_cnt == 0:  ## 超過一秒
                    two_cnt = 1
                    print("2!")
                else:
                    if three_cnt == 0:
                        print("3!")
                        three_cnt = 1
                power_temp = rabbo.Accx**2 + rabbo.Accy**2 + rabbo.Accz**2  ##將三軸平方相加
                if power_temp >= power:  # 更新紀錄的power
                    power = power_temp

                print("Power threshold:", threshold)
                print("Your Power : ", power)
                if power > threshold:
                    print("You win!")
                else:
                    print("You Loss!")
                await asyncio.sleep(0.1)  # add a small delay to prevent CPU overuse

        except KeyboardInterrupt:  # 結束程式
            print("Shut done!")
            await rabbo.stop()  # 停止運作

    # Run the main function
    asyncio.run(main())
