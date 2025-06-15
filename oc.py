import streamlit as st
import time
import os
from PIL import Image
import predict
import shutil
import requests
from io import BytesIO
import json

st.set_page_config(page_title="犬猫分類AI", layout="centered")
st.write('# AIで画像を分類しよう！')

# サンプル画像のURL
SAMPLE_IMAGES = [
    {
        "title": "🐕 犬のサンプル1",
        "url": "https://images.unsplash.com/photo-1552053831-71594a27632d?w=400&h=400&fit=crop",
        "thumbnail": "https://images.unsplash.com/photo-1552053831-71594a27632d?w=200&h=200&fit=crop"
    },
    {
        "title": "🐱 猫のサンプル1",
        "url": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=400&h=400&fit=crop",
        "thumbnail": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=200&h=200&fit=crop"
    },
    {
        "title": "🐕 犬のサンプル2",
        "url": "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=400&h=400&fit=crop",
        "thumbnail": "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=200&h=200&fit=crop"
    },
    {
        "title": "🐱 猫のサンプル2",
        "url": "https://images.unsplash.com/photo-1574158622682-e40e69881006?w=400&h=400&fit=crop",
        "thumbnail": "https://images.unsplash.com/photo-1574158622682-e40e69881006?w=200&h=200&fit=crop"
    }
]

def search_images_google(query, api_key, search_engine_id, num_results=8):
    """Google Custom Search APIを使って画像を検索"""
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': AIzaSyCZAhEWz6VwIfjLSIrSPdEnxQh4L1rwMkw,
            'cx': f161d859b216d43e1,
            'q': query,
            'searchType': 'image',
            'num': num_results,
            'safe': 'active',
            'imgType': 'photo',
            'imgSize': 'medium'
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        results = response.json()
        images = []

        if 'items' in results:
            for item in results['items']:
                images.append({
                    'title': item.get('title', 'No title')[:50],
                    'url': item.get('link', ''),
                    'thumbnail': item.get('image', {}).get('thumbnailLink', item.get('link', ''))
                })

        return images
    except Exception as e:
        st.error(f"画像検索でエラーが発生しました: {str(e)}")
        return []

def download_image_from_url(url):
    """URLから画像をダウンロード"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        img = Image.open(BytesIO(response.content))
        # RGB形式に変換
        if img.mode != 'RGB':
            img = img.convert('RGB')
        return img
    except Exception as e:
        st.error(f"画像のダウンロードに失敗: {str(e)}")
        return None

def save_image_to_keep(image, filename):
    """画像をkeepディレクトリに保存"""
    if not os.path.exists(keep_dir):
        os.makedirs(keep_dir, exist_ok=True)

    img_path = os.path.join(keep_dir, filename)
    image.save(img_path)
    return img_path

# keep_dir = 'dog_vs_cat\\dog_vs_cat\\keep'
keep_dir = os.path.join(os.path.dirname(__file__), "keep")
if not os.path.exists(keep_dir):
    os.makedirs(keep_dir, exist_ok=True)

# セッションステートの初期化
if "result" not in st.session_state:
    st.session_state.result = None
    st.session_state.prob = None
    st.session_state.predicted = False
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "selected_image_url" not in st.session_state:
    st.session_state.selected_image_url = None
if "current_image_path" not in st.session_state:
    st.session_state.current_image_path = None

# サイドバーでGoogle Custom Search API設定
st.sidebar.header("🔧 Google Custom Search API 設定")
st.sidebar.markdown("画像検索機能を使用するには、APIキーの設定が必要です。")

with st.sidebar.expander("📖 API設定ガイド"):
    st.markdown("""
    **手順:**
    1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成
    2. Custom Search API を有効化
    3. APIキーを作成
    4. [Programmable Search Engine](https://programmablesearchengine.google.com/) で検索エンジンを作成
    5. 画像検索を有効化
    6. 検索エンジンIDを取得
    """)

api_key = st.sidebar.text_input("Google API Key", type="password", help="Google Cloud Consoleで取得したAPIキー")
search_engine_id = st.sidebar.text_input("Custom Search Engine ID", help="Programmable Search Engineで取得したID")

# API設定状況
if api_key and search_engine_id:
    st.sidebar.success("✅ API設定完了")
else:
    st.sidebar.warning("⚠️ API未設定（サンプル画像は利用可能）")

# タブで機能を分ける
tab1, tab2 = st.tabs(["📁 ファイルアップロード", "🔍 画像検索"])

with tab1:
    st.header("ファイルから画像をアップロード")
    uploaded_file = st.file_uploader("画像を挿入してください", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        st.image(uploaded_file, caption="アップロードされた画像", width=500)

        # 保存しておく
        img_path = os.path.join(keep_dir, uploaded_file.name)
        Image.open(uploaded_file).save(img_path)
        st.session_state.current_image_path = img_path

        _, col_center, _ = st.columns(3)
        with col_center:
            predict_button = st.button("予測する", key="predict_upload")

        if predict_button:
            # プレースホルダーを用意して、バーを動的に制御
            progress_placeholder = st.empty()
            progress_bar = progress_placeholder.progress(0)
            status_text = st.empty()
            total_steps = 20

            for i in range(total_steps):
                time.sleep(0.1)
                progress_bar.progress((i + 1) / total_steps)
                status_text.text(f"推論中... {int((i + 1) / total_steps * 100)}% 完了")

            # 推論してセッションステートに保存
            result, prob = predict.main(img_path)
            st.session_state.result = result
            st.session_state.prob = prob
            st.session_state.predicted = True

            # バーとテキストを消去
            progress_placeholder.empty()
            status_text.empty()

            st.success("✅ 推論が完了しました！")

with tab2:
    st.header("画像検索で画像を選択")

    # 検索クエリ入力
    search_query = st.text_input("検索キーワードを入力してください", placeholder="例: 犬、猫、golden retriever")

    col1, col2 = st.columns(2)
    with col1:
        search_button = st.button("🔍 画像検索", disabled=not search_query)
    with col2:
        sample_button = st.button("📷 サンプル画像を表示")

    # Google画像検索
    if search_button and search_query:
        if api_key and search_engine_id:
            with st.spinner("画像を検索中..."):
                search_results = search_images_google(search_query, api_key, search_engine_id)
                st.session_state.search_results = search_results

                if search_results:
                    st.success(f"✅ {len(search_results)}件の画像が見つかりました！")
                else:
                    st.warning("画像が見つかりませんでした。サンプル画像をお試しください。")
        else:
            st.error("APIキーと検索エンジンIDを設定してください。")

    # サンプル画像表示
    if sample_button:
        st.session_state.search_results = SAMPLE_IMAGES
        st.info("サンプル画像を表示しています")

    # 検索結果の表示
    if st.session_state.search_results:
        st.subheader("画像を選択してください")

        # 2列で画像を表示
        for i in range(0, len(st.session_state.search_results), 2):
            col_img1, col_img2 = st.columns(2)

            # 左の列
            if i < len(st.session_state.search_results):
                with col_img1:
                    img_data = st.session_state.search_results[i]
                    try:
                        # サムネイル表示
                        st.image(img_data['thumbnail'], caption=img_data['title'], use_column_width=True)
                        if st.button(f"この画像を選択", key=f"select_{i}"):
                            st.session_state.selected_image_url = img_data['url']
                            st.rerun()
                    except:
                        st.error(f"画像 {i+1} の表示に失敗")

            # 右の列
            if i + 1 < len(st.session_state.search_results):
                with col_img2:
                    img_data = st.session_state.search_results[i + 1]
                    try:
                        # サムネイル表示
                        st.image(img_data['thumbnail'], caption=img_data['title'], use_column_width=True)
                        if st.button(f"この画像を選択", key=f"select_{i+1}"):
                            st.session_state.selected_image_url = img_data['url']
                            st.rerun()
                    except:
                        st.error(f"画像 {i+2} の表示に失敗")

    # 選択された画像の処理
    if st.session_state.selected_image_url:
        st.write("### 選択された画像:")

        # 画像をダウンロードして表示
        with st.spinner("画像をダウンロード中..."):
            selected_img = download_image_from_url(st.session_state.selected_image_url)

            if selected_img:
                st.image(selected_img, caption="選択された画像", width=500)

                # 画像を保存
                img_path = save_image_to_keep(selected_img, "selected_image.jpg")
                st.session_state.current_image_path = img_path

                col1, col2, col3 = st.columns(3)
                with col2:
                    predict_search_button = st.button("🧠 予測する", key="predict_search")

                if predict_search_button:
                    # プレースホルダーを用意して、バーを動的に制御
                    progress_placeholder = st.empty()
                    progress_bar = progress_placeholder.progress(0)
                    status_text = st.empty()
                    total_steps = 20

                    for i in range(total_steps):
                        time.sleep(0.1)
                        progress_bar.progress((i + 1) / total_steps)
                        status_text.text(f"推論中... {int((i + 1) / total_steps * 100)}% 完了")

                    # 推論してセッションステートに保存
                    result, prob = predict.main(img_path)
                    st.session_state.result = result
                    st.session_state.prob = prob
                    st.session_state.predicted = True

                    # バーとテキストを消去
                    progress_placeholder.empty()
                    status_text.empty()

                    st.success("✅ 推論が完了しました！")

                # 画像をクリアするボタン
                col1, col2, col3 = st.columns(3)
                with col2:
                    if st.button("🗑️ 画像をクリア", key="clear_image"):
                        st.session_state.selected_image_url = None
                        st.session_state.search_results = []
                        st.session_state.current_image_path = None
                        st.rerun()
            else:
                st.error("画像のダウンロードに失敗しました。")

# 推論結果の表示
if st.session_state.predicted:
    st.write("---")
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

# クリーンアップ処理
if not st.session_state.current_image_path:
    if os.path.exists(keep_dir):
        shutil.rmtree(keep_dir)
    # 必要に応じて状態をリセット
    if not uploaded_file and not st.session_state.selected_image_url:
        st.session_state.result = None
        st.session_state.prob = None
        st.session_state.predicted = False
