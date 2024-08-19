import streamlit as st
import torch  # Meta (facebook) が開発している、深層学習用のライブラリ（テンソル計算用）
import clip  # 今回の主役
from PIL import Image  # 画像読み込み用
import pandas as pd
import plotly.express as px  # グラフ描画用


# CLIP モデルの読み込み
device = "cuda"
model, preprocess = clip.load("RN50", device=device)


if __name__ == "__main__":
    st.title("CLIP App")
    st.text("画像とテキストのマッチ度を表示する")

    # 画像をアップロードする
    image = st.file_uploader("解析対象の画像をアップロードしてください")
    if image is not None:
        st.image(image)

    # テキストを入力する
    text = st.text_area("解析対象のテキストを入力してください")
    if text:
        st.text(text)

    # CLIP の実行ボタン
    is_button_activated = (image is not None) and text
    if st.button("CLIP による解析を実行する", disabled=not is_button_activated):

        # CLIP のための前処理
        preprocessed_image = preprocess(Image.open(image)).unsqueeze(0).to(device)
        labels = text.split("\n")
        preprocessed_text = clip.tokenize(labels).to(device)

        # CLIP による推論と確信度化の処理
        with torch.no_grad():
            logits_per_image, logits_per_text = model(preprocessed_image, preprocessed_text)
            probs = logits_per_image.softmax(dim=-1).cpu().numpy()
        
        # 類似度を表示する UI
        df = pd.DataFrame({"ラベル": labels, "確率": probs[0]})
        df = df.sort_values(by="確率", ascending=False)
        st.table(df)

        # 円グラフを表示する UI
        pie_chart = px.pie(df, values="確率", names="ラベル", title="ラベルごとの確率")
        st.plotly_chart(pie_chart)