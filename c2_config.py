"""2차시 라벨링 미션 설정.

1라운드 (라벨러): 헷갈리는 사진 12장에 각자 라벨과 단서를 붙인다 → 반 전체 일치율 확인
2라운드 (검수자): 다른 라벨러가 라벨을 붙여 둔 사진 12장을 검수한다 → 숨겨진 틀린 라벨 4장 찾기

images/c2_r1/1.jpg ~ 12.jpg, images/c2_r2/1.jpg ~ 12.jpg 가 순서대로 아래 사진입니다.
"""
from pathlib import Path

CLASSES = {"plastic": "플라스틱", "can": "캔", "glass": "유리", "other": "기타"}
CLASS_KEYS = list(CLASSES)


def label(c: str) -> str:
    return f"{CLASSES[c]} ({c})" if c in CLASSES else c


# 단서: 분류마다 다른 단서를 고를 수 있도록 종류별로 나눔 (목록에 없으면 학생이 직접 입력 가능)
CLUE_GROUPS = {
    "빛·색": ["금속처럼 반짝인다", "은색이다", "맑고 투명하게 비친다", "뿌옇게 반투명하다", "색이 있다 (초록·갈색 등)", "색이 화려하게 인쇄되어 있다"],
    "재질": ["두껍고 단단해 보인다", "얇아서 눌리면 휠 것 같다", "얇고 흐물흐물하다 (비닐)", "가볍고 푹신해 보인다 (스티로폼)", "종이·천 같다"],
    "모양": ["원통 모양", "병 모양 (입구가 좁다)", "넓은 용기·접시 모양", "납작하다", "작은 조각이다"],
    "부분": ["따개(고리)가 있다", "윗면 테두리가 말려 있다", "병뚜껑·나사선이 있다", "병 바닥이 울퉁불퉁하다", "라벨 비닐이 감겨 있다"],
    "상태": ["찌그러졌다", "구겨졌다", "깨졌거나 금이 갔다", "흙·물때가 묻었다", "흙에 가려 잘 안 보인다"],
    "기타": ["상표·글자가 보인다"],
}
CLUES = [f"[{g}] {c}" for g, items in CLUE_GROUPS.items() for c in items]

# 1라운드: 정답을 맞히는 활동이 아니라 '반 친구들과 같은 라벨을 붙이는지' 보는 활동
# note: 선생님 화면에 보이는 사진 설명 (원래 데이터셋의 분류)
ROUND1 = [
    {"no": 1, "note": "투명 생수병"},
    {"no": 2, "note": "투명 플라스틱 계란판"},
    {"no": 3, "note": "투명 플라스틱 용기 (유리처럼 보임)"},
    {"no": 4, "note": "유리병 (잼 병)"},
    {"no": 5, "note": "유리병 일부를 가까이 찍음"},
    {"no": 6, "note": "음료 캔 윗면"},
    {"no": 7, "note": "구겨진 은박지"},
    {"no": 8, "note": "은박 접시"},
    {"no": 9, "note": "금속 병뚜껑"},
    {"no": 10, "note": "작은 포장지 조각"},
    {"no": 11, "note": "스티로폼 조각"},
    {"no": 12, "note": "흙 묻은 생수병 (합성)"},
]

# 2라운드: given = 다른 라벨러가 붙여 둔 라벨, answer = 실제 정답. given != answer 인 4장이 숨겨진 틀린 라벨
ROUND2 = [
    {"no": 1, "given": "plastic", "answer": "plastic"},
    {"no": 2, "given": "glass", "answer": "plastic"},
    {"no": 3, "given": "glass", "answer": "glass"},
    {"no": 4, "given": "glass", "answer": "glass"},
    {"no": 5, "given": "plastic", "answer": "glass"},
    {"no": 6, "given": "can", "answer": "can"},
    {"no": 7, "given": "can", "answer": "can"},
    {"no": 8, "given": "other", "answer": "can"},
    {"no": 9, "given": "other", "answer": "other"},
    {"no": 10, "given": "other", "answer": "other"},
    {"no": 11, "given": "plastic", "answer": "plastic"},
    {"no": 12, "given": "can", "answer": "plastic"},
]
WRONG_NOS = [p["no"] for p in ROUND2 if p["given"] != p["answer"]]

# 기준 세우기: 클래스마다 단서와 한 줄 기준, 헷갈리는 경우 두 가지를 미리 정한다
SPECIAL = {
    "은박 처리": ("은박지·은박 접시는 어디로 분류할까?", ["캔 (금속이니까)", "기타 (캔이 아니니까)"]),
    "흙 처리": ("흙에 덮여 재질이 잘 안 보이면?", ["보이는 모양으로 가장 비슷한 것", "기타"]),
}
CRIT_SHEET = "2차시_기준표"
CLASS_CRIT_SHEET = "2차시_우리반기준표"

GOAL = 0.9  # 반 전체 목표 일치율
SHEET1 = "2차시_라벨링"
SHEET2 = "2차시_검수"
IMG = Path(__file__).parent / "images"


def photo(round_no: int, no: int):
    p = IMG / f"c2_r{round_no}" / f"{no}.jpg"
    return str(p) if p.exists() else None
