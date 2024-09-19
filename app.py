from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from sqlalchemy import create_engine
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from data_update import update_baseball_data
from data_process import data_process
from predictor import predictor


app = Flask(__name__)

# チーム名と番号の対応表
team_mapping = {
    '阪神タイガース': 5,
    '広島東洋カープ': 6,
    '横浜DeNAベイスターズ': 3,
    '読売ジャイアンツ': 1,
    '東京ヤクルトスワローズ': 2,
    '中日ドラゴンズ': 4
}


@app.route('/')
def top():
    return render_template('top.html')

@app.route('/vote', methods=['POST'])
def vote():
    team_name1 = request.form.get('team_name1')
    team_name2 = request.form.get('team_name2')

    # チームが選択されていない、または同じチームが選択された場合のバリデーション
    if not team_name1 or not team_name2 or team_name1 == team_name2:
        return render_template('top.html')

    # チーム名から番号を取得
    team_number1 = team_mapping.get(team_name1)
    team_number2 = team_mapping.get(team_name2)

    if team_number1 is None or team_number2 is None:
        return render_template('top.html')

    # 各チームのデータを更新
    update_baseball_data(team_number1)
    update_baseball_data(team_number2)

    #各チームのサマリーデータとNPBデータの結合し、回帰分析できる形に加工する
    #data_combining(team_number1)

    # 各チームのデータを処理し、クリーニングされたデータフレームを取得
    df_cleaned1, DF_comb1,new_df1 = data_process(team_number1)
    df_cleaned2, DF_comb2,new_df2 = data_process(team_number2)

    team_score1 = predictor(df_cleaned1,DF_comb1,new_df1,team_number2)

    team_score2 = predictor(df_cleaned2,DF_comb2,new_df2,team_number1)

    # 結果ページを表示する、またはリダイレクトする
    return render_template('vote.html', team1=team_name1, team2=team_name2, team_score1=team_score1, team_score2=team_score2)

if __name__ == '__main__':
    app.run(debug=True)
