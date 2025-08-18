import streamlit as st
import pandas as pd
from .data import get_users, get_posts, add_post, inc_repost


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

    # 현재 로그인한 사용자 정보
    current_user = st.session_state.get("user")
    current_user_id = int(current_user["user_id"]) if current_user else None

    for _, row in df.iterrows():
        with st.container(border=True):
            st.markdown(f"**@{_username(users, int(row['user_id']))}** · {row['created_at']}")
            st.write(row["content"])
            st.caption(f"태그: {row['tags']}  |  ❤️ {int(row['likes'])}  🔁 {int(row['reposts'])}")

            # 현재 사용자가 이 게시글을 좋아요 했는지 확인
            post_id = int(row['post_id'])
            user_liked = False
            
            if current_user_id:
                try:
                    from .data import is_post_liked_by_user
                    user_liked = is_post_liked_by_user(post_id, current_user_id)
                except ImportError:
                    # 새로운 함수가 없으면 기존 방식 유지
                    pass

            # 테스트용: 모든 게시글에 삭제 버튼 표시 (임시)
            is_author = True  # 테스트용으로 모든 사용자에게 표시
            # is_author = current_user_id and current_user_id == int(row['user_id'])  # 원래 코드
            
            # 디버깅 정보 출력
            st.caption(f"현재 사용자 ID: {current_user_id}, 게시글 작성자 ID: {int(row['user_id'])}, 작성자 여부: {is_author}")
            
            # 모든 게시글에 삭제 버튼 표시 (테스트용)
            c1, c2, c3 = st.columns(3)
            
            with c1:
                # 좋아요 버튼 - 상태에 따라 다른 스타일과 텍스트
                if current_user_id:
                    if user_liked:
                        like_button_text = "💖 좋아요 취소"
                        like_button_type = "primary"
                    else:
                        like_button_text = "🤍 좋아요"
                        like_button_type = "secondary"
                        
                    if st.button(like_button_text, key=f"like_{post_id}", type=like_button_type):
                        try:
                            from .data import toggle_like
                            result = toggle_like(post_id, current_user_id)
                            
                            if result["liked"]:
                                st.success("👍 좋아요!")
                            else:
                                st.info("👋 좋아요 취소")
                                
                            _safe_rerun()
                        except ImportError:
                            st.error("좋아요 기능이 구현되지 않았습니다.")
                        except Exception as e:
                            st.error(f"좋아요 처리 중 오류: {str(e)}")
                else:
                    # 로그인하지 않은 사용자
                    if st.button("🤍 좋아요 (로그인 필요)", key=f"like_{post_id}", disabled=True):
                        pass
                        
            with c2:
                if st.button("🔁 리포스트", key=f"re_{post_id}"):
                    inc_repost(post_id)
                    _safe_rerun()
            with c3:
                if st.button("🗑️ 삭제", key=f"del_{post_id}", type="secondary"):
                    st.session_state[f"confirm_delete_{post_id}"] = True
                    _safe_rerun()
            
            # 삭제 확인 처리
            if st.session_state.get(f"confirm_delete_{int(row['post_id'])}", False):
                st.warning("⚠️ 정말로 이 게시글을 삭제하시겠습니까?")
                col_yes, col_no = st.columns(2)
                
                with col_yes:
                    if st.button("✅ 예, 삭제합니다", key=f"confirm_yes_{int(row['post_id'])}", type="primary"):
                        # data.py에 delete_post 함수가 있다고 가정
                        try:
                            from .data import delete_post
                            delete_post(int(row['post_id']))
                            st.success("게시글이 삭제되었습니다.")
                            # 확인 상태 초기화
                            if f"confirm_delete_{int(row['post_id'])}" in st.session_state:
                                del st.session_state[f"confirm_delete_{int(row['post_id'])}"]
                            _safe_rerun()
                        except ImportError:
                            st.error("삭제 기능이 구현되지 않았습니다. data.py에 delete_post 함수를 추가해주세요.")
                        except Exception as e:
                            st.error(f"삭제 중 오류가 발생했습니다: {str(e)}")
                
                with col_no:
                    if st.button("❌ 아니요, 취소", key=f"confirm_no_{int(row['post_id'])}"):
                        # 확인 상태 초기화
                        if f"confirm_delete_{int(row['post_id'])}" in st.session_state:
                            del st.session_state[f"confirm_delete_{int(row['post_id'])}"]
                        _safe_rerun()


def render_write_page():
    if not st.session_state.get("user"):
        st.info("글쓰기는 로그인 후 이용 가능합니다.")
        return

    st.subheader("새 게시글 작성")
    
    # 게시 완료 후 초기화를 위한 플래그
    if "post_submitted" not in st.session_state:
        st.session_state.post_submitted = False
    
    # 게시 완료 후에는 빈 값으로 시작
    default_content = "" if st.session_state.post_submitted else ""
    default_tags = "community,india" if not st.session_state.post_submitted else "community,india"
    
    # key 없이 위젯 사용 (자동으로 관리됨)
    content = st.text_area("내용", value=default_content)
    tags = st.text_input("태그 (쉼표로 구분)", value=default_tags)

    if st.button("게시"):
        if content.strip():
            add_post(int(st.session_state["user"]["user_id"]), content.strip(), tags.strip())
            st.session_state.post_submitted = True  # 플래그 설정
            st.success("게시 완료!")
            _safe_rerun()  # ✅ 새로고침으로 폼 초기화
        else:
            st.warning("내용을 입력해주세요.")
    
    # 한 번 새로고침 후 플래그 리셋
    if st.session_state.post_submitted:
        st.session_state.post_submitted = False