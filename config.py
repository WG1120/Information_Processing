import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI API 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ChromaDB 설정
CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION_NAME = "exam_questions"

# 데이터 경로
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")

# 청킹 설정
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# 임베딩 모델
EMBEDDING_MODEL = "jhgan/ko-sroberta-multitask"

# LLM 설정
LLM_MODEL = "gpt-4o-mini"
MAX_TOKENS = 2000
TEMPERATURE = 0.7

# 검색 설정
TOP_K = 5
