from time import sleep
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import text

team_number = 4

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
#print("以下の番号から球団を選んでください：")
#for num, team in teams.items():
#    print(f"{num}: {team[2]}")

#team_number = int(input("球団番号を入力してください: "))

# 選択された球団情報を取得
team_short_name = teams[team_number][0]
team_full_name = teams[team_number][1]
team_db_name = teams[team_number][2]


# SQLiteデータベースに接続（SQLiteの場合）
engine = create_engine('sqlite:///baseball_app.db')

# 選択された球団のデータベースからサマリーデータを読み込む
DB12_sum = pd.read_sql(f'{team_db_name}_sum', con=engine)
print(DB12_sum.tail(15))

# NPBのデータも同様に取得
DB13_npb = pd.read_sql(f'{team_db_name}_npb', con=engine)
print(DB13_npb.tail(15))

