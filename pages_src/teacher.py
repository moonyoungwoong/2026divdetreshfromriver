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
        st.dataframe(df, width="stretch", hide_index=True)


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


def label_tab():
    from c2_config import CLASS_KEYS, CLASSES, GOAL, ROUND1, ROUND2, SHEET1, SHEET2, WRONG_NOS, photo

    st.subheader("1라운드 · 반 전체 라벨 일치율")
    d1 = storage.latest_per_student(storage.load(SHEET1))
    if d1.empty or "학생" not in d1.columns:
        st.info("아직 1라운드 제출이 없습니다.")
    else:
        stats = []
        for p in ROUND1:
            col = f"사진{p['no']}_라벨"
            if col not in d1.columns:
                continue
            vc = d1[col].value_counts()
            clues = d1[f"사진{p['no']}_단서"].fillna("").str.split(", ").explode()
            clues = clues[clues != ""].value_counts()
            stats.append({"no": p["no"], "note": p["note"], "top": vc.idxmax(), "share": vc.max() / len(d1), "vc": vc, "clues": clues})
        agree = sum(x["share"] for x in stats) / len(stats)
        m = st.columns(3)
        m[0].metric("제출한 학생", f"{len(d1)}명")
        m[1].metric("반 전체 일치율", f"{agree:.0%}", help="사진마다 가장 많이 고른 라벨을 고른 학생 비율의 평균")
        m[2].metric("목표", f"{GOAL:.0%}", delta=f"{(agree - GOAL) * 100:+.0f}%p")
        st.progress(min(agree, 1.0), text=f"일치율 {agree:.0%} / 목표 {GOAL:.0%}")
        st.markdown("**의견이 많이 갈린 사진부터** (기준표를 고칠 근거)")
        stats.sort(key=lambda x: x["share"])
        cols = st.columns(4, gap="small")
        for i, x in enumerate(stats):
            with cols[i % 4].container(border=True):
                img = photo(1, x["no"])
                if img:
                    st.image(img)
                color = "#FF3131" if x["share"] < 0.7 else "#1D1D1F"
                st.markdown(f"**사진 {x['no']}** · <span style='color:{color};font-weight:700'>{x['share']:.0%} 일치</span>  \n<span style='color:#8C8C8C;font-size:0.8em'>{x['note']}</span>", unsafe_allow_html=True)
                st.markdown("  \n".join(f"{CLASSES[k]} {v}명" for k, v in x["vc"].items()))
                if len(x["clues"]):
                    st.caption("단서: " + ", ".join(x["clues"].index[:3]))

    st.divider()
    st.subheader("2라운드 · 틀린 라벨 검수")
    d2 = storage.latest_per_student(storage.load(SHEET2))
    if d2.empty or "학생" not in d2.columns:
        st.info("아직 2라운드 제출이 없습니다.")
        return
    for c in ["찾은 틀린 라벨", "잘못 의심한 수"]:
        d2[c] = pd.to_numeric(d2[c], errors="coerce")
    m = st.columns(3)
    m[0].metric("제출한 학생", f"{len(d2)}명")
    m[1].metric("평균 찾은 틀린 라벨", f"{d2['찾은 틀린 라벨'].mean():.1f} / {len(WRONG_NOS)}")
    m[2].metric("4장 모두 찾은 학생", f"{int((d2['찾은 틀린 라벨'] == len(WRONG_NOS)).sum())}명")
    agree2 = []
    for p in ROUND2:
        col = f"사진{p['no']}_최종라벨"
        if col in d2.columns:
            agree2.append(d2[col].value_counts().max() / len(d2))
    if agree2 and not d1.empty and "학생" in d1.columns:
        st.markdown(f"**최종 라벨 일치율**: 1라운드 {agree:.0%} → 2라운드 **{sum(agree2) / len(agree2):.0%}**")
    cols = st.columns(6, gap="small")
    for i, p in enumerate(ROUND2):
        col = f"사진{p['no']}_검수"
        if col not in d2.columns:
            continue
        wrong = p["no"] in WRONG_NOS
        rate = (d2[col] == "틀렸다").mean()
        with cols[i % 6].container(border=True):
            img = photo(2, p["no"])
            if img:
                st.image(img)
            st.markdown(f"**사진 {p['no']}** {'🚩' if wrong else ''}  \n라벨 {CLASSES[p['given']]}" + (f" → 정답 {CLASSES[p['answer']]}" if wrong else ""))
            st.markdown(f"<span style='font-weight:700;color:{'#5170FF' if wrong else ('#FF3131' if rate > 0.3 else '#1D1D1F')}'>{rate:.0%}</span> 가 틀렸다고 함", unsafe_allow_html=True)
    st.caption("🚩 = 일부러 숨긴 틀린 라벨. 🚩가 없는데 '틀렸다'가 많으면, 그 사진도 기준표로 다시 이야기해 볼 만합니다.")


def tm_tab():
    from c3_config import CAUSES, CLASS_KEYS, EXPERIMENTS, SHEET, TEST_PHOTOS, label, photo_path

    df = storage.latest_per_student(storage.load(SHEET))
    if df.empty or "실험" not in df.columns:
        st.info("아직 제출한 실험 기록이 없습니다. 학생이 ③ 티처블 머신 실험 기록을 제출하면 여기에 바로 나타납니다.")
        return
    for c in ["맞힌 수", "깨끗한 사진 맞힌 수", "흙 묻은 사진 맞힌 수"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    base = df.loc[df["실험"] == "실험 1", "맞힌 수"].mean()

    m = st.columns(3)
    m[0].metric("제출한 학생", f"{len(df)}명")
    m[1].metric("기준 실험(실험 1) 평균", "아직 없음" if pd.isna(base) else f"{base:.1f} / 8")
    m[2].metric("전체 평균", f"{df['맞힌 수'].mean():.1f} / 8")

    st.subheader("우리 반 실험 결과")
    rows = []
    for exp, e in EXPERIMENTS.items():
        g = df[df["실험"] == exp]
        if g.empty:
            rows.append({"실험": exp, "바꾼 조건": f"{e['조건']} ({e['실험값']})" if exp != "실험 1" else e["조건"], "학생 수": 0})
            continue
        avg = g["맞힌 수"].mean()
        if exp == "실험 1" or pd.isna(base):
            vs = "-"
        else:
            d = avg - base
            vs = f"{'▲' if d > 0.5 else '▼' if d < -0.5 else '≈'} {d:+.1f}"
        pred = g["예측"].value_counts().idxmax() if exp != "실험 1" else "-"
        rows.append(
            {
                "실험": exp,
                "바꾼 조건": f"{e['조건']} ({e['실험값']})" if exp != "실험 1" else e["조건"],
                "학생 수": len(g),
                "가장 많은 예측": pred,
                "평균 점수(/8)": round(avg, 1),
                "기준 대비": vs,
                "깨끗한 사진(/4)": round(g["깨끗한 사진 맞힌 수"].mean(), 1),
                "흙 묻은 사진(/4)": round(g["흙 묻은 사진 맞힌 수"].mean(), 1),
            }
        )
    summary = pd.DataFrame(rows)
    st.dataframe(summary, hide_index=True, width="stretch")

    left, right = st.columns(2, gap="large")
    with left:
        st.markdown("**실험별 평균 테스트 점수**")
        done = summary[summary["학생 수"] > 0]
        bars = alt.Chart(done).mark_bar(color="#5170FF").encode(
            x=alt.X("실험:N", title=None, sort=list(EXPERIMENTS)),
            y=alt.Y("평균 점수(/8):Q", title="평균 점수", scale=alt.Scale(domain=[0, 8])),
            tooltip=["실험", "바꾼 조건", "학생 수", "평균 점수(/8)"],
        )
        layers = [bars]
        if not pd.isna(base):
            layers.append(alt.Chart(pd.DataFrame({"y": [base]})).mark_rule(color="#FF3131", strokeDash=[6, 4], size=2).encode(y="y:Q"))
        st.altair_chart(alt.layer(*layers).properties(height=280), use_container_width=True)
        st.caption("빨간 점선 = 기준 실험(실험 1) 평균")
    with right:
        st.markdown("**깨끗한 사진 vs 흙 묻은 사진**")
        long = done.melt(id_vars="실험", value_vars=["깨끗한 사진(/4)", "흙 묻은 사진(/4)"], var_name="사진", value_name="평균")
        ch = alt.Chart(long).mark_bar().encode(
            x=alt.X("실험:N", title=None, sort=list(EXPERIMENTS)),
            xOffset="사진:N",
            y=alt.Y("평균:Q", title="평균 맞힌 수", scale=alt.Scale(domain=[0, 4])),
            color=alt.Color("사진:N", scale=alt.Scale(range=["#5170FF", "#A28231"]), legend=alt.Legend(orient="top", title=None)),
            tooltip=["실험", "사진", "평균"],
        )
        st.altair_chart(ch.properties(height=280), use_container_width=True)

    st.subheader("AI가 많이 틀린 사진")
    cols = st.columns(8, gap="small")
    for i, p in enumerate(TEST_PHOTOS):
        col = f"사진{p['no']}_예측값"
        if col not in df.columns:
            continue
        preds = df[col]
        ok = (preds == p["answer"]).mean()
        wrong = preds[preds != p["answer"]]
        with cols[i].container(border=True):
            path = photo_path(p["no"])
            if path:
                st.image(str(path))
            st.markdown(f"**사진 {p['no']}**{' (흙)' if p['dirty'] else ''}  \n정답 {p['answer']}")
            st.markdown(f"<span style='font-size:1.4em;font-weight:700;color:{'#FF3131' if ok < 0.5 else '#1D1D1F'}'>{ok:.0%}</span> 맞힘", unsafe_allow_html=True)
            if len(wrong):
                st.caption(f"주로 {wrong.value_counts().idxmax()}(으)로 착각")

    left, right = st.columns([1, 1.4], gap="large")
    with left:
        st.markdown("**학생들이 고른 틀린 원인**")
        causes = df["틀린 원인"].fillna("").str.split(" / ").explode().str.split(":").str[-1]
        causes = causes[(causes != "") & (causes != "nan")].value_counts()
        if causes.empty:
            st.write("아직 없습니다.")
        else:
            st.bar_chart(causes.rename("학생 수"), horizontal=True, color="#FF3131")
    with right:
        st.markdown("**발견한 점 (발표 문장)**")
        pick = st.segmented_control("실험", ["전체"] + list(EXPERIMENTS), default="전체", key="tm_found_pick")
        view = df if pick in (None, "전체") else df[df["실험"] == pick]
        for _, r in view.sort_values("실험").iterrows():
            with st.container(border=True):
                st.markdown(f"{r['발견한 점']}  \n<span style='color:#8C8C8C;font-size:0.85em'>{r['실험']} · {r['학생']} · {int(r['맞힌 수'])}/8</span>", unsafe_allow_html=True)

    with st.expander("제출 원본 보기"):
        st.dataframe(df, width="stretch", hide_index=True)


@st.fragment(run_every=10 if auto else None)
def board():
    t1, t2, t4, t3 = st.tabs(["① 5분 분류 체험", "② 문제 정의서", "② 라벨링 미션 (2차시)", "③ 티처블 머신 실험"])
    with t1:
        sort_tab()
    with t2:
        define_tab()
    with t4:
        label_tab()
    with t3:
        tm_tab()


board()
