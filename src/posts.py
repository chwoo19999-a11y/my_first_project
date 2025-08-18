import streamlit as st
import pandas as pd
from .data import get_users, get_posts, add_post, inc_like, inc_repost


def _username(users: pd.DataFrame, user_id: int) -> str:
    row = users[users["user_id"] == user_id]
    return row.iloc[0]["username"] if len(row) else "알수없음"


def _safe_rerun():
    # Streamlit 버전에 따라 지원 함수가 다를 수 있어 방어적으로 처리
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()


def render_feed_page():
    st.subheader("타임라인")
    users = get_users()
    posts = get_posts()

    col1, col2 = st.columns([2, 1])
    with col1:
        q = st.text_input("검색어(내용/태그)")
    with col2:
        order = st.selectbox("정렬", ["최신순", "좋아요순"])

    df = posts.copy()
    if q:
        ql = q.lower()
        df = df[
            df["content"].str.lower().str.contains(ql, na=False)
            | df["tags"].str.lower().str.contains(ql, na=False)
        ]

    if order == "최신순":
        df = df.sort_values("created_at", ascending=False)
    else:
        df = df.sort_values("likes", ascending=False)

    for _, row in df.iterrows():
        with st.container(border=True):
            st.markdown(f"**@{_username(users, int(row['user_id']))}** · {row['created_at']}")
            st.write(row["content"])
            st.caption(f"태그: {row['tags']}  |  ❤️ {int(row['likes'])}  🔁 {int(row['reposts'])}")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("좋아요", key=f"like_{int(row['post_id'])}"):
                    inc_like(int(row["post_id"]))
                    _safe_rerun()  # ✅ 새로고침
            with c2:
                if st.button("리포스트", key=f"re_{int(row['post_id'])}"):
                    inc_repost(int(row["post_id"]))
                    _safe_rerun()  # ✅ 새로고침


def render_write_page():
    if not st.session_state.get("user"):
        st.info("글쓰기는 로그인 후 이용 가능합니다.")
        return

    st.subheader("새 게시글 작성")
    # 입력값을 session_state로 관리하면 게시 후 초기화가 쉬워요
    content = st.text_area("내용", key="write_content")
    tags = st.text_input("태그 (쉼표로 구분)", value="community,india", key="write_tags")

    if st.button("게시"):
        if content.strip():
            add_post(int(st.session_state["user"]["user_id"]), content.strip(), tags.strip())
            # 입력란 초기화
            st.session_state["write_content"] = ""
            st.session_state["write_tags"] = "community,india"
            st.success("게시 완료!")
            _safe_rerun()  # ✅ 목록 갱신
        else:
            st.warning("내용을 입력해주세요.")
