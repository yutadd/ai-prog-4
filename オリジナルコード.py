import streamlit as st
import pandas as pd
import time
import psutil
import requests
'''
@author 坂島悠太君  
国勢調査 時系列データ 人口の労働力状態，就業者の産業・職業 の結果を表示するよ  
'''
# 読み込むCSVの形式：
# "地域_時系列 コード","地域_時系列","表章項目 コード","表章項目","男女_時系列 コード","男女_時系列","労働力状態３区分_時系列 コード","労働力状態３区分_時系列","/時間軸（調査年）","1950年","1955年","1960年","1965年","1970年","1975年","1980年","1985年","1990年","1995年","2000年","2005年","2010年","2015年","2020年","2015年_不詳補完値","2020年_不詳補完値"
# "01000","北海道","320","15歳以上人口【人】","100","総数","100","総数","","2,729,860","3,022,822","3,357,727","3,709,677","3,874,800","4,024,535","4,275,535","4,460,216","4,599,598","4,787,795","4,864,454","4,901,756","4,840,237","4,749,191","4,609,750","4,749,191","4,609,750"
# "01000","北海道","320","15歳以上人口【人】","100","総数","110","労働力人口","","1,753,762","2,004,607","2,201,598","2,357,808","2,498,680","2,515,903","2,668,789","2,744,844","2,796,200","2,935,207","2,867,676","2,785,794","2,701,824","2,553,043","2,449,395","2,737,721","2,753,582"
df = pd.read_csv(r".\.dataset\kokuzei.csv", encoding="shift_jis")

# 表章項目が15歳以上人口【人】のものだけにフィルタリング
df = df[df["表章項目"] == "15歳以上人口【人】"]
# 数値が文字列として読み込まれている列を数値型に変換する
for col in df.columns[9:]:
    df[col] = df[col].str.replace(',', '').astype(int)
st.title(f"人口の労働力状態 人口の労働力状態")

# 都道府県別フィルタ
if st.toggle("検索を表示"):
    st.header("検索")
    colmname = st.selectbox("カラム", df.columns)
    value = st.selectbox("値", df[colmname].unique().tolist())
    df = df[df[colmname] == value]
    # 列選択用のチェックボックスを作成
    selected_options=["地域_時系列"]+df.columns[9:].tolist()
    options=df.columns.tolist()
    if st.toggle("列の選択を表示"):
        st.header("列の選択")
        selected_years = st.multiselect(
            "表示する列を選択してください",
            options=options,  # 1950年以降の列名を選択肢として設定
            default=selected_options  # デフォルトで全ての年を選択
        )
        # 選択された年のデータのみを表示
        df = df[selected_years]
df = df.groupby("地域_時系列").sum()
st.header("結果")
st.dataframe(df)
cpu_placeholder = st.empty()  # プレースホルダーを作成
btc_placeholder = st.empty()  # ビットコイン価格用のプレースホルダーを作成
frame=0
while True:
    time.sleep(1)
    # CPU使用率を更新
    cpu_placeholder.metric(label="サーバーのCPU使用率", value=f"{psutil.cpu_percent()}%")
    # ビットコインの価格情報を取得して表示
    if frame%5==0:
        try:
            btc_response = requests.get('https://api.coindesk.com/v1/bpi/currentprice/BTC.json')
            btc_data = btc_response.json()
            btc_price = btc_data['bpi']['USD']['rate']
            btc_placeholder.metric(label="ビットコインの価格（USD）", value=f"${btc_price}")
        except requests.RequestException as e:
            btc_placeholder.error("ビットコインの価格情報の取得に失敗しました。")
    frame+=1