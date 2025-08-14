import streamlit as st
from src.ui import setup_page
from src.auth import render_auth_sidebar
from src.posts import render_feed_page, render_write_page
from src.travel import render_travel_page

setup_page()  # 페이지 설정과 상단 타이틀만 담당

# 사이드바 로그인/회원가입 처리 (세션 상태 관리)
render_auth_sidebar()

# 네비게이션 (메뉴만 보유, 실제 화면 렌더는 각 모듈)
pages = {
    "🏠 홈": render_feed_page,
    "✍️ 글쓰기": render_write_page,
    "🧭 여행메이트": render_travel_page,
}
page = st.sidebar.radio("메뉴", list(pages.keys()))

# 선택된 페이지 실행
pages[page]()