import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional
from rich.console import Console
from pathlib import Path
import numpy as np

console = Console()

class DummyEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __call__(self, input: chromadb.Documents) -> chromadb.Embeddings:
        # Return random vectors of dimension 384 (standard for all-MiniLM-L6-v2)
        # to ensure compatibility with the collection if it was created with the real model.
        # Or just zeros.
        return [np.zeros(384).tolist() for _ in input]

class VectorStore:
    """
    Manages code embeddings using ChromaDB.
    """
    def __init__(self, db_path: str = "./db"):
        self.client = chromadb.PersistentClient(path=db_path)
        
        try:
            # Try to load the real model
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to load embedding model (likely offline). Using dummy embeddings.[/yellow]")
            console.print(f"[dim]Error: {e}[/dim]")
            self.embedding_fn = DummyEmbeddingFunction()
        
        self.collection = self.client.get_or_create_collection(
            name="synapse_index",
            embedding_function=self.embedding_fn
        )

    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str], quiet: bool = False):
        """
        Add code snippets to the vector index.
        """
        if not documents:
            return
            
        try:
            self.collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            if not quiet:
                console.print(f"[green]Indexed {len(documents)} snippets.[/green]")
        except Exception as e:
            if not quiet:
                console.print(f"[red]Error indexing documents: {e}[/red]")

    def query(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Search for relevant code snippets.
        """
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results
        except Exception as e:
            console.print(f"[red]Error querying index: {e}[/red]")
            return {}

    def count(self) -> int:
        return self.collection.count()
