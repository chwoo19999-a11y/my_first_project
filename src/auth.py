import streamlit as st
import hashlib
from .data import get_users, add_user


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def render_auth_sidebar():
    users = get_users()

    st.sidebar.header("로그인")
    login_user = st.sidebar.text_input("아이디")
    login_pw = st.sidebar.text_input("비밀번호", type="password")
    if st.sidebar.button("로그인"):
        if not login_user or not login_pw:
            st.sidebar.error("아이디/비밀번호를 입력하세요.")
        else:
            row = users[users["username"] == login_user]
            if len(row) == 1 and row.iloc[0]["password_sha256"] == _sha256(login_pw):
                st.session_state["user"] = dict(row.iloc[0])
                st.sidebar.success(f"어서오세요, {login_user}님!")
            else:
                st.sidebar.error("로그인 실패")

    st.sidebar.divider()
    st.sidebar.caption("처음이신가요?")
    with st.sidebar.expander("회원가입"):
        su_user = st.text_input("새 아이디", key="su_user")
        su_email = st.text_input("이메일", key="su_email")
        su_pw = st.text_input("새 비밀번호", type="password", key="su_pw")
        if st.button("가입하기"):
            if su_user and su_email and su_pw:
                ok, info = add_user(su_user, _sha256(su_pw), su_email)
                if ok:
                    st.success("가입 완료! 사이드바에서 로그인 해주세요.")
                else:
                    st.warning(info)
            else:
                st.warning("필수 정보를 입력해주세요.")

    if "user" in st.session_state and st.session_state["user"]:
        st.sidebar.caption(f"현재 로그인: **{st.session_state['user']['username']}**")
        if st.sidebar.button("로그아웃"):
            st.session_state["user"] = None
            st.experimental_rerun()