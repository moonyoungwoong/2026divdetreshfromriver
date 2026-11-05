import streamlit as st

# 오늘 수업 차시. 학생이 '시작하기'를 누르면 이 차시의 첫 활동으로 이동합니다.
# 1차시 수업 날에는 1, 3차시 수업 날에는 3 으로 바꾸세요.
TODAY = 3

LESSONS = {
    1: {
        "page": "pages_src/c1_sort.py",
        "title": "금강에 버려진 쓰레기, AI가 도울 수 있을까?",
        "intro": "오늘은 쓰레기를 직접 분류해 보고, 우리 AI 프로젝트가 해결할 문제를 정리합니다.",
        "plan": """
        **① 5분 분류 체험**
        쓰레기 15개를 플라스틱 / 캔 / 유리 / 기타로 나눕니다.
        헷갈린 쓰레기도 표시해 주세요.

        **② 문제 정의서**
        금강 쓰레기 문제에서 AI가 할 일과 사람이 할 일을 정리합니다.
        """,
    },
    3: {
        "page": "pages_src/c3_tm.py",
        "title": "AI는 어떻게 배울까?",
        "intro": "오늘은 티처블 머신으로 조건을 하나씩 바꿔 AI를 학습시키고, 데이터가 AI의 실력을 어떻게 바꾸는지 확인합니다.",
        "plan": """
        **③ 티처블 머신 실험 기록**
        1. 내 실험을 고르고 결과를 **예측**합니다.
        2. 티처블 머신으로 학습시킨 뒤, 테스트 사진 8장의 **AI 예측값**을 입력합니다.
        3. 실제값과 비교해 **틀린 사진의 원인**을 분석하고 발견한 점을 적습니다.
        """,
    },
}


def require_student():
    """이름을 입력하지 않았으면 시작하기 화면으로 안내하고 멈춘다."""
    name = st.session_state.get("student", "")
    if not name:
        st.info("먼저 **시작하기** 화면에서 학번과 이름을 입력해 주세요.")
        st.page_link("pages_src/home.py", label="시작하기로 가기", icon=":material/arrow_back:")
        st.stop()
    st.caption(f"👤 {name}")
    return name
