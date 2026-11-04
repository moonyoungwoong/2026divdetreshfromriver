import streamlit as st

from common import require_student
import storage

student = require_student()
st.title("② 문제 정의서")
st.write("우리 AI 프로젝트가 해결할 문제를 정리합니다. 칸마다 한두 문장이면 충분해요.")

FIELDS = [
    ("무엇이 문제인가", "금강 쓰레기를 나눌 때 가장 어려운 점은 무엇인가요?",
     "급식실에서 학생들이 잔반을 종류별로 나누지 않고 한꺼번에 버린다."),
    ("누가 불편한가", "이 문제 때문에 힘든 사람이나 생물은 누구인가요?",
     "잔반을 다시 나눠야 하는 조리원 선생님, 처리 비용을 내는 학교"),
    ("AI가 할 수 있는 일", "사진을 보고 판단하는 AI라면 어떤 일을 맡길 수 있을까요?",
     "식판 사진을 찍어 남은 음식의 종류를 알아맞힌다."),
    ("사람이 해야 할 일", "AI에게 맡길 수 없거나, 사람이 꼭 정해야 하는 일은 무엇인가요?",
     "어떤 음식을 어느 통에 넣을지 기준 정하기, AI가 틀린 것 바로잡기"),
    ("AI를 만들려면 필요한 것", "이 AI를 만들려면 무엇을 준비해야 할까요?",
     "종류별로 정리된 잔반 사진 수백 장"),
]

with st.expander("📌 다른 주제로 쓴 예시 보기 (급식실 잔반 분류)"):
    for title, _, ex in FIELDS:
        st.markdown(f"**{title}** — {ex}")

prev = st.session_state.get("c1_define_done", {})
with st.form("c1_define_form"):
    values = {}
    for i, (title, question, _) in enumerate(FIELDS):
        st.markdown(f"#### {i + 1}. {title}")
        values[title] = st.text_area(question, value=prev.get(title, ""), key=f"c1_def_{i}", height=80)
    submitted = st.form_submit_button("저장하기", type="primary", use_container_width=True)

if submitted:
    empty = [t for t, v in values.items() if not v.strip()]
    if empty:
        st.error(f"아직 비어 있는 칸이 있어요: {', '.join(empty)}")
    else:
        record = {"학생": student, **{k: v.strip() for k, v in values.items()}}
        if storage.save("1차시_문제정의서", record):
            storage.load.clear()
            st.session_state["c1_define_done"] = record
            st.success("저장했어요! 고칠 내용이 있으면 수정해서 다시 저장해도 됩니다. 마지막에 저장한 내용이 남아요.")
        else:
            st.error("저장하지 못했어요. 인터넷 연결을 확인하고 다시 눌러 주세요.")
