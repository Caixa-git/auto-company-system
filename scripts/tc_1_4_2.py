#!/usr/bin/env python3
"""TC-1.4.2: 회고 → 다음 창업 CEO 프롬프트 주입 검증"""
import sys

RETROSPECTIVE = {
    "outcome": "exit",
    "lessons_learned": [
        "초기 시장 검증 부족이 가장 큰 실수",
        "완성도 높은 제품이 Exit 가치 상승에 기여",
    ],
    "trait_reflection": "장인형 성향으로 인해 초기 속도가 느렸으나 품질은 좋았음",
}

# CEO 프롬프트에 주입될 회고 요약 형식
PROMPT_INJECTION = f"""
## 이전 창업 회고 (익명)
최근 Exit 성공. 핵심 교훈:
- 초기 시장 검증 부족이 가장 큰 실수
- 완성도 높은 제품이 Exit 가치 상승에 기여
- 장인형 성향: 초기 속도 느림, 품질 좋음
"""


def build_prompt(retro):
    """회고 데이터 → 프롬프트 주입 문자열"""
    lessons = "\n".join(f"- {l}" for l in retro["lessons_learned"])
    return f"""
## 이전 창업 회고 (익명)
최근 {retro["outcome"]} 성공. 핵심 교훈:
{lessons}
- {retro["trait_reflection"]}
""".strip()


def run():
    passed = 0
    failed = 0

    print("=" * 60)
    print("TC-1.4.2: 회고 → CEO 프롬프트 주입")
    print("=" * 60)

    # 회고 데이터 존재
    if RETROSPECTIVE["lessons_learned"]:
        print(f"  ✅ 회고 데이터 존재: {len(RETROSPECTIVE['lessons_learned'])}개 교훈")
        passed += 1
    else:
        print(f"  ❌ 회고 데이터 없음")
        failed += 1

    # 프롬프트 주입 형식 생성
    prompt = build_prompt(RETROSPECTIVE)
    checks = ["회고", "Exit", "교훈", "장인형"]
    for c in checks:
        if c in prompt:
            print(f"  ✅ '{c}' 주입됨")
            passed += 1
        else:
            print(f"  ❌ '{c}' 누락")
            failed += 1

    # 익명화 확인 (company_id 없음)
    if "C_" not in prompt:
        print(f"  ✅ 익명화: 회사 식별자 없음")
        passed += 1
    else:
        print(f"  ❌ 익명화 실패: 회사 식별자 발견")
        failed += 1

    print(f"\n결과: {passed} 통과, {failed} 실패 (총 {passed+failed}개)")
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
