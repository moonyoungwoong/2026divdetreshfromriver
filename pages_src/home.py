import streamlit as st

from common import LESSONS, TODAY

lesson = LESSONS[TODAY]

st.markdown("##### 하천 쓰레기 분류 AI 프로젝트")
st.title(lesson["title"])
st.write(lesson["intro"])

st.divider()

c1, c2 = st.columns([1, 1], gap="large")
with c1:
    st.subheader("내 정보")
    sid = st.text_input("학번", value=st.session_state.get("sid", ""), placeholder="예) 10203", key="sid_input")
    name = st.text_input("이름", value=st.session_state.get("sname", ""), placeholder="예) 김공주", key="name_input")
    if st.button("시작하기", type="primary", use_container_width=True):
        if not sid.strip() or not name.strip():
            st.error("학번과 이름을 모두 입력해 주세요.")
        else:
            st.session_state["sid"] = sid.strip()
            st.session_state["sname"] = name.strip()
            st.session_state["student"] = f"{sid.strip()} {name.strip()}"
            st.switch_page(lesson["page"])
    if st.session_state.get("student"):
        st.success(f"{st.session_state['student']} 님으로 참여 중입니다.")

with c2:
    st.subheader("오늘의 활동")
    st.markdown(lesson["plan"])
