# app.py (최종 완성 버전)
import streamlit as st
from auth import show_auth_page, logout_user
from user_manager import UserManager
from post_manager import PostManager

# 페이지 설정
st.set_page_config(
    page_title="프롬프트 트위터",
    page_icon="🐦",
    layout="wide"
)

# 페이지 함수들 (위에서 구현한 것들)
def show_home_page(current_user, post_mgr, user_mgr):
    # 위에서 구현한 코드 그대로 사용
    pass

def show_write_page(current_user, post_mgr):
    # 위에서 구현한 코드 그대로 사용
    pass

def show_profile_page(current_user, post_mgr, user_mgr):
    # 위에서 구현한 코드 그대로 사용
    pass

# 매니저 초기화
@st.cache_resource
def init_managers():
    return UserManager(), PostManager()

user_mgr, post_mgr = init_managers()

# Session State 초기화
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'menu' not in st.session_state:
    st.session_state.menu = "🏠 홈"

# 로그인 체크
if not st.session_state.logged_in:
    show_auth_page()
else:
    current_user = st.session_state.current_user

    # 헤더
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("🐦 프롬프트 트위터")
        st.markdown(f"**{current_user['username']}님 환영합니다!** ✨")
    with col2:
        if st.button("🚪 로그아웃"):
            logout_user()

    # 메뉴
    menu = st.sidebar.selectbox(
        "📋 메뉴",
        ["🏠 홈", "✍️ 글쓰기", "👤 프로필"],
        index=["🏠 홈", "✍️ 글쓰기", "👤 프로필"].index(st.session_state.menu)
    )

    # 메뉴 변경 감지
    if menu != st.session_state.menu:
        st.session_state.menu = menu
        st.rerun()

    # 페이지 표시
    if menu == "🏠 홈":
        show_home_page(current_user, post_mgr, user_mgr)
    elif menu == "✍️ 글쓰기":
        show_write_page(current_user, post_mgr)
    elif menu == "👤 프로필":
        show_profile_page(current_user, post_mgr, user_mgr)


