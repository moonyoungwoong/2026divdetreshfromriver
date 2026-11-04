"""1차시 분류 체험에 쓰는 쓰레기 목록과 분류 이름.

images/ 폴더의 01.png ~ 15.png 가 순서대로 각 쓰레기의 사진입니다. (교재 54쪽 그림)
사진을 바꾸려면 같은 번호의 파일로 교체하세요 (.jpg 도 됩니다).
"""
from pathlib import Path

CATEGORIES = ["플라스틱", "캔", "유리", "기타"]
SORT_SECONDS = 5 * 60  # 분류 체험 제한 시간 (5분)
SHOW_NAMES = True  # False로 바꾸면 사진과 번호만 보이고 쓰레기 이름은 숨깁니다

ITEMS = [
    "생수 페트병",
    "찌그러진 캔 묶음",
    "깨진 유리병",
    "음료 캔",
    "음식물 쓰레기 (생선 뼈·과일 껍질)",
    "젖은 헝겊",
    "유리병",
    "스티로폼 상자",
    "폐타이어",
    "고무장갑",
    "낡은 운동화",
    "과자 봉지",
    "채소·과일 껍질",
    "깨진 스티로폼 조각",
    "비닐봉지와 플라스틱 조각",
]

IMAGE_DIR = Path(__file__).parent / "images"


def image_for(i: int):
    """i번째(0부터) 쓰레기 사진 경로. 없으면 None."""
    for ext in ("jpg", "jpeg", "png", "webp"):
        p = IMAGE_DIR / f"{i + 1:02d}.{ext}"
        if p.exists():
            return p
    return None


def image_html(i: int, width: int = 200):
    """i번째 쓰레기 사진을 페이지에 직접 넣는 <img> 태그.

    st.image는 타이머가 1초마다 화면을 새로 그릴 때 사진 파일 주소가 지워져
    일부 사진이 빠지는 문제가 있어, 사진을 페이지 안에 바로 넣는다.
    """
    p = image_for(i)
    if not p:
        return ""
    return (
        f'<img src="data:image/jpeg;base64,{_jpeg_b64(str(p), p.stat().st_mtime)}" '
        f'width="{width}" style="max-width:100%;height:auto;border-radius:6px;display:block;margin-bottom:6px" alt="{i + 1}번 쓰레기">'
    )


def _jpeg_b64(path: str, _mtime: float) -> str:
    return _cached_jpeg_b64(path, _mtime)


try:
    import streamlit as _st

    @_st.cache_data(show_spinner=False)
    def _cached_jpeg_b64(path: str, _mtime: float) -> str:
        return _encode(path)
except Exception:  # streamlit 밖에서 불러올 때
    def _cached_jpeg_b64(path: str, _mtime: float) -> str:
        return _encode(path)


def _encode(path: str) -> str:
    import base64
    import io

    from PIL import Image

    im = Image.open(path).convert("RGB")
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()
