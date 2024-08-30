import streamlit as st
import cv2
# タイトルを表示
st.title("OpenCV で画像処理")
# ヘッダーを表示
st.header("輪郭抽出")
# 画像をアップロードするためのウィジェットを表示
uploaded_file = st.file_uploader("画像をアップロードしてください")
# 画像がアップロードされた場合の処理
if uploaded_file is not None:
    # アップロードされたファイルの名前を表示
    st.write(uploaded_file.name)
    # アップロードされた画像ファイルを一時保存する
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getvalue())
    # 画像を読み込む
    img = cv2.imread(uploaded_file.name)
    # 処理前の画像を表示
    st.image(uploaded_file, caption="処理前")
    # 処理後の画像を表示（ここではまだ処理は行っていない）
    st.image(img, caption="処理後")
