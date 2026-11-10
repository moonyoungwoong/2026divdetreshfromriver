import pandas as pd
import streamlit as st

from c3_config import (
    CAUSES,
    CLASS_KEYS,
    EXPERIMENTS,
    GRAPH_CHOICES,
    GRAPH_SHAPES,
    PREDICT_CHOICES,
    SHEET,
    TEST_PHOTOS,
    graph_path,
    label,
    photo_path,
)
from common import require_student
import storage

student = require_student()
ss = st.session_state

st.title("③ 티처블 머신 실험 기록")
st.write("조건 하나만 바꿔 AI를 학습시키고, **공통 테스트 사진 8장**으로 AI의 실력을 확인합니다.")

STEPS = ["1. 결과 예측", "2. 테스트 결과 입력", "3. 틀린 사진 분석"]
step = ss.get("c3_step", 0)
if not ss.get("c3_done"):
    st.progress((step + 1) / len(STEPS), text=STEPS[step])


def show_shapes():
    cols = st.columns(4, gap="small")
    for i, g in enumerate(GRAPH_SHAPES):
        with cols[i].container(border=True):
            path = graph_path(g["key"])
            if path:
                st.image(path)
            st.markdown(f"**{'ABCD'[i]}. {g['key']}**  \n<span style='font-size:0.8em;color:#8C8C8C'>{g['desc']}</span>", unsafe_allow_html=True)
    st.caption("파란선 = 훈련 정확도(acc, 연습문제 점수) · 빨간선 = 검증 정확도(test acc, 시험문제 점수)")


def exp_card(exp: str):
    e = EXPERIMENTS[exp]
    with st.container(border=True):
        a, b, c = st.columns([1.2, 1, 1])
        a.markdown(f"**바꾸는 조건**  \n{e['조건']}")
        b.markdown(f"**기준값 → 실험값**  \n{e['기준값']} → **{e['실험값']}**")
        c.markdown(f"**사용할 사진 폴더**  \n`{e['폴더']}`")


# ---------------------------------------------------------------- 제출 완료
if ss.get("c3_done"):
    r = ss["c3_done"]
    st.success("실험 기록을 제출했어요!")
    m = st.columns(3)
    m[0].metric("내 실험", r["실험"])
    m[1].metric("테스트 점수", f"{r['맞힌 수']} / 8")
    m[2].metric("흙 묻은 사진", f"{r['흙 묻은 사진 맞힌 수']} / 4")
    base = storage.load(SHEET)
    if not base.empty and "실험" in base.columns:
        base = storage.latest_per_student(base)
        b1 = pd.to_numeric(base.loc[base["실험"] == "실험 1", "맞힌 수"], errors="coerce").dropna()
        if len(b1) and r["실험"] != "실험 1":
            diff = int(r["맞힌 수"]) - b1.mean()
            word = "높아요" if diff > 0.5 else "낮아요" if diff < -0.5 else "비슷해요"
            st.info(f"우리 반 **기준 실험(실험 1)** 평균은 **{b1.mean():.1f} / 8**점이에요. 내 결과는 기준보다 **{word}**.")
    st.markdown("**발표 문장**")
    st.markdown(f"> {r['발견한 점']}")
    if st.button("다른 실험 다시 하기"):
        for k in [k for k in ss.keys() if k.startswith("c3_")]:
            del ss[k]
        st.rerun()
    st.stop()


# ---------------------------------------------------------------- 1단계: 예측
if step == 0:
    st.subheader("1. 내 실험을 고르고 결과를 예측하기")
    exp = st.radio("내가 맡은 실험", list(EXPERIMENTS), horizontal=True, key="c3_exp_pick", index=None)
    if exp:
        exp_card(exp)
        if exp != "실험 1":
            st.caption("나머지 설정은 모두 그대로 둡니다. 한 번에 하나만 바꿔야 무엇 때문에 결과가 달라졌는지 알 수 있어요.")
    st.markdown("**학습시키기 전에, 정확도 그래프가 어떤 모양일지 예측해 보세요.**")
    show_shapes()
    with st.form("c3_predict"):
        gpred = st.radio("내 조건에서 정확도 그래프는 이런 모양일 것이다", GRAPH_CHOICES, horizontal=True, index=None,
                         format_func=lambda k: f"{'ABCD'[GRAPH_CHOICES.index(k)]}. {k}")
        pred = st.radio(
            "내 조건에서는 테스트 점수가 기준 실험보다",
            PREDICT_CHOICES,
            horizontal=True,
            index=None,
            disabled=exp == "실험 1",
        )
        why = st.text_area("왜냐하면", placeholder="예) 사진이 적으면 AI가 충분히 배우지 못할 것 같아서")
        go = st.form_submit_button("예측 저장하고 실험 시작", type="primary", width="stretch")
    if go:
        if not exp:
            st.error("내가 맡은 실험을 먼저 골라 주세요.")
        elif exp != "실험 1" and not pred:
            st.error("결과를 예측해 주세요.")
        elif not gpred:
            st.error("그래프 모양을 예측해 주세요.")
        elif not why.strip():
            st.error("예측한 이유를 적어 주세요.")
        else:
            ss["c3_gpred"] = gpred
            ss["c3_exp"] = exp
            ss["c3_pred"] = "기준 실험" if exp == "실험 1" else pred
            ss["c3_why"] = why.strip()
            ss["c3_step"] = 1
            st.rerun()
    st.stop()


exp = ss["c3_exp"]
exp_card(exp)

# ---------------------------------------------------------------- 2단계: 테스트 결과 입력
if step == 1:
    st.subheader("2. 티처블 머신 테스트 결과 입력하기")
    with st.expander("티처블 머신에서 할 일 (펼치기)", expanded=True):
        st.markdown(
            f"""
            1. 클래스 이름을 **plastic, can, glass, other** 로 만들고 `{EXPERIMENTS[exp]['폴더']}` 폴더 사진을 올립니다.
            2. {"**고급** 을 열어 **에포크를 5** 로 바꾼 뒤 " if exp == "실험 3" else ""}**모델 학습시키기** 를 누릅니다.
            3. 미리보기에서 입력을 켜고 **웹캠 → 파일** 로 바꿉니다.
            4. `00_공통_테스트사진_8장` 의 사진을 한 장씩 올리고, AI가 고른 클래스와 퍼센트를 아래에 적습니다.
            """
        )
    with st.form("c3_results"):
        cols = st.columns(4, gap="small")
        for i, p in enumerate(TEST_PHOTOS):
            with cols[i % 4].container(border=True):
                path = photo_path(p["no"])
                if path:
                    st.image(str(path))
                st.markdown(f"**사진 {p['no']}**{' · 흙 묻음' if p['dirty'] else ''}  \n<span style='color:#8C8C8C;font-size:0.8em'>{p['file']}</span>", unsafe_allow_html=True)
                st.selectbox("AI의 예측값", CLASS_KEYS, index=None, format_func=label, key=f"c3_p{p['no']}", placeholder="AI가 고른 클래스")
                st.number_input("확률(%)", 0, 100, value=None, step=1, key=f"c3_pct{p['no']}", placeholder="예) 87")
        st.divider()
        st.markdown("**‘고급 > 내부 살펴보기’의 정확도 그래프는 어느 모양과 가장 비슷한가요?**")
        show_shapes()
        g1, g2 = st.columns([2, 1])
        g1.radio(f"실제 그래프 (내 예측: {ss.get('c3_gpred', '')})", GRAPH_CHOICES, index=None, key="c3_graph", horizontal=True,
                 format_func=lambda k: f"{'ABCD'[GRAPH_CHOICES.index(k)]}. {k}")
        g2.number_input("마지막 검증 정확도(test acc, %)", 0, 100, value=None, key="c3_valacc", placeholder="모르면 비워 두기")
        go = st.form_submit_button("결과 확인하기", type="primary", width="stretch")
    if go:
        missing = [p["no"] for p in TEST_PHOTOS if not ss.get(f"c3_p{p['no']}")]
        if missing:
            st.error(f"사진 {', '.join(map(str, missing))}번의 예측값을 골라 주세요.")
        else:
            ss["c3_preds"] = {p["no"]: ss[f"c3_p{p['no']}"] for p in TEST_PHOTOS}
            ss["c3_pcts"] = {p["no"]: ss.get(f"c3_pct{p['no']}") for p in TEST_PHOTOS}
            if not ss.get("c3_graph"):
                st.error("실제 그래프가 어느 모양과 비슷한지 골라 주세요.")
                st.stop()
            ss["c3_graph_v"] = ss.get("c3_graph") or ""
            ss["c3_valacc_v"] = ss.get("c3_valacc")
            ss["c3_step"] = 2
            st.rerun()
    if st.button("← 1단계로"):
        ss["c3_step"] = 0
        st.rerun()
    st.stop()


# ---------------------------------------------------------------- 3단계: 결과와 분석
preds = ss["c3_preds"]
pcts = ss["c3_pcts"]
right = [p for p in TEST_PHOTOS if preds[p["no"]] == p["answer"]]
wrong = [p for p in TEST_PHOTOS if preds[p["no"]] != p["answer"]]
clean_ok = sum(1 for p in right if not p["dirty"])
dirty_ok = sum(1 for p in right if p["dirty"])

st.subheader("3. 결과 보기와 틀린 사진 분석")
m = st.columns(3)
m[0].metric("테스트 점수", f"{len(right)} / 8")
m[1].metric("깨끗한 사진", f"{clean_ok} / 4")
m[2].metric("흙 묻은 사진", f"{dirty_ok} / 4")
st.caption(f"내 예측: 기준 실험보다 **{ss['c3_pred']}**" if exp != "실험 1" else "기준 실험은 다른 실험과 비교하는 기준이 됩니다.")
gp, go_ = ss.get("c3_gpred", ""), ss.get("c3_graph_v", "")
with st.container(border=True):
    a, b, c = st.columns([1, 1, 1.4])
    a.markdown("**예측한 그래프**")
    if graph_path(gp):
        a.image(graph_path(gp))
    a.caption(gp)
    b.markdown("**실제 그래프**")
    if graph_path(go_):
        b.image(graph_path(go_))
    b.caption(go_)
    if gp == go_:
        c.success("그래프 예측이 맞았어요!")
    else:
        c.warning(f"예측은 **{gp}**, 실제는 **{go_}**. 왜 다르게 나왔을지 아래 ‘발견한 점’에 함께 적어 보세요.")

table = pd.DataFrame(
    [
        {
            "사진": f"사진 {p['no']}{' (흙)' if p['dirty'] else ''}",
            "실제값": label(p["answer"]),
            "AI 예측값": label(preds[p["no"]]),
            "확률(%)": "" if pcts[p["no"]] is None else int(pcts[p["no"]]),
            "결과": "⭕ 맞음" if preds[p["no"]] == p["answer"] else "❌ 틀림",
        }
        for p in TEST_PHOTOS
    ]
)
left, rightcol = st.columns([1.3, 1], gap="large")
with left:
    st.markdown("**실제값과 예측값 비교**")
    st.dataframe(table, hide_index=True, width="stretch")
with rightcol:
    st.markdown("**혼동표** (세로: 실제값, 가로: AI 예측값)")
    cm = pd.DataFrame(0, index=CLASS_KEYS, columns=CLASS_KEYS)
    for p in TEST_PHOTOS:
        cm.loc[p["answer"], preds[p["no"]]] += 1
    shade = {0: "", 1: "background-color:#DCE3FF", 2: "background-color:#5170FF;color:white"}
    st.dataframe(cm.style.map(lambda v: shade.get(v, shade[2])), width="stretch")
    st.caption("대각선에 숫자가 모일수록 잘 맞힌 것입니다.")

with st.form("c3_analysis"):
    if wrong:
        st.markdown("**AI가 틀린 사진, 왜 틀렸을까?**")
        for p in wrong:
            with st.container(border=True):
                a, b = st.columns([1, 3])
                path = photo_path(p["no"])
                if path:
                    a.image(str(path))
                b.markdown(f"**사진 {p['no']}** · 실제값 **{label(p['answer'])}** → AI는 **{label(preds[p['no']])}** 로 예측")
                b.radio("가장 그럴듯한 원인", CAUSES, horizontal=True, index=None, key=f"c3_cause{p['no']}")
                b.text_input("그렇게 생각한 이유", key=f"c3_causewhy{p['no']}", placeholder="예) 흙 때문에 캔의 반짝이는 부분이 가려져서")
    else:
        st.success("8장을 모두 맞혔어요! 그래도 AI가 헷갈릴 만한 사진은 어떤 사진일지 아래에 함께 적어 보세요.")
    example = (
        f"예) {EXPERIMENTS[exp]['조건']}을(를) {EXPERIMENTS[exp]['실험값']}(으)로 바꿨더니 테스트 점수가 기준보다 낮아졌다. "
        "데이터가 적으면 AI가 충분히 배우지 못한다는 것을 알았다."
        if exp != "실험 1"
        else "예) 기준 실험에서 AI는 깨끗한 사진은 잘 맞혔지만 흙 묻은 사진은 자주 틀렸다."
    )
    found = st.text_area("발견한 점 (발표 문장으로 적기)", placeholder=example)
    go = st.form_submit_button("실험 기록 제출하기", type="primary", width="stretch")

if go:
    if not found.strip():
        st.error("발견한 점을 적어 주세요.")
        st.stop()
    record = {
        "학생": student,
        "실험": exp,
        "바꾼 조건": f"{EXPERIMENTS[exp]['조건']}: {EXPERIMENTS[exp]['기준값']} → {EXPERIMENTS[exp]['실험값']}",
        "예측": ss["c3_pred"],
        "예측 이유": ss["c3_why"],
        "맞힌 수": len(right),
        "깨끗한 사진 맞힌 수": clean_ok,
        "흙 묻은 사진 맞힌 수": dirty_ok,
        "그래프 예측": ss.get("c3_gpred", ""),
        "그래프 관찰": ss["c3_graph_v"],
        "검증정확도(%)": "" if ss["c3_valacc_v"] is None else int(ss["c3_valacc_v"]),
        "틀린 사진": ", ".join(str(p["no"]) for p in wrong),
        "틀린 원인": " / ".join(str(p["no"]) + ":" + (ss.get("c3_cause" + str(p["no"])) or "") for p in wrong),
        "원인 설명": " / ".join(str(p["no"]) + ":" + (ss.get("c3_causewhy" + str(p["no"])) or "").strip() for p in wrong),
        "발견한 점": found.strip(),
    }
    for p in TEST_PHOTOS:
        record[f"사진{p['no']}_실제값"] = p["answer"]
        record[f"사진{p['no']}_예측값"] = preds[p["no"]]
        record[f"사진{p['no']}_확률"] = "" if pcts[p["no"]] is None else int(pcts[p["no"]])
    if storage.save(SHEET, record):
        storage.load.clear()
        ss["c3_done"] = record
        st.rerun()
    else:
        st.error("저장하지 못했어요. 잠시 뒤 다시 눌러 주세요.")
        if ss.get("save_error"):
            st.caption("선생님 확인용: " + ss["save_error"])

if st.button("← 2단계로 (결과 다시 입력)"):
    ss["c3_step"] = 1
    st.rerun()
