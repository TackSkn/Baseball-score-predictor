#アプリで実際に使っている関数コード
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

def update_baseball_data(team_number):

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
    DB1_sum = pd.read_sql(f'{team_db_name}_sum', con=engine)
    print(DB1_sum)


    #追加用のデータフレーム
    DB1_sum_import = pd.DataFrame(columns=['日付','勝ち負け','盗塁','先発','勝投手','負投手'])


    # driverの設定
    options = webdriver.ChromeOptions()
    options.add_argument('--incognito')  # ブラウザをクッキーや履歴を保存せず起動
    options.add_argument('--ignore-certificate-errors') #SSLエラーを無視してブラウザが続行するように設定
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--headless')  # ブラウザを表示しない

    # Serviceオブジェクトを使用してChromeDriverを指定
    service = Service('./chromedriver-win64/chromedriver.exe')
    # WebDriverの初期化
    driver = webdriver.Chrome(service=service, options=options)
    # WebDriverWaitの設定
    wait = WebDriverWait(driver, 10)


    # 球団ごとのページにアクセス
    url = f'https://baseballdata.jp/{team_number}/GResult.html'
    driver.get(url)
    sleep(0.5)


    hometeam = driver.find_elements(By.CLASS_NAME, 'deftr')

    sum_number = 0

    for i in range(len(hometeam)):
    #for i in range(0,11):
        choice = hometeam[i].text.split()
        #print(choice)

        if '動員' not in choice:
            #日付，勝ち負け，盗塁数の取得
            hometeam_num = [choice[0],choice[8],choice[-7]]
            
            #元データと日付が一緒なら終了する
            if hometeam_num[0] == DB1_sum.iloc[-1]["日付"]:
                break

            player_name = hometeam[i].find_elements(By.CSS_SELECTOR, 'td > a')

            #先発投手，勝ち投手・負け投手名の取得
            player_name.pop(-3)
            player_name.pop(-3)
            player_name.pop(-4)
            for j in range(len(player_name)):
                player_name[j] = player_name[j].text
            if len(player_name) > 3:
                player_name.pop(0)
            #print(hometeam_num + player_name)
    
            DB1_sum_import.loc[sum_number] = hometeam_num + player_name

            #NPBのデータから直近の何試合のデータを取得するかカウントする
            sum_number += 1

    #print(df_game)
    DB1_sum_import = DB1_sum_import.sort_values("日付")
    #print(df_sorted)


    print(str(sum_number)+"試合がサマリーの新たなデータ数です")
    #df_sorted.to_csv('summary_hanshin24.csv', index=False,encoding="shift-jis", errors='replace')




    #########################ここからはNPBからのデータ取得##################################################


    # NPBのデータも同様に取得
    DB1_npb = pd.read_sql(f'{team_db_name}_npb', con=engine)


    #print(DB1_npb)


    #チーム1の得点を予測するためのデータフレーム
    DB1_npb_import = pd.DataFrame(columns=['対戦相手','得点','打数','安打','打点','四球','死球','三振','攻撃回'])

    # 行数をsum_numberに設定（空の行を追加）
    DB1_npb_import = DB1_npb_import.reindex(range(sum_number+1))

    #何回目の試合か(df_importの何行列目に追加するか)
    npb_number = 0


    # driver上で対象サイトにアクセス
    url2 = 'https://npb.jp/bis/2024/calendar/index_04.html'
    driver.get(url2)
    sleep(0.5)

    months = driver.find_elements(By.CSS_SELECTOR, '#tedivlink a')

    #for idm in months:
    #   print(idm.text)


    month_size = len(months)

    #次の月に移動するか判断するためのカウント
    for k in range(1,month_size+1):
        driver.get('https://npb.jp/bis/2024/calendar/index_04.html')
        months = driver.find_elements(By.CSS_SELECTOR, '#tedivlink a')
        months[-k].click()
        sleep(0.5)
        
        games = driver.find_elements(By.CSS_SELECTOR, 'td > div > div > a')
        if not games:
            print("この月は試合がありません")
        
        else:
            #sleep(3)
            for team in reversed(games):
                #相手球団名取得のためのリスト
                opp_name = [0]
                #得点取得のためのリスト
                team_point = [0]
                if team_short_name in team.text:
                    #試合カレンダーの得失点結果を取得
                    point = team.text.split()
                    team.click()
                    #sleep(3)

                    player_score = driver.find_elements(By.CSS_SELECTOR, 'tr > td > table > tbody >tr')
                    #sleep(3)

                    if len(player_score) > 10:

                        hometeam = driver.find_elements(By.CLASS_NAME, 'gmtblteam')
                        #sleep(3)

                        if team_full_name in hometeam[0].text:
                            #print("{}がビジター".format(team_name[l][0]))
                            opp_name[0] = hometeam[1].text
                            home_team = 0
                            team_point[0] = point[3]
                        #player_score
                        else:
                            #print("{}がホーム".format(team_name[l][0]))
                            opp_name[0] = hometeam[0].text
                            home_team = 1
                            team_point[0] = point[1]

                        opp_pitch = [0]
                        team_bat = [0 for _ in range(6)]
                        #どこからが投打成績のホームとビジターの位置を把握
                    
                        #ホームチームの打撃成績の位置把握
                        for i in range(7,len(player_score)):
                            if "死" in player_score[i].text:
                                home_bat_count = i+1
                                break
                        #print(i,list(map(int,player_score[i].text.split()[2:]))) #ビジターの個人打撃

                        #ビジターの投手成績の位置把握
                        keywords = ["投","回"]
                        for i in range(home_bat_count,len(player_score)+1):
                            if all(keyword in player_score[i].text for keyword in keywords):
                                vis_pitch_count = i+1
                                break
                    
                        #ホームチームの投手成績の位置把握
                        for i in range(vis_pitch_count,len(player_score)+1):
                            if all(keyword in player_score[i].text for keyword in keywords):
                                home_pitch_count = i+1
                                break
                    
                        #阪神がホームなら以下を実行する
                        if home_team == 1:
                            #ホームチームの打撃成績の取得
                            for i in range(home_bat_count,vis_pitch_count-1):
                                #print(player_score[i].text.split()[2:])
                                team_bat = [a + b for a,b in zip(team_bat,list(map(int,player_score[i].text.split()[2:])))]
                        
                            #ビジターの投手成績の取得
                            #3アウト未満をpartでカウントする
                            part = 0
                            for i in range(vis_pitch_count,home_pitch_count-1):
                                ind_player_score = player_score[i].text.split()
                                #投球回数に+が含まれる場合の処理
                                if '+' in ind_player_score:
                                    for index, element in enumerate(ind_player_score):
                                        if '+' in element and (index == 1 or index == 2):
                                            test = ind_player_score[index-1]
                                            try:
                                                int(test)
                                            except:
                                                ind_player_score[index] = '0'

                                if '+' in ind_player_score:
                                    ind_player_score.remove('+')

                                for j in range(len(ind_player_score)):
                                    if ".1" in ind_player_score[j]:
                                        ind_player_score.pop(j)
                                        part += 1
                                        break

                                    elif ".2" in ind_player_score[j]:
                                        ind_player_score.pop(j)
                                        part += 2
                                        break

                                #print(ind_player_score)
                                if len(ind_player_score) > 8:
                                    ind_player_score = ind_player_score[1:]
                                #print(ind_player_score[1]) #各投手の投球回数を表示

                                #投球回数の総和を計算
                                opp_pitch = [a + b for a,b in zip(opp_pitch,list(map(float,ind_player_score[1])))]
                            opp_pitch[0] += part*(1/3)
                    
                        #阪神がビジターなら以下を実行する
                        else:
                            #ビジターの打撃成績の取得
                            for i in range(7,home_bat_count-1):
                                team_bat = [a + b for a,b in zip(team_bat,list(map(int,player_score[i].text.split()[2:])))]
                        
                            #ホームチームの投手成績の取得
                            #3アウト未満をpartでカウントする
                            part = 0
                            for i in range(home_pitch_count,len(player_score)):
                                ind_player_score = player_score[i].text.split()

                                #投球回数に+が含まれる場合の処理
                                if '+' in ind_player_score:
                                    for index, element in enumerate(ind_player_score):
                                        if '+' in element and (index == 1 or index == 2):
                                            test = ind_player_score[index-1]
                                            try:
                                                int(test)
                                            except:
                                                ind_player_score[index] = '0'

                                if '+' in ind_player_score:
                                    ind_player_score.remove('+')
                    
                                for j in range(len(ind_player_score)):
                                    if ".1" in ind_player_score[j]:
                                        part += 1
                                        ind_player_score.pop(j)
                                        break

                                    elif ".2" in ind_player_score[j]:
                                        part += 2
                                        ind_player_score.pop(j)
                                        break

                                if len(ind_player_score) > 8:
                                    ind_player_score = ind_player_score[1:]

                                #print(ind_player_score[1]) #各投手の投球回数を表示

                                #投球回数の総和を計算
                                opp_pitch = [a + b for a,b in zip(opp_pitch,list(map(float,ind_player_score[1])))]
                            opp_pitch[0] += part*(1/3)

                        DB1_npb_import.loc[sum_number-npb_number] = opp_name + team_point + team_bat + opp_pitch
                        #df_game.loc[number] = team_bat + opp_pitch
                        #print(sum_number-1-npb_number)
                        #print(df_import2)


                        npb_number += 1

                        #print(df_game)
                        #sleep(3)
                        driver.back()
                    
                    else:
                        driver.back()

                    #print("新データ")
                    #print(DB1_npb_import)
                    #print("一致しているかの行")
                    #print(sum_number-npb_number)
                    #print(DF2.iloc[-1])
                    #print("新たに追加した行")
                    #print(df_import2.loc[sum_number-npb_number])


                    #summaryデータと同じ数取得、あるいは行が一致したらgameの移動を終了する
                    if npb_number >= sum_number or DB1_npb_import.loc[sum_number-npb_number].equals(DB1_npb.iloc[-1]):
                        break

        #DF2の最後の行と新たに取得したデータの行が一致した場合はnpb_numberを1つ減らしmonthの移動も終了する
        if DB1_npb_import.loc[sum_number-npb_number].equals(DB1_npb.iloc[-1]):
            npb_number = npb_number-1
            break

        #summaryデータと同じ数取得できたらmonthの移動も終了する
        elif npb_number >= sum_number:
            break

    #print(df_import2)
    #print(DB1_npb_import)

    print(str(sum_number)+"試合がnpbの新たなデータ数です")

    #npbとサマリーで新たな取得したデータ数が少ない方をmin_numberとする
    min_number = min(npb_number,sum_number)


    if min_number >= 1:

        #行方向への結合
        DF_sum = pd.concat([DB1_sum, DB1_sum_import.iloc[:min_number]], axis=0, ignore_index=True)

        #行方向への結合
        DF_npb = pd.concat([DB1_npb, DB1_npb_import.iloc[-min_number:]], axis=0, ignore_index=True)
        #DF_npb = pd.concat([DB1_npb, DB1_npb_import.iloc[-min_number-1:-1]], axis=0, ignore_index=True)

        #print("サマリー更新後")
        #print(DF_sum.tail(5))


        #print("npb更新後")
        #print(DF_npb.tail(5))
            
        # データベースに上書きするために既存のテーブルを削除
        with engine.connect() as connection:
            # DROP TABLE クエリを text() でラップして実行する
            connection.execute(text(f"DROP TABLE IF EXISTS {team_db_name}_sum"))
            connection.execute(text(f"DROP TABLE IF EXISTS {team_db_name}_npb"))

        #欠損値のある行を排除する
        #DF_sum = DF_sum.dropna()
        #DF_npb = DF_npb.dropna()


        # 新しいデータをデータベースに保存
        DF_sum.to_sql(f'{team_db_name}_sum', con=engine, index=False, if_exists='replace')
        DF_npb.to_sql(f'{team_db_name}_npb', con=engine, index=False, if_exists='replace')