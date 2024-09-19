#元データから分析用に加工するコード
import pandas as pd
import numpy as np
from sqlalchemy import create_engine


def data_process(team_number):
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

    #print(DF_comb.head())
    #df_comb.info()

    # 新しいデータフレームを作成
    new_df = pd.DataFrame()

    #以下は説明変数列を作るための加工

    #日付
    new_df['日付'] = DF_comb['日付']

    #対戦相手
    new_df['対戦相手'] = DF_comb['対戦相手']

    #チームの勝ち負け
    new_df['勝ち負け'] = DF_comb.apply(lambda row: 1 if row['勝ち負け'] == '○' else 0, axis=1)

    #チーム打率
    new_df['チーム打率'] = DF_comb['安打']/DF_comb['打数']

    #四死球の数
    new_df['四死球'] = DF_comb['四球'] + DF_comb['死球']

    #得点
    new_df['得点'] = DF_comb['得点']

    #打点
    new_df['打点'] = DF_comb['打点']


    #以下は説明変数列の作成

    #直近の平均盗塁数
    new_df['平均盗塁'] = DF_comb['盗塁'].shift(1).rolling(window=6).sum()/6

    #自チームの直近6試合の勝率
    new_df['直近勝率'] = new_df['勝ち負け'].shift(1).rolling(window=6).sum()/6

    #直近6試合の平均得点
    new_df['平均打点'] = DF_comb['打点'].shift(1).rolling(window=6).sum()/6

    #直近6試合の平均打率
    new_df['平均打率'] = new_df['チーム打率'].shift(1).rolling(window=6).sum()/6

    #対戦相手との直近6試合の勝率
    new_df['直近対戦勝率'] = new_df.apply(
        lambda row: new_df[(new_df['対戦相手'] == row['対戦相手']) & (new_df.index < row.name)]['勝ち負け']
        .tail(6).sum()/6 if DF_comb[(new_df['対戦相手'] == row['対戦相手']) & (new_df.index < row.name)].shape[0] >= 6 else np.nan, axis=1)

    #対戦相手との直近6試合の得点率
    # '得点' 列を数値に変換（数値変換ができない場合は NaN に変換）
    new_df['得点'] = pd.to_numeric(new_df['得点'], errors='coerce')

    new_df['対戦平均得点'] = new_df.apply(
        lambda row: new_df[(new_df['対戦相手'] == row['対戦相手']) & (new_df.index < row.name)]['得点']
        .tail(6).sum()/6 if DF_comb[(new_df['対戦相手'] == row['対戦相手']) & (new_df.index < row.name)].shape[0] >= 6 else np.nan, axis=1)



    #平均四死球数
    new_df['平均四死球'] = new_df['四死球'].shift(1).rolling(window=6).sum()/6

    # 特定の対戦相手を取り除く
    filtered_df = new_df[~new_df['対戦相手'].isin(['北海道日本ハム','埼玉西武', '福岡ソフトバンク', '千葉ロッテ','東北楽天','オリックス'])]

    #欠損値のある行を排除する
    df_cleaned = filtered_df.dropna()

    #インデックスをつけ直す
    df_cleaned = df_cleaned.reset_index(drop=True)

    # 新しいデータフレームを確認
    #print(df_cleaned.tail(20))

    return df_cleaned, DF_comb, new_df
    # 必要に応じて、新しいデータフレームをCSVファイルとして保存
    #df_cleaned.to_csv('240831hanshin4.csv', index=False, encoding="shift-jis", errors='replace')

    #print(f"新しいCSVファイルが {output_path} に保存されました。")