import streamlit as st
import pandas as pd
from openai import OpenAI
# 読み込むCSVの形式：
# "地域_時系列 コード","地域_時系列","表章項目 コード","表章項目","男女_時系列 コード","男女_時系列","労働力状態３区分_時系列 コード","労働力状態３区分_時系列","/時間軸（調査年）","1950年","1955年","1960年","1965年","1970年","1975年","1980年","1985年","1990年","1995年","2000年","2005年","2010年","2015年","2020年","2015年_不詳補完値","2020年_不詳補完値"
# "地域_時系列 コード","地域_時系列","表章項目 コード","表章項目","男女_時系列 コード","男女_時系列","労働力状態３区分_時系列 コード","労働力状態３区分_時系列","/時間軸（調査年）","1950年","1955年","1960年","1965年","1970年","1975年","1980年","1985年","1990年","1995年","2000年","2005年","2010年","2015年","2020年","2015年_不詳補完値","2020年_不詳補完値"
# "01000","北海道","320","15歳以上人口【人】","100","総数","100","総数","","2,729,860","3,022,822","3,357,727","3,709,677","3,874,800","4,024,535","4,275,535","4,460,216","4,599,598","4,787,795","4,864,454","4,901,756","4,840,237","4,749,191","4,609,750","4,749,191","4,609,750"
import time
def set_is_loading(value):
    global isLoading
    isLoading = value
    st.session_state['isLoading'] = value
    
set_is_loading(False)
df = pd.read_csv(r".\.dataset\kokuzei.csv", encoding="shift_jis")
user_input = st.text_input("表示したいグラフ", "棒グラフで熊本県に絞って表示して",disabled=isLoading)
client = OpenAI()
my_assistant = client.beta.assistants.retrieve("asst_t9H7ziJYvu6yKz8ahziQcbFo")
if st.button("問い合わせを開始") and user_input:
    set_is_loading(True)
    st.success("AIへの問い合わせを行っています。")
    run = client.beta.threads.create_and_run(
        assistant_id="asst_t9H7ziJYvu6yKz8ahziQcbFo",
        thread={
            "messages": [
                {"role": "user", "content": user_input}
            ]
        }
    )
    print(run.status)
    while(run.status=="queued"):
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=run.thread_id, run_id=run.id)
        print(run.status)
    while run.status=="in_progress":
        run = client.beta.threads.runs.retrieve(thread_id=run.thread_id, run_id=run.id)
        print(run.status)
        time.sleep(1)
    if run.status=="completed":
        messages = client.beta.threads.messages.list(thread_id=run.thread_id)
        if messages.data[0].content[0].text.value:
            import re
            codes = re.findall(r'```python\n([\s\S]*?)\n```', str(messages.data[0].content[0].text.value))
            if len(codes)>0:
                print(codes)
                exec(codes[0])
            else:
                st.error("アシスタントがコードを返しませんでした。")
                st.error(messages.data[0].content[0].text)
                print("アシスタントがコードを返しませんでした。")
        else:
            st.error("essages.data[0].content[0].textの中身が空っぽです")
            print(messages[0])
    else:
        st.error(run.status)
        st.error(run.last_error)
    set_is_loading(False)
    st.success("問い合わせが終了しました。")
