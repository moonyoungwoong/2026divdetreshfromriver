import pandas as pd
import streamlit as st

from c2_config import CLASS_KEYS, CLASSES, CLUES, ROUND1, ROUND2, SHEET1, SHEET2, WRONG_NOS, label, photo
from common import require_student
import storage

student = require_student()
ss = st.session_state

st.title("② 라벨링 미션: 나는 AI 데이터 라벨러")
st.write(
    "AI는 사람이 붙인 **라벨**(정답)을 그대로 믿고 배웁니다. "
    "오늘 우리는 AI가 배울 사진에 라벨을 붙이고, 다른 사람이 붙인 라벨을 검수합니다."
)

r1_done = ss.get("c2_r1")
r2_done = ss.get("c2_r2")

with st.container(border=True):
    a, b = st.columns(2)
    a.markdown(f"{'✅' if r1_done else '1️⃣'} **1라운드 · 라벨러**  \n사진 12장에 라벨과 단서 붙이기")
    b.markdown(f"{'✅' if r2_done else '2️⃣'} **2라운드 · 검수자**  \n숨겨진 틀린 라벨 4장 찾기")


def short(c):
    return CLASSES[c]


# ---------------------------------------------------------------- 1라운드
if not r1_done:
    st.subheader("1라운드 · 라벨러")
    st.info("우리 반이 만든 **분류 기준표**를 떠올리며 라벨을 붙이세요. 라벨마다 무엇을 보고 판단했는지, 즉 **단서**도 골라 주세요.")
    with st.form("c2_r1_form"):
        cols = st.columns(3, gap="small")
        for i, p in enumerate(ROUND1):
            with cols[i % 3].container(border=True):
                img = photo(1, p["no"])
                if img:
                    st.image(img)
                st.markdown(f"**사진 {p['no']}**")
                st.radio("라벨", CLASS_KEYS, format_func=short, horizontal=True, index=None, key=f"c2_l{p['no']}", label_visibility="collapsed")
                st.multiselect("판단한 단서 (최대 2개)", CLUES, max_selections=2, key=f"c2_c{p['no']}", placeholder="단서 고르기")
        go = st.form_submit_button("1라운드 제출", type="primary", width="stretch")
    if go:
        miss_l = [p["no"] for p in ROUND1 if not ss.get(f"c2_l{p['no']}")]
        miss_c = [p["no"] for p in ROUND1 if not ss.get(f"c2_c{p['no']}")]
        if miss_l:
            st.error(f"사진 {', '.join(map(str, miss_l))}번의 라벨을 골라 주세요.")
        elif miss_c:
            st.error(f"사진 {', '.join(map(str, miss_c))}번의 단서를 하나 이상 골라 주세요.")
        else:
            rec = {"학생": student}
            for p in ROUND1:
                rec[f"사진{p['no']}_라벨"] = ss[f"c2_l{p['no']}"]
                rec[f"사진{p['no']}_단서"] = ", ".join(ss[f"c2_c{p['no']}"])
            if storage.save(SHEET1, rec):
                storage.load.clear()
                ss["c2_r1"] = rec
                st.rerun()
            else:
                st.error("저장하지 못했어요. 잠시 뒤 다시 눌러 주세요.")
    st.stop()

# ---------------------------------------------------------------- 1라운드 결과
with st.expander("1라운드 결과: 반 친구들과 얼마나 같은 라벨을 붙였을까?", expanded=not r2_done):
    df = storage.latest_per_student(storage.load(SHEET1))
    others = df[df["학생"] != student] if not df.empty and "학생" in df.columns else pd.DataFrame()
    if others.empty:
        st.write("아직 다른 친구의 제출이 없어요. 잠시 뒤 다시 열어 보세요.")
    else:
        same, rows = 0, []
        for p in ROUND1:
            col = f"사진{p['no']}_라벨"
            if col not in others.columns:
                continue
            vc = others[col].value_counts()
            top = vc.idxmax()
            mine = r1_done[col]
            share = (others[col] == mine).mean()
            same += int(mine == top)
            rows.append({"사진": p["no"], "내 라벨": short(mine), "친구들이 가장 많이 고른 라벨": f"{short(top)} ({vc.max() / len(others):.0%})", "나와 같은 친구": f"{share:.0%}"})
        st.metric("가장 많은 친구와 같은 라벨", f"{same} / {len(rows)}")
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        st.caption("의견이 갈린 사진은 선생님 화면에서 함께 보고, 분류 기준표를 더 구체적으로 고칩니다.")

# ---------------------------------------------------------------- 2라운드
if not r2_done:
    st.subheader("2라운드 · 검수자")
    if not ss.get("c2_r2_open"):
        st.write("기준표를 고친 뒤, 선생님이 신호를 주면 2라운드를 시작하세요.")
        if st.button("2라운드 시작", type="primary"):
            ss["c2_r2_open"] = True
            st.rerun()
        st.stop()
    st.warning(
        "다른 라벨러가 사진에 라벨을 붙여 두었습니다. 그런데 **12장 중 4장은 라벨이 틀렸다**고 합니다. "
        "AI가 틀린 정답을 배우지 않도록 찾아 주세요!"
    )
    with st.form("c2_r2_form"):
        cols = st.columns(3, gap="small")
        for i, p in enumerate(ROUND2):
            with cols[i % 3].container(border=True):
                img = photo(2, p["no"])
                if img:
                    st.image(img)
                st.markdown(f"**사진 {p['no']}** · 붙어 있는 라벨: **:blue-background[{label(p['given'])}]**")
                st.radio("검수", ["맞다", "틀렸다"], horizontal=True, index=None, key=f"c2_v{p['no']}", label_visibility="collapsed")
                st.selectbox("틀렸다면 올바른 라벨", CLASS_KEYS, index=None, format_func=short, key=f"c2_f{p['no']}", placeholder="틀렸다면 올바른 라벨 고르기")
        go = st.form_submit_button("검수 결과 제출", type="primary", width="stretch")
    if go:
        miss = [p["no"] for p in ROUND2 if not ss.get(f"c2_v{p['no']}")]
        nofix = [p["no"] for p in ROUND2 if ss.get(f"c2_v{p['no']}") == "틀렸다" and not ss.get(f"c2_f{p['no']}")]
        if miss:
            st.error(f"사진 {', '.join(map(str, miss))}번을 검수해 주세요.")
        elif nofix:
            st.error(f"'틀렸다'고 한 사진 {', '.join(map(str, nofix))}번의 올바른 라벨을 골라 주세요.")
        else:
            flagged = [p["no"] for p in ROUND2 if ss[f"c2_v{p['no']}"] == "틀렸다"]
            found = [n for n in flagged if n in WRONG_NOS]
            fixed = [p["no"] for p in ROUND2 if p["no"] in found and ss.get(f"c2_f{p['no']}") == p["answer"]]
            rec = {
                "학생": student,
                "찾은 틀린 라벨": len(found),
                "올바르게 고친 수": len(fixed),
                "잘못 의심한 수": len(flagged) - len(found),
                "틀렸다고 한 사진": ", ".join(map(str, flagged)),
            }
            for p in ROUND2:
                v = ss[f"c2_v{p['no']}"]
                rec[f"사진{p['no']}_검수"] = v
                rec[f"사진{p['no']}_최종라벨"] = ss.get(f"c2_f{p['no']}") if v == "틀렸다" else p["given"]
            if storage.save(SHEET2, rec):
                storage.load.clear()
                ss["c2_r2"] = rec
                st.rerun()
            else:
                st.error("저장하지 못했어요. 잠시 뒤 다시 눌러 주세요.")
    st.stop()

# ---------------------------------------------------------------- 완료
r = r2_done
st.subheader("검수 결과")
m = st.columns(3)
m[0].metric("찾은 틀린 라벨", f"{r['찾은 틀린 라벨']} / {len(WRONG_NOS)}")
m[1].metric("올바르게 고친 수", f"{r['올바르게 고친 수']} / {len(WRONG_NOS)}")
m[2].metric("맞는 라벨을 틀렸다고 의심", f"{r['잘못 의심한 수']}장")
rows = []
for p in ROUND2:
    wrong = p["given"] != p["answer"]
    flagged = r[f"사진{p['no']}_검수"] == "틀렸다"
    rows.append(
        {
            "사진": p["no"],
            "붙어 있던 라벨": short(p["given"]),
            "실제 정답": short(p["answer"]),
            "내 검수": r[f"사진{p['no']}_검수"],
            "결과": "⭕" if wrong == flagged else "❌",
        }
    )
st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
st.success("수고했어요! 우리 반이 검수한 데이터로 다음 시간에 AI를 학습시킵니다.")
st.markdown("**생각해 보기**: 틀린 라벨을 못 찾고 AI에게 그대로 가르쳤다면, AI는 어떻게 될까요?")
