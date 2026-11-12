import time

import streamlit as st

from common import require_student
from items import CATEGORIES, ITEMS, SHOW_NAMES, SORT_SECONDS, image_html
import storage

student = require_student()
st.title("① 5분 분류 체험")
st.write("공주 **금강 정화 활동**에서 주운 쓰레기를 우리가 직접 나눈다고 생각해 보세요. "
         "사진 속 쓰레기를 **플라스틱 / 캔 / 유리 / 기타** 중 하나로 나누고, 판단하기 어려운 쓰레기는 **헷갈려요**에 표시합니다.")

ss = st.session_state

if ss.get("c1_sort_done"):
    r = ss["c1_sort_done"]
    st.success("제출했어요!")
    m1, m2, m3 = st.columns(3)
    m1.metric("분류한 쓰레기", f"{r['분류한 개수']} / {len(ITEMS)}개")
    m2.metric("걸린 시간", f"{int(r['걸린시간(초)']) // 60}분 {int(r['걸린시간(초)']) % 60}초")
    m3.metric("헷갈린 쓰레기", f"{r['헷갈린 개수']}개")
    st.write("옆 친구와 결과를 비교해 보세요. 같은 쓰레기를 다르게 나눈 것이 있나요?")
    c1, c2 = st.columns(2)
    c1.page_link("pages_src/c1_define.py", label="다음 활동: 문제 정의서 쓰기", icon=":material/arrow_forward:")
    if c2.button("다시 하기"):
        for k in list(ss.keys()):
            if k.startswith("c1_"):
                del ss[k]
        st.rerun()
    st.stop()

if "c1_start" not in ss:
    st.info(f"시작 버튼을 누르면 **{SORT_SECONDS // 60}분** 타이머가 시작됩니다.")
    if st.button("분류 시작", type="primary"):
        ss["c1_start"] = time.time()
        st.rerun()
    st.stop()


@st.fragment(run_every=1)
def timer():
    left = SORT_SECONDS - (time.time() - ss["c1_start"])
    if left > 0:
        m, s = divmod(int(left), 60)
        st.markdown(f"### ⏱ 남은 시간 {m}:{s:02d}")
        st.progress(left / SORT_SECONDS)
    else:
        st.markdown("### ⏰ 시간이 끝났어요")
        st.progress(0.0)
        st.warning("지금까지 나눈 만큼 아래 **제출하기**를 눌러 주세요.")


timer()

with st.form("c1_sort_form"):
    cols = st.columns(3, gap="medium")
    for i, item in enumerate(ITEMS):
        with cols[i % 3].container(border=True):
            img = image_html(i)
            if img:
                st.markdown(img, unsafe_allow_html=True)
            st.markdown(f"**{i + 1}. {item}**" if SHOW_NAMES else f"**{i + 1}번**")
            st.radio("분류", CATEGORIES, index=None, horizontal=True, key=f"c1_cat_{i}", label_visibility="collapsed")
            st.checkbox("헷갈려요", key=f"c1_hard_{i}")
    reason = st.text_area("가장 헷갈렸던 쓰레기와 그 이유", placeholder="예) 과자 봉지: 비닐인지 알루미늄인지 겉만 보고는 알 수 없어서", key="c1_reason")
    submitted = st.form_submit_button("제출하기", type="primary", use_container_width=True)

if submitted:
    elapsed = min(time.time() - ss["c1_start"], SORT_SECONDS)
    answers = {item: (ss.get(f"c1_cat_{i}") or "") for i, item in enumerate(ITEMS)}
    hard = [item for i, item in enumerate(ITEMS) if ss.get(f"c1_hard_{i}")]
    record = {
        "학생": student,
        "걸린시간(초)": int(elapsed),
        "분류한 개수": sum(1 for v in answers.values() if v),
        "헷갈린 개수": len(hard),
        "헷갈린 쓰레기": ", ".join(hard),
        "헷갈린 이유": reason.strip(),
        **{f"분류_{k}": v for k, v in answers.items()},
    }
    if storage.save("1차시_분류체험", record):
        storage.load.clear()
        ss["c1_sort_done"] = record
        st.rerun()
    else:
        st.error("저장하지 못했어요. 잠시 뒤 다시 눌러 주세요.")
        if st.session_state.get("save_error"):
            st.caption("선생님 확인용: " + st.session_state["save_error"])
