"""
벡터 스토어 모듈

ChromaDB를 사용하여 기출문제 청크를 임베딩하고
유사도 검색을 수행합니다.
"""

import chromadb
from chromadb.utils import embedding_functions

from config import CHROMA_DB_PATH, COLLECTION_NAME, EMBEDDING_MODEL, TOP_K


class VectorStore:
    """ChromaDB 기반 벡터 스토어"""

    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, chunks: list[dict]):
        """청크 리스트를 벡터 스토어에 추가합니다."""
        if not chunks:
            print("[벡터DB] 추가할 청크가 없습니다.")
            return

        ids = [c["id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        # 기존 데이터 제거 후 새로 추가
        existing = self.collection.get()
        if existing["ids"]:
            self.collection.delete(ids=existing["ids"])

        # 배치 단위로 추가 (ChromaDB 제한 고려)
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            end = min(i + batch_size, len(ids))
            self.collection.add(
                ids=ids[i:end],
                documents=documents[i:end],
                metadatas=metadatas[i:end],
            )

        print(f"[벡터DB] {len(chunks)}개 청크 인덱싱 완료")

    def search(self, query: str, top_k: int = TOP_K, category: str = "") -> list[dict]:
        """
        쿼리와 유사한 문서를 검색합니다.

        Args:
            query: 검색 키워드 또는 문장
            top_k: 반환할 최대 결과 수
            category: 특정 카테고리로 필터링 (선택)

        Returns:
            검색 결과 리스트 [{text, metadata, distance}]
        """
        where_filter = None
        if category:
            where_filter = {"category": category}

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter,
        )

        output = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                output.append({
                    "text": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0,
                })
        return output

    def get_count(self) -> int:
        """저장된 문서 수를 반환합니다."""
        return self.collection.count()

    def reset(self):
        """컬렉션을 초기화합니다."""
        self.client.delete_collection(COLLECTION_NAME)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )
        print("[벡터DB] 컬렉션 초기화 완료")
