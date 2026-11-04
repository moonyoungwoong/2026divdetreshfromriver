"""활동 기록 저장소.

- secrets에 APPS_SCRIPT_URL이 있으면 구글 시트(Apps Script 웹앱)에 저장한다.
- 없으면 data/ 폴더의 CSV에 저장한다 (내 컴퓨터에서 연습할 때).
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

KST = timezone(timedelta(hours=9))
DATA_DIR = Path(__file__).parent / "data"


def _secret(key, default=""):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


def using_sheet():
    return bool(_secret("APPS_SCRIPT_URL"))


def now_str():
    return datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")


def save(sheet: str, record: dict):
    """record 한 줄을 sheet 탭에 추가한다. 성공하면 True."""
    record = {"제출시각": now_str(), **record}
    url = _secret("APPS_SCRIPT_URL")
    if url:
        st.session_state["save_error"] = ""
        try:
            r = requests.post(
                url,
                json={"token": _secret("APPS_SCRIPT_TOKEN"), "sheet": sheet, "record": record},
                timeout=20,
            )
        except Exception as e:
            st.session_state["save_error"] = f"구글 시트에 연결하지 못했습니다 ({type(e).__name__})."
            return False
        try:
            data = r.json()
        except Exception:
            st.session_state["save_error"] = (
                f"구글 시트가 데이터 대신 웹페이지를 돌려줬습니다 (HTTP {r.status_code}). "
                "Apps Script 배포의 액세스 권한이 '모든 사용자'인지, URL이 /exec로 끝나는지 확인하세요."
            )
            return False
        if not data.get("ok"):
            if data.get("error") == "token":
                st.session_state["save_error"] = "비밀 문자열(TOKEN)이 서로 다릅니다. Secrets의 APPS_SCRIPT_TOKEN과 Apps Script의 TOKEN을 맞추고, Apps Script는 새 버전으로 다시 배포하세요."
            else:
                st.session_state["save_error"] = f"구글 시트가 저장을 거부했습니다: {data}"
            return False
        return True
    DATA_DIR.mkdir(exist_ok=True)
    path = DATA_DIR / f"{sheet}.csv"
    df = pd.DataFrame([record])
    if path.exists():
        df = pd.concat([pd.read_csv(path, dtype=str), df.astype(str)], ignore_index=True)
    df.to_csv(path, index=False)
    return True


@st.cache_data(ttl=5, show_spinner=False)
def load(sheet: str) -> pd.DataFrame:
    url = _secret("APPS_SCRIPT_URL")
    if url:
        try:
            r = requests.get(url, params={"token": _secret("APPS_SCRIPT_TOKEN"), "sheet": sheet}, timeout=20)
            data = r.json()
            return pd.DataFrame(data.get("rows", [])).astype(str)
        except Exception:
            return pd.DataFrame()
    path = DATA_DIR / f"{sheet}.csv"
    return pd.read_csv(path, dtype=str).fillna("") if path.exists() else pd.DataFrame()


def latest_per_student(df: pd.DataFrame) -> pd.DataFrame:
    """같은 학생이 여러 번 제출했으면 마지막 제출만 남긴다."""
    if df.empty or "학생" not in df.columns:
        return df
    return df.sort_values("제출시각").drop_duplicates("학생", keep="last")
