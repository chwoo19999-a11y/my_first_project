import streamlit as st

def setup_page():
    st.set_page_config(
        page_title="재한 인도인 커뮤니티",
        page_icon="assets/india_flag_square_256.png",
        layout="wide",
    )
    st.title("🇮🇳 재한 인도인 커뮤니티")
    with st.sidebar:
        st.image("assets/india_flag_256x170.png", use_container_width=True)