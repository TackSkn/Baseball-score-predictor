import pandas as pd
from sqlalchemy import create_engine


# SQLiteデータベースに接続（SQLiteの場合）
engine = create_engine('sqlite:///baseball_app.db')


# データベースからデータを読み込む
df_loaded = pd.read_sql('hanshin_npb', con=engine)

print(df_loaded)

