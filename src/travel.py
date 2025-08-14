import streamlit as st
from .data import get_tms, add_travel_mate, close_travel_mate


def render_travel_page():
    st.subheader("여행메이트 게시판")
    df = get_tms().copy()

    with st.expander("🔎 필터"):
        colf1, colf2, colf3 = st.columns(3)
        with colf1:
            dep = st.text_input("출발 도시 예: Seoul/Busan")
        with colf2:
            dst = st.text_input("목적지 도시 예: Jeju/Busan")
        with colf3:
            status = st.selectbox("상태", ["전체","open","closed"], index=0)

    if dep: df = df[df["departure_city"].str.contains(dep, case=False, na=False)]
    if dst: df = df[df["destination_city"].str.contains(dst, case=False, na=False)]
    if status != "전체": df = df[df["status"] == status]
    df = df.sort_values("created_at", ascending=False)

    for _, r in df.iterrows():
        with st.container(border=True):
            st.markdown(f"**{r['title']}**")
            st.caption(f"{r['departure_city']} → {r['destination_city']} | {r['date_from']} ~ {r['date_to']} | 예산 {r['budget_range_krw']}원 | 교통 {r['preferred_transport']}")
            st.write(r["notes"])
            st.caption(f"연락처: {r['contact']} · 상태: {r['status']} · 등록: {r['created_at']}")
            if st.session_state.get("user") and int(st.session_state["user"]["user_id"]) == int(r["user_id"]):
                if st.button("마감하기", key=f"close_{int(r['mate_id'])}"):
                    close_travel_mate(int(r["mate_id"]))
                    st.experimental_rerun()

    st.divider()
    st.subheader("여행메이트 등록")
    if not st.session_state.get("user"):
        st.info("등록은 로그인 후 이용 가능합니다.")
        return

    c1, c2 = st.columns(2)
    with c1:
        title = st.text_input("제목", value="부산 주말 여행 메이트 구해요")
        dep_city = st.text_input("출발 도시", value="Seoul")
        dst_city = st.text_input("목적지 도시", value="Busan")
        date_from = st.date_input("시작일")
    with c2:
        date_to = st.date_input("종료일")
        budget = st.text_input("예산 범위(원)", value="150000-250000")
        transport = st.selectbox("교통수단", ["KTX", "Bus", "Flight", "Car"], index=0)
        contact = st.text_input("연락처", value=st.session_state["user"]["email"])
    notes = st.text_area("추가 메모", value="바닷가 산책, 맛집 좋아요")

    if st.button("등록"):
        add_travel_mate(
            int(st.session_state["user"]["user_id"]), title, dep_city, dst_city,
            date_from, date_to, budget, transport, contact, notes
        )
        st.success("여행메이트 등록 완료!")
        st.experimental_rerun()