"""
기출문제 청킹 모듈

스크래핑된 기출문제를 RAG 참조용 문서로 변환합니다.
각 문제를 독립적인 청크로 만들고, 메타데이터를 부착합니다.
"""

import json
import os
from typing import Optional

from config import PROCESSED_DATA_DIR, RAW_DATA_DIR


def create_chunk_text(question: dict) -> str:
    """
    하나의 기출문제를 RAG 검색에 최적화된 텍스트 청크로 변환합니다.
    문제, 답, 키워드, 메타 정보를 모두 포함합니다.
    """
    parts = []

    # 메타 정보
    year = question.get("year", "")
    session = question.get("session", "")
    number = question.get("number", "")
    category = question.get("category", "")
    subcategory = question.get("subcategory", "")

    if year and session:
        parts.append(f"[{year}년 {session} 제{number}문]")
    elif number:
        parts.append(f"[문제 {number}]")

    if category:
        header = f"분야: {category}"
        if subcategory:
            header += f" > {subcategory}"
        parts.append(header)

    # 문제 본문
    parts.append(f"\n문제:\n{question.get('question', '')}")

    # 정답
    answer = question.get("answer", "")
    if answer:
        parts.append(f"\n정답:\n{answer}")

    # 키워드
    keywords = question.get("keywords", [])
    if keywords:
        parts.append(f"\n키워드: {', '.join(keywords)}")

    return "\n".join(parts)


def create_metadata(question: dict, chunk_id: int) -> dict:
    """청크의 메타데이터를 생성합니다."""
    return {
        "chunk_id": str(chunk_id),
        "year": question.get("year", ""),
        "session": question.get("session", ""),
        "number": str(question.get("number", "")),
        "category": question.get("category", ""),
        "subcategory": question.get("subcategory", ""),
        "keywords": ", ".join(question.get("keywords", [])),
    }


def chunk_questions(questions: list[dict]) -> list[dict]:
    """
    기출문제 리스트를 RAG용 청크 리스트로 변환합니다.

    각 문제를 하나의 청크로 처리합니다.
    문제 단위가 의미적으로 완결된 단위이므로
    문제를 분할하지 않고 통째로 청크화합니다.
    """
    chunks = []
    for idx, q in enumerate(questions):
        chunk_text = create_chunk_text(q)
        metadata = create_metadata(q, idx)
        chunks.append({
            "id": f"chunk_{idx}",
            "text": chunk_text,
            "metadata": metadata,
        })
    return chunks


def save_chunks(chunks: list[dict], filename: str = "chunks.json"):
    """청크 데이터를 JSON 파일로 저장합니다."""
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    filepath = os.path.join(PROCESSED_DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"[청킹] {len(chunks)}개 청크 저장 -> {filepath}")
    return filepath


def load_chunks(filename: str = "chunks.json") -> list[dict]:
    """저장된 청크 데이터를 로드합니다."""
    filepath = os.path.join(PROCESSED_DATA_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def run_chunker(
    input_file: Optional[str] = None,
    questions: Optional[list[dict]] = None,
) -> list[dict]:
    """
    청킹 파이프라인을 실행합니다.

    Args:
        input_file: 입력 JSON 파일 경로 (questions가 없을 때 사용)
        questions: 직접 전달하는 문제 리스트

    Returns:
        생성된 청크 리스트
    """
    if questions is None:
        if input_file is None:
            input_file = os.path.join(RAW_DATA_DIR, "scraped_questions.json")
        if not os.path.exists(input_file):
            print(f"[오류] 입력 파일 없음: {input_file}")
            return []
        with open(input_file, "r", encoding="utf-8") as f:
            questions = json.load(f)

    print(f"[청킹] {len(questions)}개 문제 처리 중...")
    chunks = chunk_questions(questions)
    save_chunks(chunks)
    print(f"[청킹] 완료: {len(chunks)}개 청크 생성")
    return chunks


if __name__ == "__main__":
    chunks = run_chunker()
    if chunks:
        print(f"\n=== 청크 예시 ===")
        print(chunks[0]["text"][:300])
