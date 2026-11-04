import altair as alt
import pandas as pd
import streamlit as st

from items import CATEGORIES, ITEMS
import storage

st.title("선생님 화면")

try:
    PASSWORD = st.secrets.get("TEACHER_PASSWORD", "teacher")
except Exception:
    PASSWORD = "teacher"

if not st.session_state.get("teacher_ok"):
    pw = st.text_input("선생님 비밀번호", type="password")
    if st.button("들어가기", type="primary"):
        if pw == PASSWORD:
            st.session_state["teacher_ok"] = True
            st.rerun()
        else:
            st.error("비밀번호가 맞지 않습니다.")
    st.stop()

if not storage.using_sheet():
    st.caption("⚠️ 구글 시트가 연결되지 않아 이 컴퓨터의 data 폴더에 저장 중입니다.")

auto = st.toggle("10초마다 자동 새로고침", value=True)
CAT_COLORS = ["#5170FF", "#A28231", "#2E9E5B", "#8C8C8C"]


def sort_tab():
    df = storage.latest_per_student(storage.load("1차시_분류체험"))
    if df.empty:
        st.info("아직 제출한 학생이 없습니다. 학생이 분류 체험을 제출하면 여기에 바로 나타납니다.")
        return
    for c in ["걸린시간(초)", "분류한 개수", "헷갈린 개수"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    m = st.columns(4)
    m[0].metric("제출한 학생", f"{len(df)}명")
    m[1].metric("평균 분류 개수", f"{df['분류한 개수'].mean():.1f} / {len(ITEMS)}개")
    sec = df["걸린시간(초)"].mean()
    m[2].metric("평균 걸린 시간", f"{int(sec) // 60}분 {int(sec) % 60}초")
    m[3].metric("평균 헷갈린 개수", f"{df['헷갈린 개수'].mean():.1f}개")

    rows = []
    for item in ITEMS:
        col = f"분류_{item}"
        if col not in df.columns:
            continue
        vals = df[col].replace("nan", "").fillna("")
        vals = vals[vals != ""]
        counts = vals.value_counts()
        total = int(counts.sum())
        agree = (counts.max() / total) if total else 0
        for cat in CATEGORIES:
            rows.append({"쓰레기": item, "분류": cat, "학생 수": int(counts.get(cat, 0)), "일치도": agree})
    dist = pd.DataFrame(rows)

    st.subheader("의견이 갈린 쓰레기")
    st.caption("위에 있을수록 학생마다 다르게 나눈 쓰레기입니다. 일치도 = 가장 많이 고른 분류의 비율")
    order = dist.drop_duplicates("쓰레기").sort_values("일치도")["쓰레기"].tolist()
    chart = (
        alt.Chart(dist)
        .mark_bar()
        .encode(
            y=alt.Y("쓰레기:N", sort=order, title=None, axis=alt.Axis(labelLimit=260)),
            x=alt.X("학생 수:Q", stack="normalize", title="학생 비율", axis=alt.Axis(format="%")),
            color=alt.Color("분류:N", scale=alt.Scale(domain=CATEGORIES, range=CAT_COLORS), legend=alt.Legend(orient="top", title=None)),
            tooltip=["쓰레기", "분류", "학생 수", alt.Tooltip("일치도:Q", format=".0%")],
        )
        .properties(height=36 * len(ITEMS))
    )
    st.altair_chart(chart, use_container_width=True)

    left, right = st.columns(2, gap="large")
    with left:
        st.subheader("‘헷갈려요’를 가장 많이 누른 쓰레기")
        hard = df["헷갈린 쓰레기"].fillna("").str.split(", ").explode()
        hard = hard[(hard != "") & (hard != "nan")].value_counts().head(8)
        if hard.empty:
            st.write("아직 없습니다.")
        else:
            st.bar_chart(hard.rename("학생 수"), horizontal=True, color="#FF3131")
    with right:
        st.subheader("헷갈린 이유")
        reasons = df[["학생", "헷갈린 이유"]]
        reasons = reasons[(reasons["헷갈린 이유"] != "") & (reasons["헷갈린 이유"] != "nan")]
        if reasons.empty:
            st.write("아직 없습니다.")
        for _, r in reasons.iterrows():
            st.markdown(f"- {r['헷갈린 이유']}  \n  <span style='color:#8C8C8C;font-size:0.85em'>{r['학생']}</span>", unsafe_allow_html=True)

    with st.expander("제출 원본 보기"):
        st.dataframe(df, use_container_width=True, hide_index=True)


def define_tab():
    df = storage.latest_per_student(storage.load("1차시_문제정의서"))
    if df.empty:
        st.info("아직 제출한 문제 정의서가 없습니다.")
        return
    fields = [c for c in ["무엇이 문제인가", "누가 불편한가", "AI가 할 수 있는 일", "사람이 해야 할 일", "AI를 만들려면 필요한 것"] if c in df.columns]
    st.metric("제출한 학생", f"{len(df)}명")
    view = st.segmented_control("보기", ["항목별로 모아 보기", "학생별로 보기"], default="항목별로 모아 보기")
    if view == "학생별로 보기":
        cols = st.columns(2, gap="medium")
        for i, (_, r) in enumerate(df.iterrows()):
            with cols[i % 2].container(border=True):
                st.markdown(f"**{r['학생']}**")
                for f in fields:
                    st.markdown(f"<span style='color:#5170FF;font-weight:600'>{f}</span><br>{r[f]}", unsafe_allow_html=True)
    else:
        field = st.radio("항목", fields, horizontal=True)
        for _, r in df.iterrows():
            with st.container(border=True):
                st.markdown(f"{r[field]}  \n<span style='color:#8C8C8C;font-size:0.85em'>{r['학생']}</span>", unsafe_allow_html=True)


@st.fragment(run_every=10 if auto else None)
def board():
    t1, t2 = st.tabs(["① 5분 분류 체험", "② 문제 정의서"])
    with t1:
        sort_tab()
    with t2:
        define_tab()


board()
