"""
정보처리기사 실기 기출문제 스크래퍼

여러 소스에서 기출문제를 수집합니다:
1. 웹 스크래핑 (블로그, 기출문제 사이트)
2. 샘플 데이터 (내장)
"""

import json
import os
import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

from config import RAW_DATA_DIR


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def scrape_from_url(url: str) -> list[dict]:
    """
    주어진 URL에서 기출문제를 스크래핑합니다.
    블로그나 기출문제 사이트의 HTML을 파싱하여
    문제-답 쌍을 추출합니다.
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        soup = BeautifulSoup(resp.text, "lxml")
    except requests.RequestException as e:
        print(f"[오류] URL 접근 실패: {url} - {e}")
        return []

    questions = []
    # 일반적인 블로그 본문 영역 탐색
    content_area = (
        soup.find("div", class_="entry-content")
        or soup.find("div", class_="post-content")
        or soup.find("div", class_="article-content")
        or soup.find("div", class_="tt_article_useless_p_margin")
        or soup.find("article")
        or soup.find("div", id="content")
        or soup.body
    )
    if not content_area:
        return questions

    text = content_area.get_text(separator="\n")
    # "문제 N." 또는 "N." 또는 "N)" 패턴으로 문제 분리
    pattern = r"(?:문제\s*)?(\d{1,2})\s*[.)]\s*(.+?)(?=(?:문제\s*)?\d{1,2}\s*[.)]|\Z)"
    matches = re.findall(pattern, text, re.DOTALL)

    for num, body in matches:
        body = body.strip()
        if len(body) < 10:
            continue
        # 답 분리 시도
        answer = ""
        ans_match = re.search(
            r"(?:정답|답|answer|해설)\s*[:：]\s*(.+?)(?:\n|$)",
            body, re.IGNORECASE
        )
        if ans_match:
            answer = ans_match.group(1).strip()
            body = body[:ans_match.start()].strip()

        questions.append({
            "number": int(num),
            "question": body,
            "answer": answer,
            "source_url": url,
        })

    return questions


def scrape_multiple_urls(urls: list[str], delay: float = 1.0) -> list[dict]:
    """여러 URL에서 기출문제를 수집합니다."""
    all_questions = []
    for url in urls:
        print(f"[스크래핑] {url}")
        questions = scrape_from_url(url)
        print(f"  -> {len(questions)}개 문제 수집")
        all_questions.extend(questions)
        time.sleep(delay)
    return all_questions


def load_sample_data() -> list[dict]:
    """내장된 샘플 기출문제 데이터를 로드합니다."""
    sample_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data", "sample_questions.json"
    )
    if os.path.exists(sample_path):
        with open(sample_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_questions(questions: list[dict], filename: str = "scraped_questions.json"):
    """수집된 문제를 JSON 파일로 저장합니다."""
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    filepath = os.path.join(RAW_DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"[저장] {len(questions)}개 문제 -> {filepath}")
    return filepath


def load_questions(filename: str = "scraped_questions.json") -> list[dict]:
    """저장된 문제를 로드합니다."""
    filepath = os.path.join(RAW_DATA_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def run_scraper(urls: Optional[list[str]] = None) -> list[dict]:
    """
    스크래퍼를 실행합니다.
    URL이 주어지면 웹에서 수집하고,
    없으면 샘플 데이터를 사용합니다.
    """
    if urls:
        questions = scrape_multiple_urls(urls)
        if questions:
            save_questions(questions)
            return questions
        print("[경고] 스크래핑 결과가 없습니다. 샘플 데이터를 사용합니다.")

    # 샘플 데이터 로드
    questions = load_sample_data()
    if questions:
        print(f"[샘플] {len(questions)}개 샘플 기출문제 로드")
        save_questions(questions)
    else:
        print("[오류] 사용 가능한 데이터가 없습니다.")
    return questions


if __name__ == "__main__":
    # 사용 예시: URL 없이 실행하면 샘플 데이터 사용
    data = run_scraper()
    print(f"\n총 {len(data)}개 문제 수집 완료")
