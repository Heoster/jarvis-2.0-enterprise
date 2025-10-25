"""Vector database for semantic search using Faiss."""

import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import asyncio

from core.logger import get_logger

logger = get_logger(__name__)


class VectorDB:
    """Faiss-based vector database for CPU-optimized semantic search."""
    
    def __init__(
        self,
        dimension: int = 384,  # Default for all-MiniLM-L6-v2
        index_path: str = "data/vectors.index",
        metadata_path: str = "data/vectors_metadata.pkl",
        index_type: str = "flat"
    ):
        """
        Initialize vector database.
        
        Args:
            dimension: Dimension of embedding vectors
            index_path: Path to save/load Faiss index
            metadata_path: Path to save/load document metadata
            index_type: Type of index ('flat' for exact search, 'ivf' for approximate)
        """
        self.dimension = dimension
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)
        self.index_type = index_type
        
        # Create directories
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize or load index
        self.index = None
        self.metadata: List[Dict[str, Any]] = []
        self.id_to_idx: Dict[str, int] = {}
        
        if self.index_path.exists():
            self.load()
        else:
            self._create_index()
        
        logger.info(f"Vector DB initialized with {len(self.metadata)} documents")
    
    def _create_index(self) -> None:
        """Create a new Faiss index."""
        if self.index_type == "flat":
            # Exact search using L2 distance
            self.index = faiss.IndexFlatL2(self.dimension)
        elif self.index_type == "ivf":
            # Approximate search using IVF (Inverted File Index)
            quantizer = faiss.IndexFlatL2(self.dimension)
            nlist = 100  # Number of clusters
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
        else:
            raise ValueError(f"Unknown index type: {self.index_type}")
        
        logger.info(f"Created new {self.index_type} index with dimension {self.dimension}")

    
    async def add(
        self,
        doc_id: str,
        embedding: np.ndarray,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Add a document embedding to the index.
        
        Args:
            doc_id: Unique document identifier
            embedding: Document embedding vector
            metadata: Document metadata (text, source, etc.)
        """
        await asyncio.to_thread(self._add_sync, doc_id, embedding, metadata)
    
    def _add_sync(
        self,
        doc_id: str,
        embedding: np.ndarray,
        metadata: Dict[str, Any]
    ) -> None:
        """Synchronous add operation."""
        # Check if document already exists
        if doc_id in self.id_to_idx:
            logger.warning(f"Document {doc_id} already exists, skipping")
            return
        
        # Ensure embedding is 2D array
        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)
        
        # Ensure correct dimension
        if embedding.shape[1] != self.dimension:
            raise ValueError(
                f"Embedding dimension {embedding.shape[1]} doesn't match index dimension {self.dimension}"
            )
        
        # Add to index
        self.index.add(embedding.astype('float32'))
        
        # Store metadata
        idx = len(self.metadata)
        self.metadata.append({
            'id': doc_id,
            **metadata
        })
        self.id_to_idx[doc_id] = idx
        
        logger.debug(f"Added document {doc_id} at index {idx}")
    
    async def add_batch(
        self,
        doc_ids: List[str],
        embeddings: np.ndarray,
        metadata_list: List[Dict[str, Any]]
    ) -> None:
        """
        Add multiple document embeddings in batch.
        
        Args:
            doc_ids: List of document identifiers
            embeddings: Array of embeddings (n_docs x dimension)
            metadata_list: List of metadata dictionaries
        """
        await asyncio.to_thread(self._add_batch_sync, doc_ids, embeddings, metadata_list)
    
    def _add_batch_sync(
        self,
        doc_ids: List[str],
        embeddings: np.ndarray,
        metadata_list: List[Dict[str, Any]]
    ) -> None:
        """Synchronous batch add operation."""
        if len(doc_ids) != len(metadata_list) or len(doc_ids) != embeddings.shape[0]:
            raise ValueError("Mismatch in number of documents, embeddings, and metadata")
        
        # Filter out existing documents
        new_indices = [i for i, doc_id in enumerate(doc_ids) if doc_id not in self.id_to_idx]
        
        if not new_indices:
            logger.warning("All documents already exist, skipping batch")
            return
        
        # Get new embeddings and metadata
        new_embeddings = embeddings[new_indices]
        new_doc_ids = [doc_ids[i] for i in new_indices]
        new_metadata = [metadata_list[i] for i in new_indices]
        
        # Add to index
        self.index.add(new_embeddings.astype('float32'))
        
        # Store metadata
        start_idx = len(self.metadata)
        for i, (doc_id, meta) in enumerate(zip(new_doc_ids, new_metadata)):
            idx = start_idx + i
            self.metadata.append({
                'id': doc_id,
                **meta
            })
            self.id_to_idx[doc_id] = idx
        
        logger.info(f"Added {len(new_indices)} documents in batch")
    
    async def search(
        self,
        query_embedding: np.ndarray,
        k: int = 10,
        min_score: Optional[float] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            min_score: Minimum similarity score (optional)
            
        Returns:
            List of (doc_id, score, metadata) tuples
        """
        return await asyncio.to_thread(self._search_sync, query_embedding, k, min_score)
    
    def _search_sync(
        self,
        query_embedding: np.ndarray,
        k: int,
        min_score: Optional[float]
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Synchronous search operation."""
        if self.index.ntotal == 0:
            logger.warning("Index is empty, returning no results")
            return []
        
        # Ensure query is 2D array
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Ensure correct dimension
        if query_embedding.shape[1] != self.dimension:
            raise ValueError(
                f"Query dimension {query_embedding.shape[1]} doesn't match index dimension {self.dimension}"
            )
        
        # Search
        k = min(k, self.index.ntotal)
        distances, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # Convert distances to similarity scores (inverse of L2 distance)
        # Using 1 / (1 + distance) to get scores between 0 and 1
        scores = 1.0 / (1.0 + distances[0])
        
        # Build results
        results = []
        for idx, score in zip(indices[0], scores):
            if idx == -1:  # Faiss returns -1 for empty slots
                continue
            
            if min_score is not None and score < min_score:
                continue
            
            meta = self.metadata[idx]
            doc_id = meta['id']
            results.append((doc_id, float(score), meta))
        
        return results

    
    async def update(
        self,
        doc_id: str,
        embedding: np.ndarray,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Update a document's embedding and metadata.
        
        Note: Faiss doesn't support in-place updates, so we rebuild the index.
        For large indices, consider using remove + add instead.
        
        Args:
            doc_id: Document identifier
            embedding: New embedding vector
            metadata: New metadata
        """
        await asyncio.to_thread(self._update_sync, doc_id, embedding, metadata)
    
    def _update_sync(
        self,
        doc_id: str,
        embedding: np.ndarray,
        metadata: Dict[str, Any]
    ) -> None:
        """Synchronous update operation."""
        if doc_id not in self.id_to_idx:
            logger.warning(f"Document {doc_id} not found, adding as new")
            self._add_sync(doc_id, embedding, metadata)
            return
        
        # Get index
        idx = self.id_to_idx[doc_id]
        
        # Update metadata
        self.metadata[idx] = {
            'id': doc_id,
            **metadata
        }
        
        # For embedding update, we need to rebuild the index
        # This is expensive but necessary for Faiss
        logger.warning(f"Updating embedding for {doc_id} requires index rebuild")
        self._rebuild_index_with_update(idx, embedding)
    
    def _rebuild_index_with_update(self, idx: int, new_embedding: np.ndarray) -> None:
        """Rebuild index with updated embedding."""
        # Extract all embeddings
        all_embeddings = []
        for i in range(self.index.ntotal):
            if i == idx:
                all_embeddings.append(new_embedding.reshape(1, -1))
            else:
                # Reconstruct embedding from index
                embedding = self.index.reconstruct(i)
                all_embeddings.append(embedding.reshape(1, -1))
        
        # Rebuild index
        self._create_index()
        embeddings_array = np.vstack(all_embeddings)
        self.index.add(embeddings_array.astype('float32'))
    
    async def delete(self, doc_id: str) -> bool:
        """
        Delete a document from the index.
        
        Note: Faiss doesn't support deletion, so we mark as deleted and rebuild on save.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            True if deleted, False if not found
        """
        return await asyncio.to_thread(self._delete_sync, doc_id)
    
    def _delete_sync(self, doc_id: str) -> bool:
        """Synchronous delete operation."""
        if doc_id not in self.id_to_idx:
            logger.warning(f"Document {doc_id} not found")
            return False
        
        idx = self.id_to_idx[doc_id]
        
        # Mark as deleted in metadata
        self.metadata[idx]['_deleted'] = True
        del self.id_to_idx[doc_id]
        
        logger.debug(f"Marked document {doc_id} as deleted")
        return True
    
    def save(self) -> None:
        """Save index and metadata to disk."""
        # Remove deleted documents before saving
        self._compact_index()
        
        # Save Faiss index
        faiss.write_index(self.index, str(self.index_path))
        
        # Save metadata
        with open(self.metadata_path, 'wb') as f:
            pickle.dump({
                'metadata': self.metadata,
                'id_to_idx': self.id_to_idx,
                'dimension': self.dimension,
                'index_type': self.index_type
            }, f)
        
        logger.info(f"Saved vector DB with {len(self.metadata)} documents")
    
    def _compact_index(self) -> None:
        """Remove deleted documents and rebuild index."""
        # Find non-deleted documents
        active_indices = [
            i for i, meta in enumerate(self.metadata)
            if not meta.get('_deleted', False)
        ]
        
        if len(active_indices) == len(self.metadata):
            return  # No deletions
        
        logger.info(f"Compacting index: {len(self.metadata) - len(active_indices)} deletions")
        
        # Extract active embeddings
        active_embeddings = []
        for idx in active_indices:
            embedding = self.index.reconstruct(idx)
            active_embeddings.append(embedding)
        
        # Rebuild metadata and id_to_idx
        new_metadata = [self.metadata[i] for i in active_indices]
        new_id_to_idx = {meta['id']: i for i, meta in enumerate(new_metadata)}
        
        # Rebuild index
        self._create_index()
        if active_embeddings:
            embeddings_array = np.vstack(active_embeddings)
            self.index.add(embeddings_array.astype('float32'))
        
        self.metadata = new_metadata
        self.id_to_idx = new_id_to_idx
    
    def load(self) -> None:
        """Load index and metadata from disk."""
        if not self.index_path.exists():
            logger.warning(f"Index file not found: {self.index_path}")
            self._create_index()
            return
        
        # Load Faiss index
        self.index = faiss.read_index(str(self.index_path))
        
        # Load metadata
        if self.metadata_path.exists():
            with open(self.metadata_path, 'rb') as f:
                data = pickle.load(f)
                self.metadata = data['metadata']
                self.id_to_idx = data['id_to_idx']
                self.dimension = data.get('dimension', self.dimension)
                self.index_type = data.get('index_type', self.index_type)
        
        logger.info(f"Loaded vector DB with {len(self.metadata)} documents")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'total_documents': len(self.metadata),
            'index_size': self.index.ntotal,
            'dimension': self.dimension,
            'index_type': self.index_type,
            'deleted_documents': sum(1 for m in self.metadata if m.get('_deleted', False))
        }
    
    def close(self) -> None:
        """Save and close the database."""
        self.save()
        logger.info("Vector DB closed")
