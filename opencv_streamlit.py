import time
import cv2
import streamlit as st
from PIL import Image  # 追加
import numpy as np
from openai import OpenAI
# 画像アップロード
uploaded_file = st.file_uploader("画像をアップロードしてください", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    # 画像を表示
    image = Image.open(uploaded_file)
    st.image(image, caption='アップロードされた画像。', use_column_width=True)
    # 画像をOpenCV形式に変換
    img_array = np.array(image)
    st.write("画像の形状:", img_array.shape)
    # グレースケールに変換
    gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
    # エッジ検出
    edges = cv2.Canny(gray, 50, 150)
    # 輪郭を検出
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 最大の輪郭を見つける
    largest_contour = max(contours, key=cv2.contourArea)
    # 名刺の部分を切り取る
    x, y, w, h = cv2.boundingRect(largest_contour)
    business_card = img_array[y:y+h, x:x+w]
    # 切り取った名刺を表示
    st.image(business_card, caption='切り取られた名刺。', use_column_width=True)
    output_path = "./tmp/output.png"
    cv2.imwrite(output_path, business_card)
    st.write(f"切り取られた名刺が {output_path} に保存されました。")

    answer_placeholder = st.empty()  # プレースホルダーを作成

    client = OpenAI()
    thread=client.beta.threads.create()
    file=client.files.create(file=open("./tmp/output.png","rb"),purpose="assistants")
    assistant=client.beta.assistants.retrieve(assistant_id="asst_1Y5PWnS8cy8pDUzIyefSJtJT")
    run = client.beta.threads.create_and_run(
        assistant_id="asst_1Y5PWnS8cy8pDUzIyefSJtJT",
        thread={
            "messages": [
                {"role": "user", "content": [{"type":"image_file","image_file":{"file_id":file.id}}]}
            ]
            
        }
    )
    print(run.status)
    answer_placeholder.text("処理しています")
    while(run.status=="queued"):
        answer_placeholder.text("処理のキューに入りました")
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=run.thread_id, run_id=run.id)
        print(run.status)
    while run.status=="in_progress":
        answer_placeholder.text("処理しています")
        run = client.beta.threads.runs.retrieve(thread_id=run.thread_id, run_id=run.id)
        print(run.status)
        time.sleep(1)
    if run.status=="completed":
        messages = client.beta.threads.messages.list(thread_id=run.thread_id)
        if messages.data[0].content[0].text.value:
            answer_placeholder.text(messages.data[0].content[0].text.value)
        else:
            st.error("essages.data[0].content[0].textの中身が空っぽです")
            print(messages[0])
    else:
        st.error(run.status)
        st.error(run.last_error)
    