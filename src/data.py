import pandas as pd
import json
import os
from datetime import datetime

# 데이터 파일 경로
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.csv")
POSTS_FILE = os.path.join(DATA_DIR, "posts.csv")
USER_LIKES_FILE = os.path.join(DATA_DIR, "user_likes.json")
TRAVEL_MATES_FILE = os.path.join(DATA_DIR, "travel_mates.csv")

# 데이터 디렉토리 생성
os.makedirs(DATA_DIR, exist_ok=True)

# =============================================================================
# 여행메이트 관련 함수들
# =============================================================================

def get_tms() -> pd.DataFrame:
    """여행메이트 목록을 반환 (TMS = Travel Mate System)"""
    if os.path.exists(TRAVEL_MATES_FILE):
        return pd.read_csv(TRAVEL_MATES_FILE)
    else:
        # 기본 여행메이트 데이터 생성
        travel_data = {
            "tm_id": [1, 2, 3],
            "user_id": [1, 2, 1],
            "departure_city": ["서울", "부산", "인천"],
            "destination_city": ["델리", "뭄바이", "델리"],
            "travel_date": ["2024-09-01", "2024-09-15", "2024-10-01"],
            "duration": ["7일", "10일", "5일"],
            "description": [
                "델리 관광지 함께 둘러봐요!",
                "뭄바이에서 볼리우드 투어 하실 분",
                "델리 맛집 탐방 같이 해요"
            ],
            "max_people": [3, 2, 4],
            "current_people": [1, 1, 2],
            "status": ["open", "open", "open"],
            "created_at": [
                "2024-08-10 09:00:00",
                "2024-08-12 14:30:00",
                "2024-08-14 16:45:00"
            ]
        }
        df = pd.DataFrame(travel_data)
        df.to_csv(TRAVEL_MATES_FILE, index=False)
        return df

def add_travel_mate(user_id: int, departure_city: str, destination_city: str, 
                   travel_date: str, duration: str, description: str, max_people: int) -> bool:
    """새 여행메이트 모집글 추가"""
    try:
        tms_df = get_tms()
        
        # 새 여행메이트 ID 생성
        new_tm_id = tms_df["tm_id"].max() + 1 if len(tms_df) > 0 else 1
        
        # 새 여행메이트 모집글 추가
        new_tm = pd.DataFrame({
            "tm_id": [new_tm_id],
            "user_id": [user_id],
            "departure_city": [departure_city],
            "destination_city": [destination_city],
            "travel_date": [travel_date],
            "duration": [duration],
            "description": [description],
            "max_people": [max_people],
            "current_people": [1],  # 작성자 포함
            "status": ["open"],
            "created_at": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        })
        
        tms_df = pd.concat([tms_df, new_tm], ignore_index=True)
        tms_df.to_csv(TRAVEL_MATES_FILE, index=False)
        return True
    except Exception as e:
        print(f"여행메이트 추가 오류: {e}")
        return False

def close_travel_mate(tm_id: int) -> bool:
    """여행메이트 모집 마감"""
    try:
        tms_df = get_tms()
        
        # 해당 tm_id가 존재하는지 확인
        if tm_id not in tms_df["tm_id"].values:
            return False
        
        # 상태를 'closed'로 변경
        tms_df.loc[tms_df["tm_id"] == tm_id, "status"] = "closed"
        tms_df.to_csv(TRAVEL_MATES_FILE, index=False)
        return True
    except Exception as e:
        print(f"여행메이트 마감 오류: {e}")
        return False

def join_travel_mate(tm_id: int, user_id: int) -> bool:
    """여행메이트에 참가"""
    try:
        tms_df = get_tms()
        
        # 해당 여행메이트 찾기
        tm_mask = tms_df["tm_id"] == tm_id
        tm_row = tms_df[tm_mask]
        
        if len(tm_row) == 0:
            return False
        
        current_people = int(tm_row.iloc[0]["current_people"])
        max_people = int(tm_row.iloc[0]["max_people"])
        status = tm_row.iloc[0]["status"]
        
        # 참가 가능한지 확인
        if status != "open" or current_people >= max_people:
            return False
        
        # 참가자 수 증가
        tms_df.loc[tm_mask, "current_people"] = current_people + 1
        
        # 정원이 다 찼으면 자동으로 마감
        if current_people + 1 >= max_people:
            tms_df.loc[tm_mask, "status"] = "full"
        
        tms_df.to_csv(TRAVEL_MATES_FILE, index=False)
        return True
    except Exception as e:
        print(f"여행메이트 참가 오류: {e}")
        return False

def delete_travel_mate(tm_id: int) -> bool:
    """여행메이트 모집글 삭제"""
    try:
        tms_df = get_tms()
        
        # 해당 tm_id가 존재하는지 확인
        if tm_id not in tms_df["tm_id"].values:
            return False
        
        # 해당 모집글 삭제
        tms_df = tms_df[tms_df["tm_id"] != tm_id]
        tms_df.to_csv(TRAVEL_MATES_FILE, index=False)
        return True
    except Exception as e:
        print(f"여행메이트 삭제 오류: {e}")
        return False

# =============================================================================
# 사용자 관련 함수들
# =============================================================================

def get_users() -> pd.DataFrame:
    """사용자 목록을 반환"""
    if os.path.exists(USERS_FILE):
        return pd.read_csv(USERS_FILE)
    else:
        # 기본 사용자 데이터 생성
        users_data = {
            "user_id": [1, 2, 3],
            "username": ["alice", "bob", "charlie"],
            "email": ["alice@email.com", "bob@email.com", "charlie@email.com"],
            "password": ["password123", "password123", "password123"]  # 실제로는 해시화해야 함
        }
        df = pd.DataFrame(users_data)
        df.to_csv(USERS_FILE, index=False)
        return df

def add_user(username: str, email: str, password: str) -> bool:
    """새 사용자 추가"""
    try:
        users_df = get_users()
        
        # 중복 사용자명/이메일 체크
        if username in users_df["username"].values:
            return False
        if email in users_df["email"].values:
            return False
        
        # 새 사용자 ID 생성
        new_user_id = users_df["user_id"].max() + 1 if len(users_df) > 0 else 1
        
        # 새 사용자 추가
        new_user = pd.DataFrame({
            "user_id": [new_user_id],
            "username": [username],
            "email": [email],
            "password": [password]  # 실제로는 해시화해야 함
        })
        
        users_df = pd.concat([users_df, new_user], ignore_index=True)
        users_df.to_csv(USERS_FILE, index=False)
        return True
    except Exception as e:
        print(f"사용자 추가 오류: {e}")
        return False

def verify_user(username: str, password: str) -> dict:
    """사용자 인증"""
    try:
        users_df = get_users()
        user_row = users_df[
            (users_df["username"] == username) & (users_df["password"] == password)
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
        user_likes = get_user_likes()
        
        return {
            "total_users": len(users_df),
            "total_posts": len(posts_df),
            "total_likes": posts_df["likes"].sum(),
            "total_reposts": posts_df["reposts"].sum(),
            "active_likers": len(user_likes)
        }
    except Exception as e:
        print(f"통계 조회 오류: {e}")
        return {}

if __name__ == "__main__":
    # 테스트 실행
    initialize_data()
    print("데이터 파일이 생성되었습니다.")
    print(f"통계: {get_user_statistics()}")