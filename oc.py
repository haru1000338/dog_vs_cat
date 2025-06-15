import streamlit as st
import time
import os
from PIL import Image
import predict
import shutil
import requests
from bs4 import BeautifulSoup
import tempfile

st.set_page_config(page_title="犬猫分類AI", layout="centered")
st.write('# AIで画像を分類しよう！')

# keep_dir = 'dog_vs_cat\\dog_vs_cat\\keep'
keep_dir = os.path.join(os.path.dirname(__file__), "keep")
if not os.path.exists(keep_dir):
    os.makedirs(keep_dir, exist_ok=True)

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

def download_image(url, filename):
    """URLから画像をダウンロードして指定したパスに保存"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # 画像をkeepディレクトリに保存
        with open(filename, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        st.error(f"画像のダウンロードに失敗しました: {e}")
        return False

# セッションステートの初期化
if "result" not in st.session_state:
    st.session_state.result = None
    st.session_state.prob = None
    st.session_state.predicted = False
    st.session_state.selected_image_url = None
    st.session_state.selected_image_path = None

# Google画像検索セクション
st.markdown("### 🔍 Google画像検索")
search_query = st.text_input("検索したいキーワードを入力してください:", value="dog cat", key="search_input")

if st.button("画像を検索", key="search_button"):
    if search_query:
        with st.spinner("画像を検索中..."):
            img_urls = search_google_images(search_query)

        if img_urls:
            st.success(f"{len(img_urls)}枚の画像が見つかりました！")
            st.session_state.img_urls = img_urls
        else:
            st.warning("画像が見つかりませんでした。別のキーワードで試してください。")
    else:
        st.warning("検索キーワードを入力してください。")

# 検索結果の表示
if hasattr(st.session_state, 'img_urls') and st.session_state.img_urls:
    st.markdown("### 📸 検索結果から画像を選択")

    # 画像を3列で表示
    cols = st.columns(3)
    for i, url in enumerate(st.session_state.img_urls):
        col = cols[i % 3]
        with col:
            try:
                st.image(url, width=200)
                if st.button(f"この画像を選択", key=f"select_{i}"):
                    # 選択された画像をダウンロード
                    img_filename = f"selected_image_{i}.jpg"
                    img_path = os.path.join(keep_dir, img_filename)

                    with st.spinner("画像をダウンロード中..."):
                        if download_image(url, img_path):
                            st.session_state.selected_image_url = url
                            st.session_state.selected_image_path = img_path
                            st.session_state.result = None
                            st.session_state.prob = None
                            st.session_state.predicted = False
                            st.success("✅ 画像が選択されました！")
                            st.rerun()
            except Exception as e:
                st.error(f"画像の処理でエラーが発生しました: {e}")

# 選択された画像の表示と予測
if st.session_state.selected_image_path and os.path.exists(st.session_state.selected_image_path):
    st.markdown("### 🖼️ 選択された画像")
    st.image(st.session_state.selected_image_path, caption="選択された画像", width=500)

    _, col_center, _ = st.columns(3)
    with col_center:
        predict_button = st.button("予測する")

    if predict_button:
        # プレースホルダーを用意して、バーを動的に制御
        progress_placeholder = st.empty()
        progress_bar = progress_placeholder.progress(0)
        status_text = st.empty()
        total_steps = 20

        for i in range(total_steps):
            time.sleep(0.1)
            progress_bar.progress((i + 1) / total_steps)
            status_text.text(f"推論中... {int((i + 1) / total_steps * 100)}% 完了")        # 推論してセッションステートに保存
        result, prob = predict.main(st.session_state.selected_image_path)
        st.session_state.result = result
        st.session_state.prob = prob
        st.session_state.predicted = True

        # バーとテキストを消去
        progress_placeholder.empty()
        status_text.empty()

        st.success("✅ 推論が完了しました！")

    # 推論済みなら表示
    if st.session_state.predicted:
        if st.button("🔍 結果を見る"):
            st.markdown("### 🧠 判定結果！")
            result = st.session_state.result
            prob = st.session_state.prob
            if result:
                if result == "犬":
                    st.markdown(f"""
                    <div style='text-align: center; padding: 30px; background-color: #d0f0c0;
                                font-size: 36px; font-weight: bold; color: #004d00; border-radius: 10px;'>
                    🐶 犬と判定されました！<br>（確率：{prob * 100:.1f}%）
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='text-align: center; padding: 30px; background-color: #ffe0e0;
                                font-size: 36px; font-weight: bold; color: #800000; border-radius: 10px;'>
                    🐱 猫と判定されました！<br>（確率：{prob * 100:.1f}%）
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("予測に失敗しました。")

else:
    # 画像が選択されていない場合のクリーンアップ
    if not hasattr(st.session_state, 'img_urls') or not st.session_state.img_urls:
        if os.path.exists(keep_dir):
            shutil.rmtree(keep_dir)
        # 状態もリセット
        st.session_state.result = None
        st.session_state.prob = None
        st.session_state.predicted = False

# 使用方法の説明
st.markdown("---")
st.markdown("### 📝 使用方法")
st.markdown("""
1. **🔍 Google画像検索**: 検索キーワードを入力して「画像を検索」をクリック
2. **📸 画像選択**: 検索結果から分類したい画像を選択
3. **🤖 予測実行**: 「予測する」ボタンをクリックして分類開始
4. **🔍 結果確認**: 「結果を見る」ボタンで犬か猫かの判定結果を表示
""")
