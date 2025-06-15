import streamlit as st
import requests
from bs4 import BeautifulSoup
import os
import sys
import tempfile
from PIL import Image
import io

# predict.pyの関数をインポート
sys.path.append('..')
from predict import main as predict_image

def search_google_images(query, num_images=10):
    """Google画像検索の結果を取得する"""
    search_url = f"https://www.google.com/search?q={query}&tbm=isch"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 画像URLを抽出
        img_tags = soup.find_all('img')
        img_urls = []

        for img in img_tags:
            src = img.get('src')
            if src and src.startswith('http'):
                img_urls.append(src)
                if len(img_urls) >= num_images:
                    break

        return img_urls
    except Exception as e:
        st.error(f"画像検索でエラーが発生しました: {e}")
        return []

def download_image(url):
    """URLから画像をダウンロードして一時ファイルに保存"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # 画像を一時ファイルに保存
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(response.content)
            return tmp_file.name
    except Exception as e:
        st.error(f"画像のダウンロードに失敗しました: {e}")
        return None

# サンプル画像のパス
sample_images = [
    "results/sample1.jpg",
    "results/sample2.jpg",
    "results/sample3.jpg"
]

# Streamlitアプリのメイン部分
st.title("🐱🐶 犬・猫画像分類アプリ")
st.write("Google画像検索で画像を選択して、犬か猫かを分類します！")

# 検索クエリの入力
search_query = st.text_input("検索したいキーワードを入力してください:", value="dog cat")

if st.button("画像を検索"):
    if search_query:
        with st.spinner("画像を検索中..."):
            img_urls = search_google_images(search_query)

        if img_urls:
            st.success(f"{len(img_urls)}枚の画像が見つかりました！")
        else:
            st.warning("画像が見つかりませんでした。サンプル画像を表示します。")
            img_urls = sample_images

        # 画像を表示（3列のレイアウト）
        cols = st.columns(3)
        for i, url in enumerate(img_urls):
            col = cols[i % 3]
            with col:
                try:
                    # サンプル画像か検索結果かで処理を分ける
                    if url.startswith("http"):
                        st.image(url, width=200)
                        temp_file = download_image(url)
                    else:
                        st.image(url, width=200)
                        temp_file = url

                    # 分類ボタン
                    if st.button(f"分類する", key=f"classify_{i}"):
                        with st.spinner("分類中..."):
                            if temp_file:
                                try:
                                    # 分類を実行
                                    prediction, probability = predict_image(temp_file)

                                    if prediction and probability:
                                        # 結果を表示
                                        st.success(f"予測結果: **{prediction}**")
                                        st.info(f"確率: {probability:.4f}")

                                        # 分類された画像を再表示
                                        st.image(url, caption=f"予測: {prediction} (確率: {probability:.4f})", width=300)
                                    else:
                                        st.error("分類に失敗しました")

                                finally:
                                    # 一時ファイルを削除
                                    if url.startswith("http") and os.path.exists(temp_file):
                                        os.unlink(temp_file)
                            else:
                                st.error("画像のダウンロードに失敗しました")

                except Exception as e:
                    st.error(f"画像の処理でエラーが発生しました: {e}")
    else:
        st.warning("検索キーワードを入力してください。")

# 使用方法の説明
st.markdown("---")
st.markdown("### 使用方法")
st.markdown("""
1. 上の入力欄に検索したいキーワードを入力
2. 「画像を検索」ボタンをクリック
3. 表示された画像の中から分類したい画像の「分類する」ボタンをクリック
4. 犬か猫かの予測結果と確率が表示されます
""")