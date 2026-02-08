"""
정보처리기사 실기 연습문제 생성기 (RAG 기반)

핵심 키워드를 입력하면 기출문제를 참조하여
유사한 연습문제를 생성합니다.

사용법:
    python main.py                    # 대화형 모드
    python main.py --keyword "SQL"    # 키워드 직접 지정
    python main.py --setup            # 초기 설정 (스크래핑 + 청킹 + 인덱싱)
"""

import argparse
import sys

from scraper.exam_scraper import run_scraper, load_sample_data, save_questions
from processor.chunker import run_chunker, load_chunks
from rag.vector_store import VectorStore
from rag.generator import generate_questions


def setup_pipeline(urls: list[str] | None = None):
    """
    전체 파이프라인을 초기화합니다.
    1. 기출문제 수집 (스크래핑 또는 샘플 데이터)
    2. 청킹
    3. 벡터 스토어 인덱싱
    """
    print("=" * 60)
    print("  정보처리기사 실기 RAG 시스템 초기 설정")
    print("=" * 60)

    # 1단계: 데이터 수집
    print("\n[1/3] 기출문제 수집 중...")
    questions = run_scraper(urls)
    if not questions:
        print("[오류] 기출문제를 수집할 수 없습니다.")
        return False

    # 2단계: 청킹
    print("\n[2/3] 문제 청킹 중...")
    chunks = run_chunker(questions=questions)
    if not chunks:
        print("[오류] 청킹에 실패했습니다.")
        return False

    # 3단계: 벡터 인덱싱
    print("\n[3/3] 벡터 인덱싱 중...")
    store = VectorStore()
    store.add_chunks(chunks)
    print(f"\n[완료] 총 {store.get_count()}개 문서 인덱싱 완료!")
    return True


def search_and_generate(keyword: str, num_questions: int = 3, category: str = ""):
    """키워드로 검색하고 연습문제를 생성합니다."""
    store = VectorStore()

    if store.get_count() == 0:
        print("[경고] 벡터 DB가 비어있습니다. 초기 설정을 먼저 실행합니다.")
        if not setup_pipeline():
            return
        store = VectorStore()

    print(f"\n[검색] '{keyword}' 관련 기출문제 검색 중...")
    results = store.search(keyword, category=category)

    if not results:
        print(f"[결과] '{keyword}'와 관련된 기출문제를 찾을 수 없습니다.")
        return

    print(f"[검색] {len(results)}개 관련 문제 발견 (유사도 기준)")
    print("\n[생성] 연습문제 생성 중...\n")

    output = generate_questions(keyword, results, num_questions)
    print(output)


def interactive_mode():
    """대화형 모드로 실행합니다."""
    print("=" * 60)
    print("  정보처리기사 실기 연습문제 생성기 (RAG 기반)")
    print("=" * 60)
    print()
    print("사용 가능한 명령어:")
    print("  키워드 입력  - 관련 연습문제 생성")
    print("  /setup      - 초기 설정 (데이터 수집 + 인덱싱)")
    print("  /count      - 인덱싱된 문서 수 확인")
    print("  /categories - 카테고리 목록 보기")
    print("  /help       - 도움말")
    print("  /quit       - 종료")
    print()

    # 벡터 스토어 초기화 체크
    store = VectorStore()
    if store.get_count() == 0:
        print("[안내] 벡터 DB가 비어있습니다.")
        answer = input("초기 설정을 실행하시겠습니까? (y/n): ").strip().lower()
        if answer in ("y", "yes", "ㅛ"):
            setup_pipeline()
        else:
            print("[안내] /setup 명령으로 나중에 설정할 수 있습니다.\n")

    categories = [
        "소프트웨어 설계", "소프트웨어 공학", "데이터베이스",
        "프로그래밍", "네트워크", "정보보안",
    ]

    while True:
        try:
            user_input = input("\n키워드를 입력하세요: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n프로그램을 종료합니다.")
            break

        if not user_input:
            continue

        if user_input == "/quit":
            print("프로그램을 종료합니다.")
            break
        elif user_input == "/setup":
            setup_pipeline()
        elif user_input == "/count":
            store = VectorStore()
            print(f"인덱싱된 문서 수: {store.get_count()}")
        elif user_input == "/categories":
            print("카테고리 목록:")
            for cat in categories:
                print(f"  - {cat}")
        elif user_input == "/help":
            print("사용법:")
            print("  1. 핵심 키워드를 입력하면 관련 연습문제를 생성합니다.")
            print("     예: SQL, 디자인 패턴, 포인터, 정규화, OSI")
            print("  2. '카테고리:키워드' 형식으로 입력하면 특정 분야를 필터링합니다.")
            print("     예: 데이터베이스:정규화, 프로그래밍:Java")
        else:
            # 카테고리 필터링
            category = ""
            keyword = user_input
            if ":" in user_input:
                parts = user_input.split(":", 1)
                category = parts[0].strip()
                keyword = parts[1].strip()

            search_and_generate(keyword, category=category)


def main():
    parser = argparse.ArgumentParser(
        description="정보처리기사 실기 연습문제 생성기 (RAG 기반)"
    )
    parser.add_argument(
        "--keyword", "-k",
        type=str,
        help="검색할 핵심 키워드",
    )
    parser.add_argument(
        "--setup", "-s",
        action="store_true",
        help="초기 설정 실행 (데이터 수집 + 인덱싱)",
    )
    parser.add_argument(
        "--num", "-n",
        type=int,
        default=3,
        help="생성할 문제 수 (기본: 3)",
    )
    parser.add_argument(
        "--category", "-c",
        type=str,
        default="",
        help="카테고리 필터 (예: 데이터베이스, 프로그래밍)",
    )
    parser.add_argument(
        "--urls",
        nargs="+",
        help="스크래핑할 URL 목록",
    )

    args = parser.parse_args()

    if args.setup:
        setup_pipeline(args.urls)
    elif args.keyword:
        search_and_generate(args.keyword, args.num, args.category)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
