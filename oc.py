import streamlit as st
import time
import os 
from PIL import Image
import predict
import shutil

st.set_page_config(page_title="犬猫分類AI", layout="centered")
st.write('# AIで画像を分類しよう！')

# keep_dir = 'dog_vs_cat\\dog_vs_cat\\keep'
keep_dir = os.path.join(os.path.dirname(__file__), "keep")
if not os.path.exists(keep_dir):
    os.makedirs(keep_dir, exist_ok=True)

# セッションステートの初期化
if "result" not in st.session_state:
    st.session_state.result = None
    st.session_state.prob = None
    st.session_state.predicted = False

uploaded_file = st.file_uploader("画像を挿入してください", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="アップロードされた画像", width=500)
    

    # 保存しておく
    img_path = os.path.join(keep_dir, uploaded_file.name)
    Image.open(uploaded_file).save(img_path)

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
    if os.path.exists(keep_dir):
        shutil.rmtree(keep_dir)
    # 状態もリセット
    st.session_state.result = None
    st.session_state.prob = None
    st.session_state.predicted = False
