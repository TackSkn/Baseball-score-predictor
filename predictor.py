#サポートベクター回帰
import numpy as np
import pandas as pd
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score

# データの読み込み
#df = pd.read_csv("240831hanshin3.csv", encoding='shift_jis')

def predictor(df,DF,new_DF,team_number):
    # 球団名と対応する番号リスト

    teams = {
        1: ['読　売', 'yomiuri'],   # 読売ジャイアンツ
        2: ['東京ヤクルト', 'yakult'], # 東京ヤクルトスワローズ
        3: ['横浜DeNA', 'yokohama'], # 横浜DeNAベイスターズ
        4: ['中　日', 'chunichi'],   # 中日ドラゴンズ
        5: ['阪　神', 'hanshin'],  # 阪神タイガース
        6: ['広島東洋', 'hiroshima']     # 広島東洋カープ
    }

    opponent_name = teams[team_number][0]

    #以下で時間変数の列を作成
    
    # データフレームの行数を取得
    total_rows = len(df)

    #np.arange

    def generate_power1_list(num):
        time_list = [num ** i for i in range(20)]
        return time_list

    # 10個の要素を持つリストを作成
    def generate_power_list(num):
        time_list = [num ** i for i in range(20)]
        return time_list

    # 例: num = 2 の場合
    #time_list = generate_power_list(3)
    #time_list = range(20)

    #time_list = [np.log(2**i) for i in range(20)]

    # time_listを二次関数に基づいて変化させる
    time_list = [(i / total_rows) ** 2 for i in range(total_rows)]


    # 'time'列を追加して初期値を設定（すべて0に設定）
    df['time'] = 0

    # 一番下の行からtime_listの1,2,3番目の要素を順に代入
    for k in range(21):
        df.iloc[-k, df.columns.get_loc('time')] = time_list[k-1]  # 一番下の行


    # 下から10行目より上の行にはtime_listの10番目の要素を代入
    df.iloc[:-20, df.columns.get_loc('time')] = time_list[-1]  # 下から10行目より上の行

    # 結果を確認
    #print(df[['日付', 'time']].tail(25))

    # 説明変数と目的変数
    X = df[['平均盗塁', '直近勝率', '平均打点', '平均打率',
            '直近対戦勝率', '対戦平均得点', '平均四死球','time']]
    y = df['得点']

    # 訓練セットとテストセットに分割（20%がテストデータ）する。random_stateにより常に分割のされ方が固定される
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    #timeのみ標準化しないようにする
    scaler = StandardScaler()
    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()

    X_train_scaled[['平均盗塁', '直近勝率', '平均打点', '平均打率',
                    '直近対戦勝率', '対戦平均得点', '平均四死球']] = scaler.fit_transform(X_train[['平均盗塁', '直近勝率', '平均打点', '平均打率',
                                                                                                    '直近対戦勝率', '対戦平均得点', '平均四死球']])

    X_test_scaled[['平均盗塁', '直近勝率', '平均打点', '平均打率',
                '直近対戦勝率', '対戦平均得点', '平均四死球']] = scaler.transform(X_test[['平均盗塁', '直近勝率', '平均打点', '平均打率',
                                                                                                    '直近対戦勝率', '対戦平均得点', '平均四死球']])


    # サポートベクター回帰モデルの作成と訓練
    model = SVR(kernel='rbf')
    model.fit(X_train_scaled, y_train)

    # 以下はモデルの評価

    # モデルの予測
    y_pred = model.predict(X_test_scaled)

    # 平均二乗誤差（MSE）を計算
    mse = mean_squared_error(y_test, y_pred)
    print(f'Mean Squared Error: {mse}')

    # R²スコアを計算
    r2 = r2_score(y_test, y_pred)
    print(f'R² Score: {r2}')

    #X = df[['平均盗塁', '直近勝率', '平均打点', '平均打率', '直近対戦勝率', '対戦平均得点', '平均四死球','time']]
    
    #print(DF['盗塁'].iloc[-6:])

    # DF_combの'盗塁'列の最後の6行の平均を計算してstealに代入
    # '盗塁'列を数値型に変換（変換できない値はNaNに置き換え）
    DF['盗塁'] = pd.to_numeric(DF['盗塁'], errors='coerce')

    steal = DF['盗塁'].iloc[-6:].mean()

    win_ave = new_DF['勝ち負け'].iloc[-6:].mean()

    rbi_ave = DF['打点'].iloc[-6:].mean()

    batting_ave = new_DF['チーム打率'].iloc[-6:].mean()

    # opponent_nameが一致する行を取り出し、直近6試合の勝率を計算してop_winに代入
    opponent_name = teams[team_number][0]

    # 対戦球団がopponent_nameと一致する行を取り出し
    matching_rows = new_DF[new_DF['対戦相手'] == opponent_name]

    # 対戦球団との直近6試合の勝率を計算
    op_win = matching_rows['勝ち負け'].tail(6).sum() / 6 if matching_rows.shape[0] >= 6 else np.nan

    # 対戦球団との直近6試合の平均得点を計算
    op_point = matching_rows['得点'].tail(6).sum() / 6 if matching_rows.shape[0] >= 6 else np.nan

    # 直近６試合の平均四死球の数
    four_out = new_DF['四死球'].iloc[-6:].mean()

    # 具体的な特徴量を代入
    new_data = np.array([[steal, win_ave, rbi_ave, batting_ave, op_win, op_point, four_out, 0]])

    

    # 'time'以外の特徴量を標準化
    new_data_scaled = new_data.copy()
    new_data_scaled[:, :-1] = scaler.transform(new_data[:, :-1])

    # 予測を行う
    predicted_score = model.predict(new_data_scaled)
    #print(f'Predicted Score: {predicted_score[0]}')
    #return predicted_score[0]

    return round(predicted_score[0])