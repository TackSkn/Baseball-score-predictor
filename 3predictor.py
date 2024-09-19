import numpy as np
import pandas as pd
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.feature_selection import RFE

# データの読み込み
# df = pd.read_csv("240831hanshin3.csv", encoding='shift_jis')

def predictor(df, DF, new_DF, team_number):
    # 球団名と対応する番号リスト
    teams = {
        1: ['読　売', 'yomiuri'],   # 読売ジャイアンツ
        2: ['東京ヤクルト', 'yakult'], # 東京ヤクルトスワローズ
        3: ['横浜DeNA', 'yokohama'], # 横浜DeNAベイスターズ
        4: ['中　日', 'chunichi'],   # 中日ドラゴンズ
        5: ['阪　神', 'hanshin'],    # 阪神タイガース
        6: ['広島東洋', 'hiroshima'] # 広島東洋カープ
    }

    opponent_name = teams[team_number][0]

    # 時間変数を生成する
    total_rows = len(df)
    time_list = [(i / total_rows) ** 2 for i in range(total_rows)]
    df['time'] = time_list[-20:] + [time_list[-1]] * (total_rows - 20)

    # 特徴量と目的変数
    X = df[['平均盗塁', '直近勝率', '平均打点', '平均打率', '直近対戦勝率', '対戦平均得点', '平均四死球', 'time']]
    y = df['得点']

    # 訓練セットとテストセットに分割
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 標準化
    scaler = StandardScaler()
    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()

    cols_to_scale = ['平均盗塁', '直近勝率', '平均打点', '平均打率', '直近対戦勝率', '対戦平均得点', '平均四死球']
    X_train_scaled[cols_to_scale] = scaler.fit_transform(X_train[cols_to_scale])
    X_test_scaled[cols_to_scale] = scaler.transform(X_test[cols_to_scale])

    # サポートベクター回帰モデルの作成
    model = SVR(kernel='rbf')

    # RFEによる特徴量選択
    # 目的：重要な特徴量を自動選択
    selector = RFE(estimator=model, n_features_to_select=5)  # 5個の重要な特徴量を選択
    selector = selector.fit(X_train_scaled, y_train)

    # 選ばれた特徴量を確認
    selected_features = X_train.columns[selector.support_]
    print(f"Selected Features: {selected_features}")

    # 特徴量を選択後のデータセットに変更
    X_train_selected = selector.transform(X_train_scaled)
    X_test_selected = selector.transform(X_test_scaled)

    # 特徴量選択後のデータを使ってモデルの再学習
    model.fit(X_train_selected, y_train)

    # モデルの予測
    y_pred = model.predict(X_test_selected)

    # モデルの評価
    mse = mean_squared_error(y_test, y_pred)
    print(f'Mean Squared Error: {mse}')

    r2 = r2_score(y_test, y_pred)
    print(f'R² Score: {r2}')

    # DF, new_DFから特徴量を生成
    DF['盗塁'] = pd.to_numeric(DF['盗塁'], errors='coerce')
    steal = DF['盗塁'].iloc[-6:].mean()
    win_ave = new_DF['勝ち負け'].iloc[-6:].mean()
    rbi_ave = DF['打点'].iloc[-6:].mean()
    batting_ave = new_DF['チーム打率'].iloc[-6:].mean()

    matching_rows = new_DF[new_DF['対戦相手'] == opponent_name]
    op_win = matching_rows['勝ち負け'].tail(6).sum() / 6 if matching_rows.shape[0] >= 6 else np.nan
    op_point = matching_rows['得点'].tail(6).sum() / 6 if matching_rows.shape[0] >= 6 else np.nan
    four_out = new_DF['四死球'].iloc[-6:].mean()

    # 新しいデータ
    new_data = np.array([[steal, win_ave, rbi_ave, batting_ave, op_win, op_point, four_out, 0]])

    # 標準化
    new_data_scaled = new_data.copy()
    new_data_scaled[:, :-1] = scaler.transform(new_data[:, :-1])

    # 特徴量選択されたモデルに新しいデータを渡す
    new_data_selected = selector.transform(new_data_scaled)

    # 予測
    predicted_score = model.predict(new_data_selected)

    return round(predicted_score[0], 1)

