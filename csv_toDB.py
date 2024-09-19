#各CSVファイルを読み込み、データフレーム化する
import pandas as pd
from sqlalchemy import create_engine

# SQLiteデータベースに接続（SQLiteの場合）
engine = create_engine('sqlite:///baseball_app.db')

#阪神
hanshin_summary = pd.read_csv("240910summary_hanshin.csv", encoding='shift_jis')

hanshin_npb23 = pd.read_csv("240910npb_hanshin23.csv", encoding='shift_jis')

hanshin_npb24 = pd.read_csv("240910npb_hanshin24.csv", encoding='shift_jis')

#行方向への結合
hanshin_npb = pd.concat([hanshin_npb23, hanshin_npb24], axis=0)

#データベース化する

# 'hanshin_sum' はデータベース内のテーブル名
hanshin_summary.to_sql('hanshin_sum', con=engine, if_exists='replace', index=False)

hanshin_npb.to_sql('hanshin_npb', con=engine, if_exists='replace', index=False)



#広島
hiroshima_summary = pd.read_csv("240910summary_hiroshima.csv", encoding='shift_jis')

hiroshima_npb23 = pd.read_csv("240910npb_hiroshima23.csv", encoding='shift_jis')

hiroshima_npb24 = pd.read_csv("240910npb_hiroshima24.csv", encoding='shift_jis')

#行方向への結合
hiroshima_npb = pd.concat([hiroshima_npb23, hiroshima_npb24], axis=0)

#データベース化する
hiroshima_summary.to_sql('hiroshima_sum', con=engine, if_exists='replace', index=False)

hiroshima_npb.to_sql('hiroshima_npb', con=engine, if_exists='replace', index=False)




#読売
yomiuri_summary = pd.read_csv("240910summary_yomiuri.csv", encoding='shift_jis')

yomiuri_npb23 = pd.read_csv("240910npb_yomiuri23.csv", encoding='shift_jis')

yomiuri_npb24 = pd.read_csv("240910npb_yomiuri24.csv", encoding='shift_jis')

#行方向への結合
yomiuri_npb = pd.concat([yomiuri_npb23, yomiuri_npb24], axis=0)

#データベース化する
yomiuri_summary.to_sql('yomiuri_sum', con=engine, if_exists='replace', index=False)

yomiuri_npb.to_sql('yomiuri_npb', con=engine, if_exists='replace', index=False)




#横浜
yokohama_summary = pd.read_csv("240910summary_yokohama.csv", encoding='shift_jis')

yokohama_npb23 = pd.read_csv("240910npb_yokohama23.csv", encoding='shift_jis')

yokohama_npb24 = pd.read_csv("240910npb_yokohama24.csv", encoding='shift_jis')

#行方向への結合
yokohama_npb = pd.concat([yokohama_npb23, yokohama_npb24], axis=0)

#データベース化する
yokohama_summary.to_sql('yokohama_sum', con=engine, if_exists='replace', index=False)

yokohama_npb.to_sql('yokohama_npb', con=engine, if_exists='replace', index=False)



#中日
chunichi_summary = pd.read_csv("240910summary_chunichi.csv", encoding='shift_jis')

chunichi_npb23 = pd.read_csv("240910npb_chunichi23.csv", encoding='shift_jis')

chunichi_npb24 = pd.read_csv("240910npb_chunichi24.csv", encoding='shift_jis')

#行方向への結合
chunichi_npb = pd.concat([chunichi_npb23, chunichi_npb24], axis=0)

#データベース化する
chunichi_summary.to_sql('chunichi_sum', con=engine, if_exists='replace', index=False)

chunichi_npb.to_sql('chunichi_npb', con=engine, if_exists='replace', index=False)



#ヤクルト
yakult_summary = pd.read_csv("240910summary_yakult.csv", encoding='shift_jis')

yakult_npb23 = pd.read_csv("240910npb_yakult23.csv", encoding='shift_jis')

yakult_npb24 = pd.read_csv("240910npb_yakult24.csv", encoding='shift_jis')

#行方向への結合
yakult_npb = pd.concat([yakult_npb23, yakult_npb24], axis=0)

#データベース化する
yakult_summary.to_sql('yakult_sum', con=engine, if_exists='replace', index=False)

yakult_npb.to_sql('yakult_npb', con=engine, if_exists='replace', index=False)




#各データの概要
#df_summary.info()

#df_npb23.info()

#df_npb24.info()

#広島
