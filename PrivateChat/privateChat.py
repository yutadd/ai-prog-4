import ollama
import streamlit as st
import sqlite3
import random
# SQLiteデータベースに接続
conn = sqlite3.connect('private.db')
cursor = conn.cursor()

# チャット履歴テーブルが存在しない場合は作成
cursor.execute('''
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()
# セッションIDを取得してユーザーがセッションを選択できるようにする
session_ids = [row[0] for row in cursor.execute('SELECT DISTINCT session_id FROM chat_history').fetchall()]
# デフォルトで新しいチャットを開く
current_session_id = random.randint(1, 1000000)
print(current_session_id)
selected_session_id = st.selectbox('過去のセッション:', session_ids)
if st.button("過去のセッションを使用する。"):
    current_session_id=selected_session_id
if current_session_id:
    st.session_state['chat_history'] = [
        {'role': row[2], 'content': row[3]} for row in cursor.execute('SELECT * FROM chat_history WHERE session_id = ?', (current_session_id,)).fetchall()
    ]

st.title("private chat created by 末永＆坂島")

messages = st.container(height=650)
if st.button('このセッションのチャット履歴を消去'):
    st.session_state['chat_history'] = []
    current_session_id = random.randint(1, 1000000)
st.write(f"現在のセッション: {current_session_id}")
# チャット履歴を保存するためのセッションステートを初期化
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
    st.experimental_rerun()
# チャット履歴を表示
for chat in st.session_state['chat_history']:
    if chat['role'] == 'user':
        messages.chat_message("user").write(chat['content'])
    else:
        messages.chat_message("assistant").write(chat['content'])
if prompt := st.chat_input("入力してね！"):
    # ユーザーのメッセージを履歴に追加
    st.session_state['chat_history'].append(
        {'role': 'user', 'content': prompt})
    messages.chat_message("user").write(prompt)
    response = ollama.chat(
        model='phi3:mini', messages=st.session_state['chat_history'])
    response_message = response['message']['content']
    print(response_message)
    # アシスタントのメッセージを履歴に追加
    st.session_state['chat_history'].append(
        {'role': 'assistant', 'content': response_message})
    messages.chat_message("assistant").write(f"Echo: {response_message}")
    # ユーザーのメッセージをDBに追加
    cursor.execute('''
    INSERT INTO chat_history (session_id, role, content) VALUES (?, ?, ?)
    ''', (current_session_id, 'user', prompt))
    conn.commit()
    # アシスタントのメッセージをDBに追加
    cursor.execute('''
    INSERT INTO chat_history (session_id, role, content) VALUES (?, ?, ?)
    ''', (current_session_id, 'assistant', response_message))
    conn.commit()

# https://docs.streamlit.io/develop/api-reference/chat
# https://docs.streamlit.io/develop/api-reference/chat
