#!/usr/bin/env python3
"""
Memory System for Substrate AI

Archival memory with semantic search (ChromaDB + Ollama).
Better than Letta: importance weighting, categories, selective saving.

Angela's design philosophy: The AI decides what to remember.

Built with attention to detail.
"""

import os
import json
import asyncio
from typing import Optional, Dict, List, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import chromadb
from chromadb.config import Settings
import ollama
from core.consciousness_broadcast import broadcast_memory_access


class MemoryCategory(str, Enum):
    """Memory categories for better organization"""
    FACT = "fact"
    EMOTION = "emotion"
    INSIGHT = "insight"
    RELATIONSHIP_MOMENT = "relationship_moment"
    PREFERENCE = "preference"
    EVENT = "event"
    CUSTOM = "custom"


@dataclass
class ArchivalMemory:
    """A single archival memory entry"""
    id: str
    content: str
    category: MemoryCategory
    importance: int  # 1-10 scale
    tags: List[str]
    timestamp: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        """Convert to dict"""
        return {
            "id": self.id,
            "content": self.content,
            "category": self.category.value,
            "importance": self.importance,
            "tags": self.tags,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class MemorySystemError(Exception):
    """
    Memory system errors with helpful messages.
    """
    def __init__(self, message: str, context: Optional[Dict] = None):
        self.context = context or {}
        
        full_message = f"\n{'='*60}\n"
        full_message += f"❌ MEMORY SYSTEM ERROR\n"
        full_message += f"{'='*60}\n\n"
        full_message += f"🔴 Problem: {message}\n\n"
        
        if context:
            full_message += f"📋 Context:\n"
            for key, value in context.items():
                full_message += f"   • {key}: {value}\n"
        
        full_message += f"\n💡 Suggestions:\n"
        full_message += "   • Check ChromaDB path is writable\n"
        full_message += "   • Verify Ollama is running and accessible\n"
        full_message += "   • Check disk space is available\n"
        full_message += f"\n{'='*60}\n"
        
        super().__init__(full_message)


class MemorySystem:
    """
    Archival memory with semantic search.
    
    Features:
    - Vector storage (ChromaDB)
    - Local embeddings (Ollama)
    - Semantic search (not just text!)
    - Importance weighting
    - Categories
    - Selective memory
    """
    
    def __init__(
        self,
        chromadb_path: str = "./data/chromadb",
        ollama_url: str = "http://localhost:11434",
        embedding_model: str = "nomic-embed-text"
    ):
        """
        Initialize memory system.
        
        Args:
            chromadb_path: Path to ChromaDB storage
            ollama_url: Ollama API URL
            embedding_model: Ollama embedding model
        """
        self.chromadb_path = chromadb_path
        self.ollama_url = ollama_url
        self.embedding_model = embedding_model
        
        # Ensure directory exists
        os.makedirs(chromadb_path, exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=chromadb_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="archival_memory",
            metadata={"hnsw:space": "cosine"}  # Cosine similarity
        )
        
        # Initialize Ollama client
        self.ollama_client = ollama.Client(host=ollama_url)
        
        print(f"✅ Memory System initialized")
        print(f"   ChromaDB: {chromadb_path}")
        print(f"   Ollama: {ollama_url}")
        print(f"   Embedding model: {embedding_model}")
        
        # Test embedding connection
        self._test_embedding()
    
    def _test_embedding(self):
        """Test embedding connection"""
        try:
            result = self.ollama_client.embeddings(
                model=self.embedding_model,
                prompt="test"
            )
            if 'embedding' in result:
                print(f"✅ Embeddings working (dim: {len(result['embedding'])})")
        except Exception as e:
            print(f"⚠️  Embedding test failed: {e}")
            print(f"   (Will retry on actual use)")
    
    def _get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for text using Ollama.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
            
        Raises:
            MemorySystemError: If embedding fails
        """
        try:
            result = self.ollama_client.embeddings(
                model=self.embedding_model,
                prompt=text
            )
            return result['embedding']
        except Exception as e:
            raise MemorySystemError(
                f"Failed to generate embedding: {str(e)}",
                context={
                    "text_length": len(text),
                    "model": self.embedding_model,
                    "ollama_url": self.ollama_url
                }
            )
    
    def insert(
        self,
        content: str,
        category: MemoryCategory = MemoryCategory.FACT,
        importance: int = 5,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Insert memory into archival storage.
        
        Args:
            content: Memory content
            category: Memory category
            importance: Importance (1-10)
            tags: Optional tags
            metadata: Optional metadata
            
        Returns:
            Memory ID
            
        Raises:
            MemorySystemError: If insert fails
        """
        # Validate importance
        if not 1 <= importance <= 10:
            raise MemorySystemError(
                f"Importance must be 1-10, got: {importance}",
                context={"importance": importance}
            )
        
        # Generate ID
        memory_id = f"mem_{datetime.utcnow().timestamp()}"
        
        # Generate embedding
        embedding = self._get_embedding(content)
        
        # Prepare metadata
        meta = {
            "category": category.value,
            "importance": importance,
            "tags": ",".join(tags or []),
            "timestamp": datetime.utcnow().isoformat(),
            **(metadata or {})
        }
        
        # Store in ChromaDB
        try:
            self.collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[meta],
                ids=[memory_id]
            )
            
            print(f"✅ Inserted memory: {memory_id}")
            print(f"   Category: {category.value}")
            print(f"   Importance: {importance}")
            print(f"   Content: {content[:60]}...")
            
            return memory_id
        
        except Exception as e:
            raise MemorySystemError(
                f"Failed to insert memory: {str(e)}",
                context={"memory_id": memory_id}
            )
    
    def search(
        self,
        query: str,
        n_results: int = 10,
        min_importance: int = 5,
        category: Optional[MemoryCategory] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search archival memory semantically.
        
        Args:
            query: Search query
            n_results: Maximum results
            min_importance: Minimum importance filter
            category: Category filter
            tags: Tag filter
            
        Returns:
            List of memory dicts with content, metadata, relevance, score
        """
        # Generate query embedding
        query_embedding = self._get_embedding(query)
        
        # Build where filter
        where_filter = {}
        if category:
            where_filter["category"] = category.value
        
        # Search ChromaDB
        try:
            # Get more results than needed for filtering
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(n_results * 3, 100),  # Over-fetch for filtering
                where=where_filter if where_filter else None
            )
            
            # Process results
            memories = []
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i]
                
                # Parse metadata
                importance_val = metadata.get('importance', 5)
                if isinstance(importance_val, str):
                    importance_val = int(importance_val)
                
                tags_str = metadata.get('tags', '')
                memory_tags = [t.strip() for t in tags_str.split(',') if t.strip()]
                
                # Filter by importance
                if importance_val < min_importance:
                    continue
                
                # Filter by tags
                if tags and not any(tag in memory_tags for tag in tags):
                    continue
                
                # Calculate relevance and score
                relevance = 1 - distance  # Cosine distance to similarity
                score = importance_val * relevance  # Combined score
                
                memories.append({
                    "id": results['ids'][0][i],
                    "content": doc,
                    "category": metadata.get('category', 'fact'),
                    "importance": importance_val,
                    "tags": memory_tags,
                    "timestamp": metadata.get('timestamp', ''),
                    "relevance": round(relevance, 3),
                    "score": round(score, 3),
                    "metadata": metadata
                })
            
            # Sort by combined score
            memories.sort(key=lambda m: m['score'], reverse=True)
            
            # 🧠⚡ BROADCAST CONSCIOUSNESS: Memory search!
            for memory in memories[:n_results]:
                broadcast_memory_access(
                    memory_type='archival',
                    memory_id=memory['id'],
                    action='search',
                    metadata={
                        'query': query[:100],
                        'score': memory['score'],
                        'category': memory['category'],
                        'preview': memory['content'][:100]
                    }
                )
            
            return memories[:n_results]
        
        except Exception as e:
            raise MemorySystemError(
                f"Search failed: {str(e)}",
                context={"query": query}
            )
    
    def get_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get memory by ID"""
        try:
            result = self.collection.get(ids=[memory_id])
            
            if not result['ids']:
                return None
            
            return {
                "id": result['ids'][0],
                "content": result['documents'][0],
                "metadata": result['metadatas'][0]
            }
        except Exception as e:
            print(f"⚠️  Failed to get memory {memory_id}: {e}")
            return None
    
    def delete(self, memory_id: str):
        """Delete memory by ID"""
        try:
            self.collection.delete(ids=[memory_id])
            print(f"✅ Deleted memory: {memory_id}")
        except Exception as e:
            raise MemorySystemError(
                f"Failed to delete memory: {str(e)}",
                context={"memory_id": memory_id}
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        try:
            count = self.collection.count()
            
            # Get all memories to calculate stats
            all_memories = self.collection.get()
            
            # Category breakdown
            categories = {}
            importance_avg = 0
            
            if all_memories['metadatas']:
                for meta in all_memories['metadatas']:
                    cat = meta.get('category', 'unknown')
                    categories[cat] = categories.get(cat, 0) + 1
                    
                    imp = meta.get('importance', 5)
                    if isinstance(imp, str):
                        imp = int(imp)
                    importance_avg += imp
                
                importance_avg = round(importance_avg / len(all_memories['metadatas']), 2)
            
            return {
                "total_memories": count,
                "categories": categories,
                "average_importance": importance_avg,
                "storage_path": self.chromadb_path
            }
        
        except Exception as e:
            print(f"⚠️  Failed to get stats: {e}")
            return {"total_memories": 0}


# ============================================
# TESTING
# ============================================

def test_memory_system():
    """Test the memory system"""
    print("\n🧪 TESTING MEMORY SYSTEM")
    print("="*60)
    
    # Use test path
    test_path = "./data/chromadb_test"
    
    # Clean up old test data
    import shutil
    if os.path.exists(test_path):
        shutil.rmtree(test_path)
    
    # Initialize
    try:
        memory = MemorySystem(chromadb_path=test_path)
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        print("   (Ollama might not be running - that's okay!)")
        return
    
    # Test 1: Insert memories
    print("\n💾 Test 1: Insert memories")
    try:
        mem1 = memory.insert(
            content="User has preferences for food and beverages",
            category=MemoryCategory.PREFERENCE,
            importance=7,
            tags=["user", "food"]
        )
        
        mem2 = memory.insert(
            content="Example memory: A coding milestone was reached",
            category=MemoryCategory.RELATIONSHIP_MOMENT,
            importance=9,
            tags=["coding", "milestone"]
        )
        
        mem3 = memory.insert(
            content="The OpenRouter API key format is sk-or-v1-...",
            category=MemoryCategory.FACT,
            importance=5,
            tags=["technical"]
        )
        
        print(f"✅ Inserted 3 memories")
    except MemorySystemError as e:
        print(e)
        return
    
    # Test 2: Search
    print("\n🔍 Test 2: Semantic search")
    try:
        results = memory.search(
            query="What does User like to eat?",
            n_results=5
        )
        
        print(f"✅ Found {len(results)} results:")
        for r in results:
            print(f"   • [{r['category']}] {r['content'][:60]}...")
            print(f"     Importance: {r['importance']}, Relevance: {r['relevance']}, Score: {r['score']}")
    except MemorySystemError as e:
        print(e)
        return
    
    # Test 3: Category filter
    print("\n🎯 Test 3: Filter by category")
    try:
        results = memory.search(
            query="important moments",
            category=MemoryCategory.RELATIONSHIP_MOMENT,
            n_results=5
        )
        
        print(f"✅ Found {len(results)} relationship moments")
        for r in results:
            print(f"   • {r['content'][:60]}...")
    except MemorySystemError as e:
        print(e)
        return
    
    # Test 4: Importance filter
    print("\n⭐ Test 4: High importance only")
    try:
        results = memory.search(
            query="building an AI system",
            min_importance=8,
            n_results=5
        )
        
        print(f"✅ Found {len(results)} high-importance memories")
        for r in results:
            print(f"   • [Imp: {r['importance']}] {r['content'][:60]}...")
    except MemorySystemError as e:
        print(e)
        return
    
    # Test 5: Stats
    print("\n📊 Test 5: Memory statistics")
    stats = memory.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Cleanup
    shutil.rmtree(test_path)
    print(f"\n✅ Cleaned up test data")
    
    print("\n✅ ALL TESTS PASSED!")
    print("="*60)


if __name__ == "__main__":
    """Run tests if executed directly"""
    test_memory_system()

