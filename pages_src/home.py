import streamlit as st

st.markdown("##### 하천 쓰레기 분류 AI 프로젝트")
st.title("금강에 버려진 쓰레기, AI가 도울 수 있을까?")
st.write("오늘은 쓰레기를 직접 분류해 보고, 우리 AI 프로젝트가 해결할 문제를 정리합니다.")

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
            st.switch_page("pages_src/c1_sort.py")
    if st.session_state.get("student"):
        st.success(f"{st.session_state['student']} 님으로 참여 중입니다.")

with c2:
    st.subheader("오늘의 활동")
    st.markdown(
        """
        **① 5분 분류 체험**
        쓰레기 15개를 플라스틱 / 캔 / 유리 / 기타로 나눕니다.
        헷갈린 쓰레기도 표시해 주세요.

        **② 문제 정의서**
        금강 쓰레기 문제에서 AI가 할 일과 사람이 할 일을 정리합니다.
        """
    )
