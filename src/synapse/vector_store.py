try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions
    _CHROMADB_AVAILABLE = True
except Exception as e:
    _CHROMADB_AVAILABLE = False
    chromadb = None
    embedding_functions = None
    print(f"[Warning] ChromaDB not available: {e}")

from typing import List, Dict, Any, Optional
from rich.console import Console
from pathlib import Path
import numpy as np
import torch

from sentence_transformers import SentenceTransformer
import os

console = Console()

if _CHROMADB_AVAILABLE:
    class DummyEmbeddingFunction(embedding_functions.EmbeddingFunction):
        def __call__(self, input: chromadb.Documents) -> chromadb.Embeddings:
            # Return random vectors of dimension 768 (standard for jina-embeddings-v2-base-en)
            return [np.zeros(768).tolist() for _ in input]
else:
    class DummyEmbeddingFunction:
        pass

if _CHROMADB_AVAILABLE:
    class JinaEmbeddingFunction(embedding_functions.EmbeddingFunction):
        """
        Jina Embeddings v2를 위한 커스텀 임베딩 함수.
        Uses SentenceTransformer for better compatibility.
        """
        def __init__(self, model_name: str = "jinaai/jina-embeddings-v2-base-en"):
            self.model_name = model_name

            try:
                # GPU/accelerator detection
                if torch.cuda.is_available():
                    self.device = "cuda"
                elif torch.backends.mps.is_available():
                    self.device = "mps"
                else:
                    self.device = "cpu"
                console.print(f"[dim]Jina 모델 로딩 중 ({self.device})...[/dim]")
                
                # Use SentenceTransformer instead of AutoModel for better stability
                self.model = SentenceTransformer(self.model_name, trust_remote_code=True, device=self.device)
                
            except Exception as e:
                raise RuntimeError(f"Jina 모델 로드 실패: {e}")

        def __call__(self, input: chromadb.Documents) -> chromadb.Embeddings:
            try:
                # Jina 모델 인코딩
                embeddings = self.model.encode(input, convert_to_numpy=True)
                return embeddings.tolist()
            except Exception as e:
                console.print(f"[red]문서 인코딩 오류: {e}[/red]")
                return [np.zeros(768).tolist() for _ in input]
else:
    class JinaEmbeddingFunction:
        def __init__(self, *args, **kwargs): pass
        def __call__(self, *args, **kwargs): return []

class VectorStore:
    """
    ChromaDB를 사용하여 코드 임베딩을 관리하는 클래스.
    """
    def __init__(self, db_path: str = "./db"):
        if not _CHROMADB_AVAILABLE:
            console.print("[yellow]VectorStore 비활성화 (ChromaDB 사용 불가).[/yellow]")
            self.collection = None
            self.embedding_fn = None
            return

        self.client = chromadb.PersistentClient(path=db_path)
        
        try:
            # Jina 모델 로드 시도
            self.embedding_fn = JinaEmbeddingFunction()
            console.print(f"[green]✓ Jina Embeddings v2 로드됨.[/green]")
        except Exception as e:
            console.print(f"[yellow]주의: Jina 모델 로드 실패. 더미 임베딩을 사용합니다.[/yellow]")
            console.print(f"[dim]오류: {e}[/dim]")
            self.embedding_fn = DummyEmbeddingFunction()
        
        self.collection = self.client.get_or_create_collection(
            name="synapse_index_v2", # 새로운 임베딩을 위한 새 컬렉션
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str], quiet: bool = False):
        """
        벡터 인덱스에 코드 조각 추가.
        """
        if not documents or not self.collection:
            return
            
        try:
            # 메모리 문제 방지를 위한 배치 처리
            # 환경 변수로 배치 크기 제어 가능 (기본값: 12)
            batch_size = int(os.getenv("SYNAPSE_BATCH_SIZE", "12"))
            total_batches = (len(documents) + batch_size - 1) // batch_size
            
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i : i + batch_size]
                batch_metas = metadatas[i : i + batch_size]
                batch_ids = ids[i : i + batch_size]
                
                # Debug input sizes
                for j, doc in enumerate(batch_docs):
                    if len(doc) > 30000:
                        console.print(f"[bold red]WARNING: Skipping/Truncating huge document ({len(doc)} chars): {batch_ids[j]}[/bold red]")
                        batch_docs[j] = doc[:30000] # Truncate aggressively

                console.print(f"[dim]DEBUG: Upserting batch {i//batch_size + 1}/{total_batches} ({len(batch_docs)} docs)...[/dim]")
                self.collection.upsert(
                    documents=batch_docs,
                    metadatas=batch_metas,
                    ids=batch_ids
                )
                console.print(f"[dim]DEBUG: Upsert finished.[/dim]")
 
                if not quiet:
                    # 간단한 진행 표시기 (필요시 구현)
                    console.print(f"[dim]Processed batch {i//batch_size + 1}/{total_batches}[/dim]")
            
            if not quiet:
                console.print(f"[green]{len(documents)}개 스니펫 인덱싱 완료.[/green]")
                
        except Exception as e:
            if not quiet:
                console.print(f"[red]문서 인덱싱 오류: {e}[/red]")

    def query(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """
        관련 코드 스니펫 검색.
        """
        if not self.collection:
            return {}
            
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results
        except Exception as e:
            console.print(f"[red]인덱스 쿼리 오류: {e}[/red]")
            return {}

    def count(self) -> int:
        if not self.collection:
            return 0
        return self.collection.count()
