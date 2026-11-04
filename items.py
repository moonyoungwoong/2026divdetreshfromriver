"""1차시 분류 체험에 쓰는 쓰레기 목록과 분류 이름.

images/ 폴더에 01.jpg ~ 15.jpg (또는 .png) 를 넣으면 사진이 함께 보입니다.
사진이 없으면 이름만 보입니다.
"""
from pathlib import Path

CATEGORIES = ["플라스틱", "캔", "유리", "기타"]
SORT_SECONDS = 5 * 60  # 분류 체험 제한 시간 (5분)

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
