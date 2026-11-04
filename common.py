import streamlit as st


def require_student():
    """이름을 입력하지 않았으면 시작하기 화면으로 안내하고 멈춘다."""
    name = st.session_state.get("student", "")
    if not name:
        st.info("먼저 **시작하기** 화면에서 학번과 이름을 입력해 주세요.")
        st.page_link("pages_src/home.py", label="시작하기로 가기", icon=":material/arrow_back:")
        st.stop()
    st.caption(f"👤 {name}")
    return name
