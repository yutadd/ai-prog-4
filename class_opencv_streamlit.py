import streamlit as st

import cv2
 
st.title("OpenCV で画像処理")

st.header("輪郭抽出")
 
# 画像をアップロードする

uploaded_file = st.file_uploader("画像をアップロードしてください")

if uploaded_file is not None:

    st.write(uploaded_file.name)
 
    # アップロードされた画像ファイルを一時保存する

    with open(uploaded_file.name, "wb") as f:

        f.write(uploaded_file.getvalue())
 
    # 画像を処理をする

    img = cv2.imread(uploaded_file.name)

    # img = cv2.
 
    # 処理前の画像と処理後の画像を並べて表示する

    st.image(uploaded_file, caption="処理前")

    st.image(img, caption="処理後")