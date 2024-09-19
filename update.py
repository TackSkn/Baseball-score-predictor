#このコードはチャットGPTから作ったもの（エラー出る）
from time import sleep
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from sqlalchemy import create_engine

# 球団名と対応する番号リスト
teams = {
    1: ['巨', '読', 'yomiuri'],   # 読売ジャイアンツ
    2: ['ヤ', 'ヤ', 'yakult'], # 東京ヤクルトスワローズ
    3: ['デ', '横', 'yokohama'], # 横浜DeNAベイスターズ
    4: ['中', '中', 'chunichi'],   # 中日ドラゴンズ
    5: ['神', '阪', 'hanshin'],  # 阪神タイガース
    6: ['広', '広', 'hiroshima']     # 広島東洋カープ
}

# チームを選ぶ
print("以下の番号から球団を選んでください：")
for num, team in teams.items():
    print(f"{num}: {team[2]}")

team_number = int(input("球団番号を入力してください: "))

# 選択された球団情報を取得
team_short_name = teams[team_number][0]
team_full_name = teams[team_number][1]
team_db_name = teams[team_number][2]

# SQLiteデータベースに接続
engine = create_engine('sqlite:///baseball_app.db')

# 選択された球団のデータベースからサマリーデータを読み込む
DB1_sum = pd.read_sql(f'{team_db_name}_sum', con=engine)
print(DB1_sum)

# 追加用のデータフレーム
DB1_sum_import = pd.DataFrame(columns=['日付','勝ち負け','盗塁','先発','勝投手','負投手'])

# driverの設定
options = webdriver.ChromeOptions()
options.add_argument('--incognito')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-running-insecure-content')

# ChromeDriverのパスを指定
service = Service('C:/Users/Owner/GeekSalon/chromedriver-win64/chromedriver.exe')
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

# 球団ごとのページにアクセス
url = f'https://baseballdata.jp/{team_number}/GResult.html'
driver.get(url)
sleep(1)

hometeam = driver.find_elements(By.CLASS_NAME, 'deftr')
sum_number = 0

for i in range(len(hometeam)):
    choice = hometeam[i].text.split()

    if '動員' not in choice:
        hometeam_num = [choice[0], choice[8], choice[-7]]

        # 元データと日付が一緒なら終了する
        if hometeam_num[0] == DB1_sum.iloc[-1]["日付"]:
            break

        player_name = hometeam[i].find_elements(By.CSS_SELECTOR, 'td > a')

        player_name.pop(-3)
        player_name.pop(-3)
        player_name.pop(-4)
        for j in range(len(player_name)):
            player_name[j] = player_name[j].text
        if len(player_name) > 3:
            player_name.pop(0)

        DB1_sum_import.loc[sum_number] = hometeam_num + player_name
        sum_number += 1

DB1_sum_import = DB1_sum_import.sort_values("日付")
print(f"{sum_number}試合がサマリーの新たなデータ数です")

# NPBのデータも同様に取得
DB1_npb = pd.read_sql(f'{team_db_name}_npb', con=engine)
print(DB1_npb)

DB1_npb_import = pd.DataFrame(columns=['対戦相手', '得点', '打数', '安打', '打点', '四球', '死球', '三振', '攻撃回'])
DB1_npb_import = DB1_npb_import.reindex(range(sum_number+1))
npb_number = 0

# NPBのカレンダーページにアクセス
url2 = 'https://npb.jp/bis/2024/calendar/index_04.html'
driver.get(url2)
sleep(1)

months = driver.find_elements(By.CSS_SELECTOR, '#tedivlink a')
month_size = len(months)

for k in range(1, month_size + 1):
    driver.get('https://npb.jp/bis/2024/calendar/index_04.html')
    months = driver.find_elements(By.CSS_SELECTOR, '#tedivlink a')
    months[-k].click()
    sleep(1)

    games = driver.find_elements(By.CSS_SELECTOR, 'td > div > div > a')
    if not games:
        print("この月は試合がありません")
    else:
        for team in reversed(games):
            opp_name = [0]
            team_point = [0]

            if team_short_name in team.text:
                point = team.text.split()
                team.click()

                player_score = driver.find_elements(By.CSS_SELECTOR, 'tr > td > table > tbody >tr')

                if len(player_score) > 10:
                    hometeam = driver.find_elements(By.CLASS_NAME, 'gmtblteam')

                    if team_full_name in hometeam[0].text:
                        opp_name[0] = hometeam[1].text
                        home_team = 0
                        team_point[0] = point[3]
                    else:
                        opp_name[0] = hometeam[0].text
                        home_team = 1
                        team_point[0] = point[1]

                    # (ここに阪神の打撃や投手成績の計算部分を追加)

                    DB1_npb_import.loc[sum_number-1-npb_number] = opp_name + team_point
                    npb_number += 1
                    driver.back()

                else:
                    driver.back()

                if npb_number >= sum_number:
                    break

    if npb_number >= sum_number:
        break

print(f"{sum_number}試合がnpbの新たなデータ数です")

# npbとサマリーで新たに取得したデータ数が少ない方をmin_numberとする
min_number = min(npb_number, sum_number)

if min_number >= 1:
    DF_sum = pd.concat([DB1_sum, DB1_sum_import.iloc[:min_number]], axis=0, ignore_index=True)
    DF_npb = pd.concat([DB1_npb, DB1_npb_import.iloc[-min_number-1:-1]], axis=0, ignore_index=True)

    print("サマリー更新後")
    print(DF_sum.tail(15))

    print("npb更新後")
    print(DF_npb.tail(15))
