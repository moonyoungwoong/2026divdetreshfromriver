import streamlit as st

st.set_page_config(page_title="금강 쓰레기 AI 프로젝트", page_icon="♻️", layout="wide")

st.markdown(
    """
    <style>
    .block-container {padding-top: 2.2rem; max-width: 1100px;}
    h1, h2, h3 {letter-spacing: -0.02em;}
    div[data-testid="stMetricValue"] {font-variant-numeric: tabular-nums;}
    </style>
    """,
    unsafe_allow_html=True,
)

home = st.Page("pages_src/home.py", title="시작하기", icon=":material/home:", default=True)
sort_page = st.Page("pages_src/c1_sort.py", title="① 5분 분류 체험", icon=":material/timer:")
define_page = st.Page("pages_src/c1_define.py", title="② 문제 정의서", icon=":material/edit_note:")
teacher = st.Page("pages_src/teacher.py", title="선생님 화면", icon=":material/monitoring:")

nav = st.navigation(
    {
        "": [home],
        "1차시 · 하천 쓰레기 문제와 AI": [sort_page, define_page],
        "선생님": [teacher],
    }
)
nav.run()
