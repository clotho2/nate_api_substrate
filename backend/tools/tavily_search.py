#!/usr/bin/env python3
"""
Tavily AI Web Search - REAL Implementation
The best web search API for AI agents!

Tavily Features:
- AI-optimized search results
- Clean, structured data
- Fast and reliable
- Pricing: ~$5 for 1000 searches

API: https://tavily.com
Docs: https://docs.tavily.com
"""

import os
import httpx
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TavilySearch:
    """
    Tavily AI Web Search client.
    
    The best search API for AI agents - optimized for LLMs!
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Tavily client.
        
        Args:
            api_key: Tavily API key (defaults to env var TAVILY_API_KEY)
        """
        self.api_key = api_key or os.getenv('TAVILY_API_KEY')
        if not self.api_key:
            logger.warning("⚠️ TAVILY_API_KEY not set - web search will not work!")
        
        self.api_url = "https://api.tavily.com/search"
    
    def search(
        self,
        query: str,
        search_depth: str = "basic",  # "basic" or "advanced"
        max_results: int = 5,
        include_images: bool = False,
        include_answer: bool = True,
        include_raw_content: bool = False,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search the web using Tavily AI.
        
        Args:
            query: Search query
            search_depth: "basic" (faster) or "advanced" (more thorough)
            max_results: Max number of results (default: 5)
            include_images: Include image results
            include_answer: Include AI-generated answer summary
            include_raw_content: Include raw HTML content
            include_domains: Only search these domains
            exclude_domains: Exclude these domains
        
        Returns:
            {
                'query': str,
                'answer': str,  # AI-generated summary (if include_answer=True)
                'results': [
                    {
                        'title': str,
                        'url': str,
                        'content': str,  # Clean, AI-optimized excerpt
                        'score': float,  # Relevance score
                        'published_date': str
                    },
                    ...
                ],
                'images': [...],  # If include_images=True
                'response_time': float
            }
        """
        if not self.api_key:
            return {
                "status": "error",
                "message": "Tavily API key not configured. Set TAVILY_API_KEY environment variable.",
                "query": query
            }
        
        try:
            # Build request payload
            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": search_depth,
                "max_results": max_results,
                "include_images": include_images,
                "include_answer": include_answer,
                "include_raw_content": include_raw_content
            }
            
            if include_domains:
                payload["include_domains"] = include_domains
            
            if exclude_domains:
                payload["exclude_domains"] = exclude_domains
            
            logger.info(f"🔍 Tavily Search: '{query}' (depth={search_depth}, max={max_results})")
            
            # Make request
            with httpx.Client(timeout=30.0) as client:
                response = client.post(self.api_url, json=payload)
                
                if response.status_code != 200:
                    error_msg = f"Tavily API error: {response.status_code}"
                    logger.error(f"❌ {error_msg}")
                    return {
                        "status": "error",
                        "message": error_msg,
                        "query": query
                    }
                
                data = response.json()
                
                # Log results
                num_results = len(data.get('results', []))
                logger.info(f"✅ Tavily returned {num_results} results")
                
                if include_answer and 'answer' in data:
                    logger.info(f"📝 AI Answer: {data['answer'][:100]}...")
                
                return {
                    "status": "OK",
                    "query": query,
                    "answer": data.get('answer'),
                    "results": data.get('results', []),
                    "images": data.get('images', []),
                    "response_time": data.get('response_time', 0)
                }
        
        except httpx.TimeoutException:
            error_msg = "Tavily API timeout (30s)"
            logger.error(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "query": query
            }
        
        except Exception as e:
            error_msg = f"Tavily search failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "query": query
            }


# Singleton instance
_tavily_client: Optional[TavilySearch] = None


def get_tavily_client() -> TavilySearch:
    """Get or create Tavily client singleton"""
    global _tavily_client
    if _tavily_client is None:
        _tavily_client = TavilySearch()
    return _tavily_client


def web_search(
    query: str,
    search_depth: str = "basic",
    max_results: int = 5,
    include_answer: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Tavily Web Search - Simple interface for agents.
    
    Args:
        query: Search query
        search_depth: "basic" or "advanced"
        max_results: Max results (default: 5)
        include_answer: Include AI summary (default: True)
    
    Returns:
        Search results dict
    """
    client = get_tavily_client()
    return client.search(
        query=query,
        search_depth=search_depth,
        max_results=max_results,
        include_answer=include_answer,
        **kwargs
    )


if __name__ == "__main__":
    # Test
    print("\n🧪 Testing Tavily Search\n")
    
    result = web_search(
        query="What are the best practices for building AI agents in 2025?",
        search_depth="basic",
        max_results=3,
        include_answer=True
    )
    
    print(f"Status: {result.get('status')}")
    print(f"Query: {result.get('query')}")
    
    if result.get('answer'):
        print(f"\n📝 AI Answer:\n{result['answer']}\n")
    
    if result.get('results'):
        print(f"📊 Results ({len(result['results'])}):\n")
        for i, res in enumerate(result['results'], 1):
            print(f"{i}. {res.get('title')}")
            print(f"   URL: {res.get('url')}")
            print(f"   Score: {res.get('score', 0):.2f}")
            print(f"   Content: {res.get('content', '')[:100]}...")
            print()

