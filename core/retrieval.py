"""Multi-source information retrieval system."""

from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
import asyncio

from core.models import Document
from storage.vector_db import VectorDB
from storage.memory_store import MemoryStore
from storage.knowledge_cache import KnowledgeCache
from core.text_utils import tokenize, normalize_text
from core.logger import get_logger

logger = get_logger(__name__)


class SparseRetriever:
    """BM25-based sparse retrieval."""
    
    def __init__(self):
        """Initialize sparse retriever."""
        self.bm25: Optional[BM25Okapi] = None
        self.documents: List[Document] = []
        self.tokenized_corpus: List[List[str]] = []
    
    def index_documents(self, documents: List[Document]) -> None:
        """
        Index documents for BM25 search.
        
        Args:
            documents: List of documents to index
        """
        self.documents = documents
        
        # Tokenize all documents
        self.tokenized_corpus = [
            tokenize(normalize_text(doc.text, lowercase=True))
            for doc in documents
        ]
        
        # Create BM25 index
        if self.tokenized_corpus:
            self.bm25 = BM25Okapi(self.tokenized_corpus)
            logger.info(f"Indexed {len(documents)} documents for BM25")
        else:
            logger.warning("No documents to index")
    
    def add_document(self, document: Document) -> None:
        """
        Add a single document to the index.
        
        Args:
            document: Document to add
        """
        self.documents.append(document)
        tokens = tokenize(normalize_text(document.text, lowercase=True))
        self.tokenized_corpus.append(tokens)
        
        # Rebuild BM25 index
        if self.tokenized_corpus:
            self.bm25 = BM25Okapi(self.tokenized_corpus)
    
    async def search(self, query: str, top_k: int = 20) -> List[Tuple[Document, float]]:
        """
        Search for relevant documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of (document, score) tuples
        """
        return await asyncio.to_thread(self._search_sync, query, top_k)
    
    def _search_sync(self, query: str, top_k: int) -> List[Tuple[Document, float]]:
        """Synchronous BM25 search."""
        if not self.bm25 or not self.documents:
            logger.warning("No documents indexed")
            return []
        
        # Tokenize query
        query_tokens = tokenize(normalize_text(query, lowercase=True))
        
        # Get BM25 scores
        scores = self.bm25.get_scores(query_tokens)
        
        # Get top-k indices
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        # Build results
        results = [
            (self.documents[idx], float(scores[idx]))
            for idx in top_indices
            if scores[idx] > 0
        ]
        
        return results



class DenseRetriever:
    """Embedding-based dense retrieval."""
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        vector_db: Optional[VectorDB] = None
    ):
        """
        Initialize dense retriever.
        
        Args:
            model_name: Sentence transformer model name
            vector_db: Vector database instance
        """
        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None
        self.vector_db = vector_db or VectorDB()
        self._load_model()
    
    def _load_model(self) -> None:
        """Load sentence transformer model."""
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            raise
    
    async def embed(self, text: str) -> np.ndarray:
        """
        Generate embedding for text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        return await asyncio.to_thread(self._embed_sync, text)
    
    def _embed_sync(self, text: str) -> np.ndarray:
        """Synchronous embedding generation."""
        return self.model.encode(text, convert_to_numpy=True)
    
    async def embed_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts
            
        Returns:
            Array of embeddings
        """
        return await asyncio.to_thread(self._embed_batch_sync, texts)
    
    def _embed_batch_sync(self, texts: List[str]) -> np.ndarray:
        """Synchronous batch embedding generation."""
        return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    
    async def index_documents(self, documents: List[Document]) -> None:
        """
        Index documents in vector database.
        
        Args:
            documents: List of documents to index
        """
        # Generate embeddings
        texts = [doc.text for doc in documents]
        embeddings = await self.embed_batch(texts)
        
        # Add to vector database
        doc_ids = [doc.id for doc in documents]
        metadata_list = [
            {'text': doc.text, 'source': doc.source, 'metadata': doc.metadata}
            for doc in documents
        ]
        
        await self.vector_db.add_batch(doc_ids, embeddings, metadata_list)
        logger.info(f"Indexed {len(documents)} documents in vector DB")
    
    async def search(
        self,
        query: str,
        top_k: int = 10,
        min_score: Optional[float] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            min_score: Minimum similarity score
            
        Returns:
            List of (doc_id, score, metadata) tuples
        """
        # Generate query embedding
        query_embedding = await self.embed(query)
        
        # Search vector database
        results = await self.vector_db.search(query_embedding, k=top_k, min_score=min_score)
        
        return results


class RetrievalSystem:
    """Two-stage retrieval system combining sparse and dense methods."""
    
    def __init__(
        self,
        sparse_retriever: Optional[SparseRetriever] = None,
        dense_retriever: Optional[DenseRetriever] = None,
        memory_store: Optional[MemoryStore] = None,
        knowledge_cache: Optional[KnowledgeCache] = None,
        use_reranking: bool = True
    ):
        """
        Initialize retrieval system.
        
        Args:
            sparse_retriever: Sparse retriever instance
            dense_retriever: Dense retriever instance
            memory_store: Memory store instance
            knowledge_cache: Knowledge cache instance
            use_reranking: Whether to use dense reranking
        """
        self.sparse_retriever = sparse_retriever or SparseRetriever()
        self.dense_retriever = dense_retriever or DenseRetriever()
        self.memory_store = memory_store
        self.knowledge_cache = knowledge_cache
        self.use_reranking = use_reranking
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        sources: Optional[List[str]] = None
    ) -> List[Document]:
        """
        Retrieve relevant documents from all sources.
        
        Args:
            query: Search query
            top_k: Number of results to return
            sources: List of sources to search (None = all)
            
        Returns:
            List of relevant documents
        """
        all_results = []
        
        # Retrieve from different sources
        if sources is None or 'memory' in sources:
            memory_results = await self.retrieve_memory(query, top_k)
            all_results.extend(memory_results)
        
        if sources is None or 'knowledge' in sources:
            knowledge_results = await self.retrieve_knowledge(query, top_k)
            all_results.extend(knowledge_results)
        
        # Deduplicate and rerank
        unique_results = self._deduplicate(all_results)
        
        if self.use_reranking and len(unique_results) > top_k:
            reranked = await self._rerank(query, unique_results, top_k)
            return reranked
        
        return unique_results[:top_k]
    
    async def retrieve_memory(self, query: str, top_k: int = 10) -> List[Document]:
        """
        Retrieve from memory store.
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of documents from memory
        """
        if not self.memory_store:
            return []
        
        # Search facts
        facts = await self.memory_store.retrieve_facts(limit=top_k)
        
        # Convert to documents
        documents = []
        for fact in facts:
            doc = Document(
                id=f"fact_{fact['id']}",
                text=f"{fact['key']}: {fact['value']}",
                source="memory",
                metadata=fact,
                confidence=fact.get('confidence', 1.0)
            )
            documents.append(doc)
        
        return documents
    
    async def retrieve_knowledge(self, query: str, top_k: int = 10) -> List[Document]:
        """
        Retrieve from knowledge cache using two-stage retrieval.
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of documents from knowledge cache
        """
        if not self.knowledge_cache:
            return []
        
        # Stage 1: Sparse retrieval (BM25)
        sparse_k = top_k * 2  # Get more candidates for reranking
        sparse_results = await self.sparse_retriever.search(query, top_k=sparse_k)
        
        if not sparse_results:
            return []
        
        # Stage 2: Dense reranking
        if self.use_reranking:
            documents = [doc for doc, _ in sparse_results]
            reranked = await self._rerank(query, documents, top_k)
            return reranked
        else:
            return [doc for doc, _ in sparse_results[:top_k]]
    
    async def _rerank(
        self,
        query: str,
        documents: List[Document],
        top_k: int
    ) -> List[Document]:
        """
        Rerank documents using dense retrieval.
        
        Args:
            query: Search query
            documents: Documents to rerank
            top_k: Number of results
            
        Returns:
            Reranked documents
        """
        # Generate query embedding
        query_embedding = await self.dense_retriever.embed(query)
        
        # Generate document embeddings
        doc_texts = [doc.text for doc in documents]
        doc_embeddings = await self.dense_retriever.embed_batch(doc_texts)
        
        # Calculate cosine similarities
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        doc_norms = doc_embeddings / np.linalg.norm(doc_embeddings, axis=1, keepdims=True)
        similarities = np.dot(doc_norms, query_norm)
        
        # Sort by similarity
        sorted_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Update confidence scores
        reranked = []
        for idx in sorted_indices:
            doc = documents[idx]
            doc.confidence = float(similarities[idx])
            reranked.append(doc)
        
        return reranked
    
    def _deduplicate(self, documents: List[Document]) -> List[Document]:
        """Remove duplicate documents."""
        seen_ids = set()
        unique = []
        
        for doc in documents:
            if doc.id not in seen_ids:
                seen_ids.add(doc.id)
                unique.append(doc)
        
        return unique
