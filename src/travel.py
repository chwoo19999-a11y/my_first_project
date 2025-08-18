import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from .data import get_users, get_tms, add_travel_mate, close_travel_mate

# 데이터 파일 경로
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.csv")
POSTS_FILE = os.path.join(DATA_DIR, "posts.csv")
TMS_FILE = os.path.join(DATA_DIR, "travel_mates.csv")  # 추가
USER_LIKES_FILE = os.path.join(DATA_DIR, "user_likes.json")

# 데이터 디렉토리 생성
os.makedirs(DATA_DIR, exist_ok=True)

# =============================================================================
# 사용자 관련 함수들
# =============================================================================

def get_users() -> pd.DataFrame:
    """사용자 목록을 반환"""
    if os.path.exists(USERS_FILE):
        return pd.read_csv(USERS_FILE)
    else:
        # 기본 사용자 데이터 생성 - 해시화된 비밀번호 사용
        users_data = {
            "user_id": [1, 2, 3],
            "username": ["alice", "bob", "charlie"],
            "email": ["alice@email.com", "bob@email.com", "charlie@email.com"],
            "password_sha256": [
                "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f",  # password123
                "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f",  # password123
                "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f"   # password123
            ]
        }
        df = pd.DataFrame(users_data)
        df.to_csv(USERS_FILE, index=False)
        return df

def add_user(username: str, password_sha256: str, email: str) -> tuple:
    """새 사용자 추가"""
    try:
        users_df = get_users()
        
        # 중복 사용자명/이메일 체크
        if username in users_df["username"].values:
            return False, "이미 존재하는 사용자명입니다."
        if email in users_df["email"].values:
            return False, "이미 존재하는 이메일입니다."
        
        # 새 사용자 ID 생성
        new_user_id = users_df["user_id"].max() + 1 if len(users_df) > 0 else 1
        
        # 새 사용자 추가
        new_user = pd.DataFrame({
            "user_id": [new_user_id],
            "username": [username],
            "email": [email],
            "password_sha256": [password_sha256]
        })
        
        users_df = pd.concat([users_df, new_user], ignore_index=True)
        users_df.to_csv(USERS_FILE, index=False)
        return True, "회원가입 성공"
    except Exception as e:
        print(f"사용자 추가 오류: {e}")
        return False, f"오류가 발생했습니다: {e}"

def verify_user(username: str, password_sha256: str) -> dict:
    """사용자 인증"""
    try:
        users_df = get_users()
        user_row = users_df[
            (users_df["username"] == username) & (users_df["password_sha256"] == password_sha256)
        ]
        
        if len(user_row) > 0:
            return {
                "user_id": int(user_row.iloc[0]["user_id"]),
                "username": user_row.iloc[0]["username"],
                "email": user_row.iloc[0]["email"]
            }
        return {}
    except Exception as e:
        print(f"사용자 인증 오류: {e}")
        return {}

# =============================================================================
# 게시글 관련 함수들
# =============================================================================

def get_posts() -> pd.DataFrame:
    """게시글 목록을 반환"""
    if os.path.exists(POSTS_FILE):
        return pd.read_csv(POSTS_FILE)
    else:
        # 기본 게시글 데이터 생성
        posts_data = {
            "post_id": [1, 2, 3],
            "user_id": [1, 2, 1],
            "content": [
                "안녕하세요! 인도 여행 중입니다. 🇮🇳",
                "델리에서 맛있는 카레 맛집을 찾고 있어요!",
                "바라나시 갠지스 강 일출이 정말 아름다워요 ✨"
            ],
            "tags": ["india,travel", "delhi,food", "varanasi,ganges"],
            "likes": [5, 3, 8],
            "reposts": [1, 0, 2],
            "created_at": [
                "2024-08-15 10:30:00",
                "2024-08-15 14:20:00", 
                "2024-08-16 07:15:00"
            ]
        }
        df = pd.DataFrame(posts_data)
        df.to_csv(POSTS_FILE, index=False)
        return df

def add_post(user_id: int, content: str, tags: str) -> bool:
    """새 게시글 추가"""
    try:
        posts_df = get_posts()
        
        # 새 게시글 ID 생성
        new_post_id = posts_df["post_id"].max() + 1 if len(posts_df) > 0 else 1
        
        # 새 게시글 추가
        new_post = pd.DataFrame({
            "post_id": [new_post_id],
            "user_id": [user_id],
            "content": [content],
            "tags": [tags],
            "likes": [0],
            "reposts": [0],
            "created_at": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        })
        
        posts_df = pd.concat([posts_df, new_post], ignore_index=True)
        posts_df.to_csv(POSTS_FILE, index=False)
        return True
    except Exception as e:
        print(f"게시글 추가 오류: {e}")
        return False

def delete_post(post_id: int) -> bool:
    """게시글 삭제"""
    try:
        posts_df = get_posts()
        
        # 해당 post_id가 존재하는지 확인
        if post_id not in posts_df["post_id"].values:
            return False
        
        # 해당 게시글 삭제
        posts_df = posts_df[posts_df["post_id"] != post_id]
        posts_df.to_csv(POSTS_FILE, index=False)
        
        # 해당 게시글의 좋아요 정보도 삭제
        _remove_post_from_likes(post_id)
        
        return True
    except Exception as e:
        print(f"게시글 삭제 오류: {e}")
        return False

def inc_repost(post_id: int) -> bool:
    """리포스트 수 증가"""
    try:
        posts_df = get_posts()
        posts_df.loc[posts_df["post_id"] == post_id, "reposts"] += 1
        posts_df.to_csv(POSTS_FILE, index=False)
        return True
    except Exception as e:
        print(f"리포스트 증가 오류: {e}")
        return False

# =============================================================================
# 여행메이트 관련 함수들 (travel.py에서 필요)
# =============================================================================

def get_tms() -> pd.DataFrame:
    """여행메이트 목록을 반환"""
    if os.path.exists(TMS_FILE):
        return pd.read_csv(TMS_FILE)
    else:
        # 기본 여행메이트 데이터 생성
        tms_data = {
            "mate_id": [1, 2],
            "user_id": [1, 2],
            "title": ["델리-아그라 당일치기 메이트 구해요", "라자스탄 일주 여행 동행자 모집"],
            "departure_city": ["Delhi", "Jaipur"],
            "destination_city": ["Agra", "Udaipur"],
            "date_from": ["2024-08-20", "2024-09-01"],
            "date_to": ["2024-08-20", "2024-09-07"],
            "budget_range_krw": ["100000-150000", "300000-500000"],
            "preferred_transport": ["Car", "Bus"],
            "contact": ["alice@email.com", "bob@email.com"],
            "notes": ["타지마할 관람, 맛집 탐방", "왕궁, 호수, 사막 투어"],
            "status": ["open", "open"],
            "created_at": ["2024-08-15 10:00:00", "2024-08-15 15:30:00"]
        }
        df = pd.DataFrame(tms_data)
        df.to_csv(TMS_FILE, index=False)
        return df

def add_travel_mate(user_id: int, title: str, departure_city: str, destination_city: str,
                   date_from, date_to, budget_range_krw: str, preferred_transport: str,
                   contact: str, notes: str) -> bool:
    """새 여행메이트 등록"""
    try:
        tms_df = get_tms()
        
        # 새 메이트 ID 생성
        new_mate_id = tms_df["mate_id"].max() + 1 if len(tms_df) > 0 else 1
        
        # 새 여행메이트 추가
        new_mate = pd.DataFrame({
            "mate_id": [new_mate_id],
            "user_id": [user_id],
            "title": [title],
            "departure_city": [departure_city],
            "destination_city": [destination_city],
            "date_from": [str(date_from)],
            "date_to": [str(date_to)],
            "budget_range_krw": [budget_range_krw],
            "preferred_transport": [preferred_transport],
            "contact": [contact],
            "notes": [notes],
            "status": ["open"],
            "created_at": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        })
        
        tms_df = pd.concat([tms_df, new_mate], ignore_index=True)
        tms_df.to_csv(TMS_FILE, index=False)
        return True
    except Exception as e:
        print(f"여행메이트 추가 오류: {e}")
        return False

def close_travel_mate(mate_id: int) -> bool:
    """여행메이트 마감"""
    try:
        tms_df = get_tms()
        tms_df.loc[tms_df["mate_id"] == mate_id, "status"] = "closed"
        tms_df.to_csv(TMS_FILE, index=False)
        return True
    except Exception as e:
        print(f"여행메이트 마감 오류: {e}")
        return False

# =============================================================================
# 개선된 좋아요 시스템
# =============================================================================

def get_user_likes() -> dict:
    """사용자별 좋아요 상태를 반환"""
    if os.path.exists(USER_LIKES_FILE):
        try:
            with open(USER_LIKES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

def save_user_likes(user_likes: dict) -> bool:
    """사용자별 좋아요 상태를 저장"""
    try:
        with open(USER_LIKES_FILE, "w", encoding="utf-8") as f:
            json.dump(user_likes, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"좋아요 데이터 저장 오류: {e}")
        return False

def is_post_liked_by_user(post_id: int, user_id: int) -> bool:
    """사용자가 특정 게시글을 좋아요 했는지 확인"""
    user_likes = get_user_likes()
    user_key = str(user_id)
    post_key = str(post_id)
    
    if user_key not in user_likes:
        return False
    
    return post_key in user_likes[user_key]

def toggle_like(post_id: int, user_id: int) -> dict:
    """
    좋아요를 토글하고 결과를 반환
    
    Returns:
        dict: {"liked": bool, "like_count": int, "success": bool}
    """
    try:
        # 현재 사용자별 좋아요 상태 가져오기
        user_likes = get_user_likes()
        user_key = str(user_id)
        post_key = str(post_id)
        
        # 사용자가 이미 이 게시글을 좋아요 했는지 확인
        if user_key not in user_likes:
            user_likes[user_key] = []
        
        user_liked_posts = user_likes[user_key]
        is_currently_liked = post_key in user_liked_posts
        
        # 게시글 데이터 가져오기
        posts_df = get_posts()
        post_mask = posts_df["post_id"] == post_id
        post_row = posts_df[post_mask]
        
        if len(post_row) == 0:
            return {"liked": False, "like_count": 0, "success": False}
        
        current_likes = int(post_row.iloc[0]["likes"])
        
        if is_currently_liked:
            # 좋아요 취소
            user_liked_posts.remove(post_key)
            new_like_count = max(0, current_likes - 1)  # 0보다 작아지지 않도록
            liked = False
        else:
            # 좋아요 추가
            user_liked_posts.append(post_key)
            new_like_count = current_likes + 1
            liked = True
        
        # 사용자 좋아요 상태 저장
        user_likes[user_key] = user_liked_posts
        save_user_likes(user_likes)
        
        # 게시글의 좋아요 수 업데이트
        posts_df.loc[post_mask, "likes"] = new_like_count
        posts_df.to_csv(POSTS_FILE, index=False)
        
        return {"liked": liked, "like_count": new_like_count, "success": True}
        
    except Exception as e:
        print(f"좋아요 토글 오류: {e}")
        return {"liked": False, "like_count": 0, "success": False}

def _remove_post_from_likes(post_id: int) -> bool:
    """게시글 삭제 시 해당 게시글의 좋아요 정보도 제거"""
    try:
        user_likes = get_user_likes()
        post_key = str(post_id)
        
        # 모든 사용자의 좋아요 목록에서 해당 게시글 제거
        for user_id in user_likes:
            if post_key in user_likes[user_id]:
                user_likes[user_id].remove(post_key)
        
        save_user_likes(user_likes)
        return True
    except Exception as e:
        print(f"게시글 좋아요 정보 삭제 오류: {e}")
        return False

# =============================================================================
# 기존 호환성을 위한 함수 (deprecated)
# =============================================================================

def inc_like(post_id: int) -> bool:
    """
    기존 호환성을 위한 함수 - 새 프로젝트에서는 toggle_like 사용 권장
    단순히 좋아요 수만 증가 (사용자 추적 없음)
    """
    try:
        posts_df = get_posts()
        posts_df.loc[posts_df["post_id"] == post_id, "likes"] += 1
        posts_df.to_csv(POSTS_FILE, index=False)
        return True
    except Exception as e:
        print(f"좋아요 증가 오류: {e}")
        return False

# =============================================================================
# 데이터 초기화 및 유틸리티 함수들
# =============================================================================

def initialize_data():
    """초기 데이터 설정"""
    print("데이터 초기화 중...")
    get_users()  # 사용자 데이터 생성
    get_posts()  # 게시글 데이터 생성
    get_tms()    # 여행메이트 데이터 생성
    print("데이터 초기화 완료!")

def get_user_statistics() -> dict:
    """사용자 통계 반환"""
    try:
        users_df = get_users()
        posts_df = get_posts()
        tms_df = get_tms()
        user_likes = get_user_likes()
        
        return {
            "total_users": len(users_df),
            "total_posts": len(posts_df),
            "total_travel_mates": len(tms_df),
            "total_likes": posts_df["likes"].sum(),
            "total_reposts": posts_df["reposts"].sum(),
            "active_likers": len(user_likes)
        }
    except Exception as e:
        print(f"통계 조회 오류: {e}")
        return {}

def _username(users: pd.DataFrame, user_id: int) -> str:
    row = users[users["user_id"] == user_id]
    return row.iloc[0]["username"] if len(row) else "알수없음"

def _safe_rerun():
    # Streamlit 버전에 따라 지원 함수가 다를 수 있어 방어적으로 처리
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()

def render_travel_page():
    st.subheader("여행 메이트 찾기")
    st.write("함께 인도 여행을 떠날 동행을 찾아보세요! 👋")

    # 여행 메이트 목록
    tms_df = get_tms()
    users_df = get_users()

    # 필터링 및 정렬
    col1, col2 = st.columns([2, 1])
    with col1:
        q = st.text_input("검색어(제목/내용)")
    with col2:
        order = st.selectbox("정렬", ["최신순", "마감되지 않은 게시글"])
    
    df = tms_df.copy()
    if q:
        ql = q.lower()
        df = df[
            df["title"].str.lower().str.contains(ql, na=False)
            | df["notes"].str.lower().str.contains(ql, na=False)
            | df["departure_city"].str.lower().str.contains(ql, na=False)
            | df["destination_city"].str.lower().str.contains(ql, na=False)
        ]

    if order == "최신순":
        df = df.sort_values("created_at", ascending=False)
    else:
        df = df[df["status"] == "open"]
        df = df.sort_values("created_at", ascending=False)
        st.info("⚠️ 현재 마감되지 않은 게시글만 표시하고 있습니다.")

    for _, row in df.iterrows():
        with st.container(border=True):
            st.markdown(f"**{row['title']}**")
            st.caption(f"작성자: **@{_username(users_df, int(row['user_id']))}** | 등록일: {row['created_at']}")
            st.write(f"✈️ **출발**: {row['departure_city']} → **도착**: {row['destination_city']}")
            st.write(f"🗓️ **기간**: {row['date_from']} ~ {row['date_to']}")
            st.write(f"💰 **예상 경비**: {row['budget_range_krw']} KRW")
            st.write(f"🔗 **연락 방법**: {row['contact']}")
            st.write(f"📝 **상세**: {row['notes']}")
            st.markdown(f"**상태**: `{row['status']}`")

            # 마감하기 버튼
            if st.session_state.get("user") and int(st.session_state["user"]["user_id"]) == int(row["user_id"]):
                if row["status"] == "open":
                    if st.button("✔️ 마감하기", key=f"close_tm_{int(row['mate_id'])}"):
                        close_travel_mate(int(row["mate_id"]))
                        st.success("게시글이 마감되었습니다.")
                        _safe_rerun()
                else:
                    st.button("✔️ 마감됨", key=f"close_tm_{int(row['mate_id'])}", disabled=True)
            

    st.divider()

    # 새 글 작성 섹션
    st.subheader("새 여행 메이트 모집글 작성")
    if not st.session_state.get("user"):
        st.info("여행 메이트 모집글은 로그인 후 작성 가능합니다.")
        return

    with st.form(key="add_travel_mate_form"):
        title = st.text_input("제목", max_chars=100)
        col_city1, col_city2 = st.columns(2)
        with col_city1:
            departure_city = st.text_input("출발 도시")
        with col_city2:
            destination_city = st.text_input("도착 도시")
        
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            date_from = st.date_input("출발일")
        with col_date2:
            date_to = st.date_input("도착일")
        
        budget_range = st.text_input("예상 경비 (범위, 예: 100000-200000)", help="단위는 KRW입니다.")
        preferred_transport = st.text_input("선호하는 이동 수단", help="예: 기차, 버스, 비행기, 렌터카 등")
        contact = st.text_input("연락 방법", help="예: 이메일, 카카오톡 ID, 오픈채팅 링크 등")
        notes = st.text_area("상세 내용", help="여행 스타일, 목적, 인원 등 자유롭게 작성해주세요.")
        
        submit_button = st.form_submit_button(label="등록하기")

    if submit_button:
        if title and departure_city and destination_city and date_from and date_to and contact:
            if add_travel_mate(
                user_id=int(st.session_state["user"]["user_id"]),
                title=title,
                departure_city=departure_city,
                destination_city=destination_city,
                date_from=date_from,
                date_to=date_to,
                budget_range_krw=budget_range,
                preferred_transport=preferred_transport,
                contact=contact,
                notes=notes
            ):
                st.success("새 여행 메이트 모집글이 성공적으로 등록되었습니다! 🎉")
                _safe_rerun()
            else:
                st.error("등록 중 오류가 발생했습니다.")
        else:
            st.warning("필수 정보를 모두 입력해주세요. (제목, 출발/도착 도시, 기간, 연락 방법)")

if __name__ == "__main__":
    # 테스트 실행
    initialize_data()
    print("데이터 파일이 생성되었습니다.")
    print(f"통계: {get_user_statistics()}")