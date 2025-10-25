"""Semantic Matching using Sentence Transformers for fuzzy matching and similarity-based routing."""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import asyncio

from core.logger import get_logger

logger = get_logger(__name__)


class SemanticMatcher:
    """
    Semantic matching using Sentence Transformers (all-MiniLM-L6-v2).
    Provides fuzzy matching and similarity-based routing.
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model_name = model_name
        self.model = None
        self.embeddings_cache = {}
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize Sentence Transformer model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Sentence Transformer loaded: {self.model_name}")
        except ImportError:
            logger.warning("sentence-transformers not installed. Run: pip install sentence-transformers")
        except Exception as e:
            logger.error(f"Failed to load Sentence Transformer: {e}")
    
    async def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        if not self.model:
            return self._fallback_similarity(text1, text2)
        
        return await asyncio.to_thread(self._compute_similarity_sync, text1, text2)
    
    def _compute_similarity_sync(self, text1: str, text2: str) -> float:
        """Synchronous similarity computation."""
        try:
            embeddings = self.model.encode([text1, text2])
            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )
            return float(similarity)
        except Exception as e:
            logger.error(f"Similarity computation failed: {e}")
            return self._fallback_similarity(text1, text2)
    
    def _fallback_similarity(self, text1: str, text2: str) -> float:
        """Fallback similarity using simple word overlap."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0.0
    
    async def find_most_similar(
        self,
        query: str,
        candidates: List[str],
        threshold: float = 0.5
    ) -> List[Tuple[str, float]]:
        """
        Find most similar candidates to query.
        
        Args:
            query: Query text
            candidates: List of candidate texts
            threshold: Minimum similarity threshold
            
        Returns:
            List of (candidate, similarity) tuples sorted by similarity
        """
        if not self.model:
            return [(c, self._fallback_similarity(query, c)) for c in candidates]
        
        return await asyncio.to_thread(
            self._find_most_similar_sync,
            query,
            candidates,
            threshold
        )
    
    def _find_most_similar_sync(
        self,
        query: str,
        candidates: List[str],
        threshold: float
    ) -> List[Tuple[str, float]]:
        """Synchronous similarity search."""
        try:
            query_embedding = self.model.encode([query])[0]
            candidate_embeddings = self.model.encode(candidates)
            
            similarities = []
            for i, candidate in enumerate(candidates):
                similarity = np.dot(query_embedding, candidate_embeddings[i]) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(candidate_embeddings[i])
                )
                if similarity >= threshold:
                    similarities.append((candidate, float(similarity)))
            
            return sorted(similarities, key=lambda x: x[1], reverse=True)
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []
    
    async def fuzzy_match(
        self,
        query: str,
        intents: Dict[str, List[str]],
        threshold: float = 0.6
    ) -> Optional[Tuple[str, float]]:
        """
        Fuzzy match query to intent examples.
        
        Args:
            query: User query
            intents: Dict of intent_name -> example_phrases
            threshold: Minimum similarity threshold
            
        Returns:
            (intent_name, confidence) or None
        """
        best_match = None
        best_score = 0.0
        
        for intent_name, examples in intents.items():
            similarities = await self.find_most_similar(query, examples, threshold)
            if similarities:
                max_sim = max(similarities, key=lambda x: x[1])
                if max_sim[1] > best_score:
                    best_score = max_sim[1]
                    best_match = intent_name
        
        if best_match and best_score >= threshold:
            return (best_match, best_score)
        return None
    
    async def semantic_search(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Semantic search over documents.
        
        Args:
            query: Search query
            documents: List of documents with 'text' field
            top_k: Number of top results
            
        Returns:
            Top-k most relevant documents with scores
        """
        if not self.model:
            return documents[:top_k]
        
        return await asyncio.to_thread(
            self._semantic_search_sync,
            query,
            documents,
            top_k
        )
    
    def _semantic_search_sync(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Synchronous semantic search."""
        try:
            query_embedding = self.model.encode([query])[0]
            doc_texts = [doc.get('text', '') for doc in documents]
            doc_embeddings = self.model.encode(doc_texts)
            
            scores = []
            for i, doc in enumerate(documents):
                similarity = np.dot(query_embedding, doc_embeddings[i]) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(doc_embeddings[i])
                )
                doc_with_score = doc.copy()
                doc_with_score['similarity_score'] = float(similarity)
                scores.append(doc_with_score)
            
            return sorted(scores, key=lambda x: x['similarity_score'], reverse=True)[:top_k]
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return documents[:top_k]
    
    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get embedding for text."""
        if not self.model:
            return None
        try:
            return self.model.encode([text])[0]
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None
