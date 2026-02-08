# 정보처리기사 실기 연습문제 생성기 (RAG 기반)

핵심 키워드를 입력하면 기출문제를 참조하여 유사한 연습문제를 생성하는 RAG 기반 프로그램입니다.

## 구조

```
├── main.py                  # 메인 프로그램 (CLI)
├── config.py                # 설정
├── scraper/
│   └── exam_scraper.py      # 기출문제 스크래핑
├── processor/
│   └── chunker.py           # RAG용 문서 청킹
├── rag/
│   ├── vector_store.py      # ChromaDB 벡터 스토어
│   └── generator.py         # LLM 연습문제 생성
└── data/
    └── sample_questions.json # 샘플 기출문제
```

## 설치

```bash
pip install -r requirements.txt
```

## 설정

```bash
cp .env.example .env
# .env 파일에 OpenAI API 키 입력
```

## 사용법

### 초기 설정

```bash
python main.py --setup
```

### 대화형 모드

```bash
python main.py
```

### 키워드 직접 지정

```bash
python main.py --keyword "SQL"
python main.py --keyword "디자인 패턴" --num 5
python main.py --keyword "정규화" --category "데이터베이스"
```

### URL에서 기출문제 스크래핑

```bash
python main.py --setup --urls "https://example.com/exam1" "https://example.com/exam2"
```

## 카테고리

- 소프트웨어 설계
- 소프트웨어 공학
- 데이터베이스
- 프로그래밍 (C, Java, Python)
- 네트워크
- 정보보안
