import streamlit as st
from src.analyze.classify_text import classify_text

st.title("応募する前に、このAIに文章を投げろ。")
st.subheader("犯罪に手を染める前に。")

text = st.text_area("怪しいと思った募集文をここに貼り付けてください")

if st.button("AIに判定してもらう"):
    if text.strip():
        result = classify_text(text)
        st.json(result)
    else:
        st.warning("文章を入力してください。")
