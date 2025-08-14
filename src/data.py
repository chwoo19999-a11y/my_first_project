import os
import pandas as pd
import streamlit as st
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

USERS_CSV = os.path.join(DATA_DIR, "users.csv")
POSTS_CSV = os.path.join(DATA_DIR, "posts.csv")
TMS_CSV = os.path.join(DATA_DIR, "travel_mates.csv")
COMMENTS_CSV = os.path.join(DATA_DIR, "comments.csv")

os.makedirs(DATA_DIR, exist_ok=True)

EMPTY = {
    USERS_CSV: ["user_id","username","password_sha256","email","country","city_in_korea","joined_at"],
    POSTS_CSV: ["post_id","user_id","content","tags","created_at","likes","reposts"],
    TMS_CSV:   ["mate_id","user_id","title","departure_city","destination_city","date_from","date_to","budget_range_krw","preferred_transport","contact","notes","status","created_at"],
    COMMENTS_CSV: ["comment_id","post_id","user_id","content","created_at"],
}

# 공통 로드/세이브
@st.cache_data
def load_csv(path: str) -> pd.DataFrame:
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame(columns=EMPTY[path])

def save_csv(df: pd.DataFrame, path: str):
    df.to_csv(path, index=False)
    st.cache_data.clear()  # 캐시 무효화

# ID 채번
def next_id(df: pd.DataFrame, col: str) -> int:
    return int(df[col].max() + 1) if len(df) and pd.notna(df[col]).any() else 1

# 퍼사드: 각 테이블 접근자

def get_users():
    return load_csv(USERS_CSV)

def get_posts():
    return load_csv(POSTS_CSV)

def get_tms():
    return load_csv(TMS_CSV)

def get_comments():
    return load_csv(COMMENTS_CSV)

# 변이 작업: 사용자/게시글/여행메이트

def add_user(username, pw_hash, email, country="India", city="Seoul"):
    users = get_users()
    if (users["username"] == username).any():
        return False, "이미 존재하는 아이디"
    uid = next_id(users, "user_id")
    users.loc[len(users)] = [uid, username, pw_hash, email, country, city, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    save_csv(users, USERS_CSV)
    return True, uid


def add_post(user_id: int, content: str, tags: str):
    posts = get_posts()
    pid = next_id(posts, "post_id")
    posts.loc[len(posts)] = [pid, user_id, content, tags, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 0]
    save_csv(posts, POSTS_CSV)


def inc_like(post_id: int):
    posts = get_posts()
    posts.loc[posts["post_id"] == post_id, "likes"] = posts.loc[posts["post_id"] == post_id, "likes"].astype(int) + 1
    save_csv(posts, POSTS_CSV)


def inc_repost(post_id: int):
    posts = get_posts()
    posts.loc[posts["post_id"] == post_id, "reposts"] = posts.loc[posts["post_id"] == post_id, "reposts"].astype(int) + 1
    save_csv(posts, POSTS_CSV)


def add_travel_mate(user_id, title, dep, dst, dfrom, dto, budget, transport, contact, notes):
    tms = get_tms()
    mid = next_id(tms, "mate_id")
    tms.loc[len(tms)] = [mid, user_id, title, dep, dst, str(dfrom), str(dto), budget, transport, contact, notes, "open", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    save_csv(tms, TMS_CSV)


def close_travel_mate(mate_id: int):
    tms = get_tms()
    tms.loc[tms["mate_id"] == mate_id, "status"] = "closed"
    save_csv(tms, TMS_CSV)