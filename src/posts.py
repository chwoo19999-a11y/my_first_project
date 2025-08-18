import streamlit as st
import pandas as pd
from .data import get_users, get_posts, add_post, inc_repost, delete_post, toggle_like, is_post_liked_by_user

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
    current_user = st.session_state.get("user")

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
    
    # 게시글 렌더링
    for _, row in df.iterrows():
        with st.container(border=True):
            user_name = _username(users, int(row["user_id"]))
            st.markdown(f"**@{user_name}**", help=f"작성자 ID: {int(row['user_id'])}")
            st.write(row["content"])
            st.caption(f"태그: {row['tags']}")
            st.caption(f"작성 시간: {row['created_at']}")

            col_like, col_repost, col_delete = st.columns([1, 1, 4])
            post_id = int(row["post_id"])
            
            # 좋아요 버튼
            with col_like:
                liked_by_user = False
                if current_user:
                    liked_by_user = is_post_liked_by_user(post_id, int(current_user["user_id"]))
                
                like_count = int(row["likes"])
                like_label = "❤️" if liked_by_user else "🤍"
                if st.button(f"{like_label} {like_count}", key=f"like_{post_id}"):
                    if current_user:
                        toggle_like(post_id, int(current_user["user_id"]))
                        _safe_rerun()
                    else:
                        st.info("로그인해야 좋아요를 누를 수 있습니다.")

            # 리포스트 버튼
            with col_repost:
                if st.button(f"🔄 {row['reposts']}", key=f"repost_{post_id}"):
                    inc_repost(post_id)
                    _safe_rerun()
            
            # 삭제 버튼 (작성자만 보이게)
            with col_delete:
                is_author = current_user and int(current_user["user_id"]) == int(row["user_id"])
                if is_author:
                    confirm_key = f"confirm_delete_{post_id}"
                    if st.button("❌ 삭제", key=f"delete_{post_id}"):
                        st.session_state[confirm_key] = True

                    if st.session_state.get(confirm_key):
                        st.warning("정말 이 게시글을 삭제하시겠습니까?")
                        col_yes, col_no = st.columns(2)
                        
                        with col_yes:
                            if st.button("✅ 예, 삭제합니다", key=f"confirm_yes_{post_id}"):
                                delete_post(post_id)
                                st.session_state[confirm_key] = False
                                st.success("게시글이 삭제되었습니다.")
                                _safe_rerun()
                        
                        with col_no:
                            if st.button("❌ 아니요, 취소", key=f"confirm_no_{post_id}"):
                                if confirm_key in st.session_state:
                                    del st.session_state[confirm_key]
                                _safe_rerun()

def render_write_page():
    if not st.session_state.get("user"):
        st.info("글쓰기는 로그인 후 이용 가능합니다.")
        return

    st.subheader("새 게시글 작성")
    
    if "post_submitted" not in st.session_state:
        st.session_state.post_submitted = False
    
    default_content = "" if st.session_state.post_submitted else ""
    default_tags = "community,india" if not st.session_state.post_submitted else "community,india"
    
    content = st.text_area("내용", value=default_content)
    tags = st.text_input("태그 (쉼표로 구분)", value=default_tags)

    if st.button("게시"):
        if content.strip():
            add_post(int(st.session_state["user"]["user_id"]), content, tags)
            st.success("게시글이 성공적으로 작성되었습니다! 🎉")
            st.session_state.post_submitted = True
            _safe_rerun()
        else:
            st.error("내용을 입력해주세요.")