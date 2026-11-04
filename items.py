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
