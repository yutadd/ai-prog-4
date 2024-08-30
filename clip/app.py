import streamlit as st
import torch  # Meta (facebook) が開発している、深層学習用のライブラリ（テンソル計算用）
import clip  # 今回の主役
from PIL import Image  # 画像読み込み用
import pandas as pd
import plotly.express as px  # グラフ描画用

# CLIP モデルの読み込み
device = "cuda"  # 使用するデバイスを指定
model, preprocess = clip.load("RN50", device=device)  # CLIP モデルと前処理関数を読み込む

if __name__ == "__main__":
    st.title("CLIP App")  # アプリのタイトルを表示
    st.text("画像とテキストのマッチ度を表示する")  # アプリの説明を表示

    # 画像をアップロードする
    image = st.file_uploader("解析対象の画像をアップロードしてください")  # 画像アップロード用のウィジェットを表示
    if image is not None:
        st.image(image)  # アップロードされた画像を表示

    # テキストを入力する
    text = st.text_area("解析対象のテキストを入力してください")  # テキスト入力用のウィジェットを表示
    if text:
        st.text(text)  # 入力されたテキストを表示

    # CLIP の実行ボタン
    is_button_activated = (image is not None) and text  # ボタンが有効かどうかを判定
    if st.button("CLIP による解析を実行する", disabled=not is_button_activated):
        # CLIP のための前処理
        preprocessed_image = preprocess(
            Image.open(image)).unsqueeze(0).to(device)  # 画像を前処理してテンソルに変換
        labels = text.split("\n")  # テキストを改行で分割してラベルにする
        preprocessed_text = clip.tokenize(labels).to(device)  # テキストをトークン化してテンソルに変換

        # CLIP による推論と確信度化の処理
        with torch.no_grad():  # 推論時に勾配計算を無効にする
            logits_per_image, logits_per_text = model(
                preprocessed_image, preprocessed_text)  # 画像とテキストのロジットを計算
            probs = logits_per_image.softmax(dim=-1).cpu().numpy()  # 確率に変換

        # 類似度を表示する UI
        df = pd.DataFrame({"ラベル": labels, "確率": probs[0]})  # ラベルと確率のデータフレームを作成
        df = df.sort_values(by="確率", ascending=False)  # 確率でソート
        st.table(df)  # データフレームをテーブルとして表示

        # 円グラフを表示する UI
        pie_chart = px.pie(df, values="確率", names="ラベル", title="ラベルごとの確率")  # 円グラフを作成
        st.plotly_chart(pie_chart)  # 円グラフを表示
