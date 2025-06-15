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
    """Google画像検索の結果をスクレイピングで取得する（簡略化版）"""
    search_url = f"https://www.google.com/search?q={query}&tbm=isch"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 画像URLを抽出
        img_tags = soup.find_all('img')
        img_urls = [img.get('src') for img in img_tags if img.get('src') and img.get('src').startswith('http')]

        return img_urls[:num_images]
    except requests.exceptions.RequestException as e:
        st.error(f"画像検索でエラーが発生しました: {e}")
        return []

def download_image(url, filename):
    """URLから画像をダウンロードして指定したパスに保存"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.google.com/',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8'
        }

        # URLの妥当性をチェック
        if not url or not url.startswith('http'):
            st.error(f"無効なURL: {url}")
            return False

        response = requests.get(url, headers=headers, timeout=15, stream=True)
        response.raise_for_status()

        # コンテンツタイプをチェック
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            st.error(f"画像ファイルではありません: {content_type}")
            return False

        # 画像をkeepディレクトリに保存
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        # ファイルサイズをチェック
        file_size = os.path.getsize(filename)
        if file_size < 1024:  # 1KB未満は無効とみなす
            st.error("ダウンロードされたファイルが小さすぎます")
            os.remove(filename)
            return False

        return True
    except requests.exceptions.Timeout:
        st.error("タイムアウト: 画像のダウンロードに時間がかかりすぎています")
        return False
    except requests.exceptions.RequestException as e:
        st.error(f"ネットワークエラー: {e}")
        return False
    except Exception as e:
        st.error(f"画像のダウンロードに失敗しました: {e}")
        return False

def get_sample_images():
    """サンプル画像のURLリストを返す"""
    sample_images = [
        # 犬の画像
        "https://images.unsplash.com/photo-1552053831-71594a27632d?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1518717758536-85ae29035b6d?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=400&h=400&fit=crop",
        # 猫の画像
        "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1573865526739-10659fec78a5?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1592194996308-7b43878e84a6?w=400&h=400&fit=crop",
        # 混合
        "https://images.unsplash.com/photo-1601758228041-f3b2795255f1?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1415369629372-26f2fe60c467?w=400&h=400&fit=crop",
    ]
    return sample_images

def search_images_simple(query, num_images=10):
    """簡易画像検索（確実に動作するサンプル画像を返す）"""

    # 検索クエリに基づいてカテゴリ分け
    dog_keywords = ['dog', 'puppy', '犬', 'いぬ', 'ワンちゃん']
    cat_keywords = ['cat', 'kitten', '猫', 'ねこ', 'ニャンコ']

    is_dog_search = any(keyword in query.lower() for keyword in dog_keywords)
    is_cat_search = any(keyword in query.lower() for keyword in cat_keywords)

    # Unsplashの高品質画像URL（確実にアクセス可能）
    dog_images = [
        "https://images.unsplash.com/photo-1552053831-71594a27632d?w=400&h=400&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1518717758536-85ae29035b6d?w=400&h=400&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=400&h=400&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=400&h=400&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1601758228041-f3b2795255f1?w=400&h=400&fit=crop&auto=format",
    ]

    cat_images = [
        "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=400&h=400&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1573865526739-10659fec78a5?w=400&h=400&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1592194996308-7b43878e84a6?w=400&h=400&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1596854407944-bf87f6fdd49e?w=400&h=400&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1415369629372-26f2fe60c467?w=400&h=400&fit=crop&auto=format",
    ]

    mixed_images = dog_images[:3] + cat_images[:3]

    # 検索クエリに基づいて画像を選択
    if is_dog_search and not is_cat_search:
        selected_images = dog_images[:num_images]
        st.success(f"犬の画像 {len(selected_images)}枚を取得しました！")
    elif is_cat_search and not is_dog_search:
        selected_images = cat_images[:num_images]
        st.success(f"猫の画像 {len(selected_images)}枚を取得しました！")
    else:
        selected_images = mixed_images[:num_images]
        st.success(f"犬・猫の画像 {len(selected_images)}枚を取得しました！")

    return selected_images

# セッションステートの初期化
if "result" not in st.session_state:
    st.session_state.result = None
    st.session_state.prob = None
    st.session_state.predicted = False
    st.session_state.selected_image_url = None
    st.session_state.selected_image_path = None

# 画像検索セクション
st.markdown("### 🔍 画像検索")
search_query = st.text_input("検索したいキーワードを入力してください:", value="dog cat", key="search_input")

col1, col2 = st.columns(2)
with col1:
    if st.button("画像を検索", key="search_button"):
        if search_query:
            with st.spinner("画像を検索中..."):
                img_urls = search_images_simple(search_query)

            if img_urls:
                st.session_state.img_urls = img_urls
        else:
            st.warning("検索キーワードを入力してください。")

with col2:
    if st.button("📸 サンプル画像を使用", key="sample_button"):
        st.session_state.img_urls = get_sample_images()
        st.success(f"{len(st.session_state.img_urls)}枚のサンプル画像を読み込みました！")

# 検索結果の表示
if hasattr(st.session_state, 'img_urls') and st.session_state.img_urls:
    st.markdown("### 📸 画像を選択してください")

    # 画像を3列で表示
    cols = st.columns(3)
    displayed_count = 0

    for i, url in enumerate(st.session_state.img_urls):
        col = cols[displayed_count % 3]
        with col:
            try:
                # 画像を表示
                st.image(url, width=200, caption=f"画像 {i+1}")

                # 選択ボタン
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
                        else:
                            st.error("この画像のダウンロードに失敗しました。別の画像を試してください。")

                displayed_count += 1

            except Exception as e:
                st.error(f"画像 {i+1} の処理でエラーが発生しました: {e}")

    if displayed_count == 0:
        st.warning("表示可能な画像が見つかりませんでした。")

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
   - Google検索で画像が見つからない場合は「📸 サンプル画像を使用」をお試しください
2. **📸 画像選択**: 検索結果またはサンプル画像から分類したい画像を選択
3. **🤖 予測実行**: 「予測する」ボタンをクリックして分類開始
4. **🔍 結果確認**: 「結果を見る」ボタンで犬か猫かの判定結果を表示

**注意**: Google検索が制限される場合があります。その際はサンプル画像をご利用ください。
""")

def save_images_to_temp(img_urls):
    """画像URLリストを一時ディレクトリに保存"""
    temp_dir = tempfile.mkdtemp()
    saved_files = []

    for i, url in enumerate(img_urls):
        filename = os.path.join(temp_dir, f"image_{i}.jpg")
        if download_image(url, filename):
            saved_files.append(filename)

    return temp_dir, saved_files

# Streamlitアプリで画像選択と推論
st.write("## Google画像検索から画像を選択")
query = st.text_input("検索キーワードを入力してください", "犬")
num_images = st.slider("取得する画像の枚数", 1, 20, 5)

if st.button("画像を検索"):
    with st.spinner("画像を検索中..."):
        img_urls = search_google_images(query, num_images)
        if img_urls:
            temp_dir, saved_files = save_images_to_temp(img_urls)
            st.success(f"{len(saved_files)} 枚の画像を取得しました")

            # 画像を表示して選択
            selected_image = st.selectbox("画像を選択してください", saved_files)
            if selected_image:
                st.image(selected_image, caption="選択された画像", use_column_width=True)

                # 推論を実行
                if st.button("推論を実行"):
                    with st.spinner("推論中..."):
                        result = predict.predict(selected_image)
                        st.write(f"推論結果: {result}")

            # 一時ディレクトリを削除
            shutil.rmtree(temp_dir)
