"""
연습문제 생성 모듈

검색된 기출문제를 참조하여 OpenAI API로
유사한 연습문제를 생성합니다.
"""

from openai import OpenAI

from config import OPENAI_API_KEY, LLM_MODEL, MAX_TOKENS, TEMPERATURE


SYSTEM_PROMPT = """당신은 정보처리기사 실기 시험 전문 출제위원입니다.
주어진 기출문제들을 참고하여, 유사하지만 새로운 연습문제를 생성해야 합니다.

연습문제 생성 규칙:
1. 기출문제와 동일한 형식(단답형, 서술형, 코드 실행 결과 등)을 유지합니다.
2. 기출문제와 동일한 난이도를 유지합니다.
3. 기출문제의 핵심 개념을 다루되, 문제 내용은 새롭게 구성합니다.
4. 정답과 간단한 해설을 함께 제공합니다.
5. 문제는 한국어로 작성합니다.
6. 실제 시험에 출제될 수 있는 실전적인 문제를 만듭니다.
"""


def build_context(references: list[dict]) -> str:
    """검색된 참조 문서들을 컨텍스트 문자열로 조합합니다."""
    context_parts = []
    for i, ref in enumerate(references, 1):
        context_parts.append(f"--- 참고 기출문제 {i} ---\n{ref['text']}\n")
    return "\n".join(context_parts)


def generate_questions(
    keyword: str,
    references: list[dict],
    num_questions: int = 3,
) -> str:
    """
    키워드와 참조 기출문제를 기반으로 연습문제를 생성합니다.

    Args:
        keyword: 사용자가 입력한 핵심 키워드
        references: 벡터 검색으로 찾은 관련 기출문제
        num_questions: 생성할 문제 수

    Returns:
        생성된 연습문제 텍스트
    """
    if not OPENAI_API_KEY:
        return _generate_template_questions(keyword, references, num_questions)

    client = OpenAI(api_key=OPENAI_API_KEY)
    context = build_context(references)

    user_prompt = f"""다음은 '{keyword}' 관련 정보처리기사 실기 기출문제입니다:

{context}

위 기출문제를 참고하여, '{keyword}' 주제로 새로운 연습문제 {num_questions}개를 생성해 주세요.

각 문제에 대해 다음 형식으로 작성해 주세요:
[문제 N]
(문제 내용)

[정답]
(정답 내용)

[해설]
(간단한 해설)

---
"""

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[오류] LLM API 호출 실패: {e}")
        return _generate_template_questions(keyword, references, num_questions)


def _generate_template_questions(
    keyword: str,
    references: list[dict],
    num_questions: int,
) -> str:
    """
    API 키가 없을 때 참조 문서 기반으로 템플릿 연습문제를 생성합니다.
    실제 LLM 없이도 기본적인 연습이 가능하도록 합니다.
    """
    output_parts = [
        f"=== '{keyword}' 관련 연습문제 ===\n",
        "(OpenAI API 키가 설정되지 않아 템플릿 기반으로 생성합니다.)\n",
        "아래 기출문제를 참고하여 직접 연습해 보세요:\n",
    ]

    for i, ref in enumerate(references[:num_questions], 1):
        meta = ref.get("metadata", {})
        year = meta.get("year", "")
        session = meta.get("session", "")
        category = meta.get("category", "")
        similarity = 1 - ref.get("distance", 0)

        output_parts.append(f"\n{'='*50}")
        output_parts.append(f"[참고 기출문제 {i}]")
        if year:
            output_parts.append(f"출처: {year}년 {session}")
        if category:
            output_parts.append(f"분야: {category}")
        output_parts.append(f"유사도: {similarity:.1%}")
        output_parts.append(f"\n{ref['text']}")

    output_parts.append(f"\n{'='*50}")
    output_parts.append("\n[연습 가이드]")
    output_parts.append(f"1. 위 기출문제의 핵심 개념을 정리해 보세요.")
    output_parts.append(f"2. 유사한 문제를 스스로 만들어 풀어 보세요.")
    output_parts.append(f"3. '{keyword}' 관련 추가 개념을 학습하세요.")
    output_parts.append(
        "\nTip: .env 파일에 OPENAI_API_KEY를 설정하면 "
        "AI가 자동으로 새로운 연습문제를 생성합니다."
    )

    return "\n".join(output_parts)
