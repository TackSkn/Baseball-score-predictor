#データベースを結合する関数
import pandas as pd
from sqlalchemy import create_engine

def data_combining(team_number):
    # 球団名と対応する番号リスト
    teams = {
        1: ['巨', '読', 'yomiuri'],   # 読売ジャイアンツ
        2: ['ヤ', 'ヤ', 'yakult'], # 東京ヤクルトスワローズ
        3: ['デ', '横', 'yokohama'], # 横浜DeNAベイスターズ
        4: ['中', '中', 'chunichi'],   # 中日ドラゴンズ
        5: ['神', '阪', 'hanshin'],  # 阪神タイガース
        6: ['広', '広', 'hiroshima']     # 広島東洋カープ
    }

    # 選択された球団情報を取得
    team_short_name = teams[team_number][0]
    team_full_name = teams[team_number][1]
    team_db_name = teams[team_number][2]

    # SQLiteデータベースに接続（SQLiteの場合）
    engine = create_engine('sqlite:///baseball_app.db')

    # 選択された球団のデータベースからサマリーデータを読み込む
    DB2_sum = pd.read_sql(f'{team_db_name}_sum', con=engine)

    DB2_npb = pd.read_sql(f'{team_db_name}_npb', con=engine)


    #列方向への結合
    DF_comb = pd.concat([DB2_npb, DB2_sum], axis=1)

    print(DF_comb.head())
    #df_comb.info()
