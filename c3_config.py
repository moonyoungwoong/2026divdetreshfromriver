"""3차시 티처블 머신 실험에 쓰는 설정.

- CLASSES: 티처블 머신에서 만든 클래스 이름 (영어) 과 화면에 보일 한글 이름
- EXPERIMENTS: 실험 번호별로 바꾸는 조건 (슬라이드 '실험 조건' 표와 같음)
- TEST_PHOTOS: 공통 테스트 사진 8장. images/c3_test/1.jpg ~ 8.jpg 가 순서대로 이 사진입니다.
  file 은 학생들이 받은 사진 묶음(00_공통_테스트사진_8장) 속 파일 이름입니다.
"""
from pathlib import Path

CLASSES = {"plastic": "플라스틱", "can": "캔", "glass": "유리", "other": "기타"}
CLASS_KEYS = list(CLASSES)


def label(c: str) -> str:
    return f"{c} ({CLASSES[c]})" if c in CLASSES else c


EXPERIMENTS = {
    "실험 1": {"조건": "바꾸지 않음 (기준 실험)", "기준값": "-", "실험값": "-", "폴더": "실험1_기준"},
    "실험 2": {"조건": "클래스당 사진 수", "기준값": "10장", "실험값": "3장", "폴더": "실험2_클래스당3장"},
    "실험 3": {"조건": "학습 횟수(에포크)", "기준값": "50회", "실험값": "5회", "폴더": "실험1_기준 (고급에서 에포크 5)"},
    "실험 4": {"조건": "일부러 틀린 정답(라벨) 섞기", "기준값": "0장", "실험값": "클래스마다 2장", "폴더": "실험4_틀린정답섞기"},
    "실험 5": {"조건": "클래스별 사진 수 균형", "기준값": "모두 10장", "실험값": "plastic만 30장", "폴더": "실험5_불균형"},
    "실험 6": {"조건": "훈련 사진 상태", "기준값": "흙 묻은 사진 포함", "실험값": "깨끗한 사진만", "폴더": "실험6_깨끗한사진만"},
}

TEST_PHOTOS = [
    {"no": 1, "answer": "plastic", "dirty": False, "file": "plastic_1.jpg"},
    {"no": 2, "answer": "plastic", "dirty": True, "file": "plastic_2_흙묻음.jpg"},
    {"no": 3, "answer": "can", "dirty": False, "file": "can_1.jpg"},
    {"no": 4, "answer": "can", "dirty": True, "file": "can_2_흙묻음.jpg"},
    {"no": 5, "answer": "glass", "dirty": False, "file": "glass_1.jpg"},
    {"no": 6, "answer": "glass", "dirty": True, "file": "glass_2_흙묻음.jpg"},
    {"no": 7, "answer": "other", "dirty": False, "file": "other_1.jpg"},
    {"no": 8, "answer": "other", "dirty": True, "file": "other_2_흙묻음.jpg"},
]

PREDICT_CHOICES = ["높을 것이다", "비슷할 것이다", "낮을 것이다"]
# 정확도 그래프 모양 (학습 전 예측, 학습 후 관찰에 같은 보기 사용). 그림: images/c3_graph/a~d.png
GRAPH_SHAPES = [
    {"key": "붙어 있다", "file": "a", "desc": "두 선이 함께 올라가 끝까지 가깝다 (차이 10%p 이하)"},
    {"key": "조금 벌어진다", "file": "b", "desc": "훈련선이 조금 더 높다 (차이 10~20%p)"},
    {"key": "많이 벌어진다", "file": "c", "desc": "훈련선만 끝까지 오르고 검증선은 낮게 멈춘다 (차이 20%p 이상) → 과적합 신호"},
    {"key": "둘 다 낮다", "file": "d", "desc": "두 선 모두 낮은 곳에 머문다 → 덜 배움"},
]
GRAPH_CHOICES = [g["key"] for g in GRAPH_SHAPES]


def graph_path(key: str):
    for g in GRAPH_SHAPES:
        if g["key"] == key:
            p = Path(__file__).parent / "images" / "c3_graph" / f"{g['file']}.png"
            return str(p) if p.exists() else None
    return None


CAUSES = [
    "데이터가 부족해서",
    "흙·물로 모양이 변해서",
    "다른 종류와 닮아서",
    "정답(라벨)이 잘못돼서",
    "기타",
]

SHEET = "3차시_티처블머신"
IMAGE_DIR = Path(__file__).parent / "images" / "c3_test"


def photo_path(no: int):
    p = IMAGE_DIR / f"{no}.jpg"
    return p if p.exists() else None
