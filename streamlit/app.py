import streamlit as st
import pandas as pd
import time

# 2乗の計算
st.write("# 2乗の計算")
input_num = st.number_input('Input a number', value=0)

result = input_num ** 2
st.write('Result', result)

# タイトル表示
st.title('streamlit Tutorial')

# ヘッダーの表示
st.header('This is a header')

# サブヘッダーの表示
st.subheader('This is a subheader')

# テキストの表示
st.text('Hello World!')

# リストの表示
st.write(['apple', 'orange', 'banana'])

# DataFrameの表示
df = pd.DataFrame({
    'name': ['Alice', 'Bob'],
    'age': [25, 30],
    'gender': ['female', 'male']
})
st.write(df)

# ファイルのアップロード
uploaded_file = st.file_uploader("choose a file")
if uploaded_file is not None:
    st.write(uploaded_file)

# ボタンの表示
if st.button('say hello'):
    st.write('hello world!')

# チェックボックスの表示
if st.checkbox('show/hide'):
    st.write('some text')

# ラジオボタンの表示
option = st.radio(
    'which number do you like best?',
    ['1', '2', '3']
)

# セレクトボックスの表示
option = st.selectbox(
    'which number do you like best?',
    ['1', '2', '3']
)

# マルチセレクトボックスの表示
options = st.multiselect(
    'What are your favorite colors',
    ['green', 'yellow', 'red', 'blue'],
    default=['yellow', 'red']
)

# スライダーの表示
value = st.slider('select a value', 0, 100, 30)

# テキスト入力ボックス
text_input = st.text_input('Input', 'Input some text here.')

# テキストエリア
text_area = st.text_area('Text Area', 'Input some text here.')

# ボタンを押したら3秒間出力を持つ
if st.button('start'):
    with st.spinner('processing...'):
        time.sleep(3)
        st.write('end!')

# sidebarの選択肢を定義する
options = ["Option 1", "Option 2", "Option 3"]
choice = st.sidebar.selectbox("Select an option", options)

# Mainコンテンツの表示を変える
if choice == "Option 1":
    st.write("You selected Option 1")
elif choice == "Option 2":
    st.write("You selected Option 2")
else:
    st.write("You selected Option 3")