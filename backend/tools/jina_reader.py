#!/usr/bin/env python3
"""
Jina AI Reader - FREE Webpage to Markdown Converter! 🔥

Jina AI offers a FREE API that converts ANY webpage to clean Markdown.
No API key needed! Just prepend URL with https://r.jina.ai/

Features:
- No rate limits (reasonable use)
- Clean Markdown output
- Removes ads, navigation, etc.
- Perfect for LLM context!

API: https://r.jina.ai/{url}
Docs: https://jina.ai/reader
"""

import logging
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)


class JinaReader:
    """
    Jina AI Reader - FREE webpage to Markdown converter.
    
    No API key needed! Completely free! 🎉
    """
    
    def __init__(self):
        """Initialize Jina Reader"""
        self.base_url = "https://r.jina.ai"
        self.client = httpx.Client(timeout=30.0)  # 30s timeout
        logger.info("✅ Jina AI Reader initialized (FREE!)")
    
    def fetch(
        self,
        url: str,
        max_chars: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Fetch webpage and convert to Markdown.
        
        Args:
            url: URL to fetch
            max_chars: Max characters to return (to limit context usage)
        
        Returns:
            {
                'status': 'OK' or 'error',
                'url': str,
                'markdown': str,  # Markdown content
                'title': str,     # Page title (if available)
                'length': int     # Character count
            }
        """
        try:
            logger.info(f"🔍 Fetching webpage: {url}")
            
            # Clean URL (remove https:// if present for Jina)
            clean_url = url.replace('https://', '').replace('http://', '')
            
            # Fetch via Jina AI Reader
            jina_url = f"{self.base_url}/{clean_url}"
            
            response = self.client.get(jina_url)
            response.raise_for_status()
            
            markdown_content = response.text
            
            # Extract title (first # heading if available)
            title = None
            lines = markdown_content.split('\n')
            for line in lines:
                if line.startswith('# '):
                    title = line[2:].strip()
                    break
            
            # Limit content if requested
            if max_chars and len(markdown_content) > max_chars:
                markdown_content = markdown_content[:max_chars] + f"\n\n... (truncated, original length: {len(response.text)} chars)"
                logger.info(f"   ⚠️ Content truncated to {max_chars} chars")
            
            logger.info(f"✅ Fetched {len(markdown_content)} characters")
            
            return {
                "status": "OK",
                "url": url,
                "markdown": markdown_content,
                "title": title or url,
                "length": len(markdown_content),
                "source": "Jina AI Reader (FREE!)"
            }
        
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error fetching {url}: {e.response.status_code}"
            logger.error(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "url": url
            }
        
        except Exception as e:
            error_msg = f"Failed to fetch webpage: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "url": url
            }
    
    def __del__(self):
        """Cleanup"""
        try:
            self.client.close()
        except:
            pass


# Singleton
_jina_reader: Optional[JinaReader] = None


def get_jina_reader() -> JinaReader:
    """Get or create Jina Reader singleton"""
    global _jina_reader
    if _jina_reader is None:
        _jina_reader = JinaReader()
    return _jina_reader


def fetch_webpage(url: str, max_chars: int = 10000, **kwargs) -> Dict[str, Any]:
    """
    Fetch webpage and convert to Markdown (FREE!).
    
    Args:
        url: URL to fetch
        max_chars: Max characters (default: 10000 to save context)
    
    Returns:
        Webpage as Markdown
    """
    reader = get_jina_reader()
    return reader.fetch(url, max_chars=max_chars)


if __name__ == "__main__":
    # Test
    print("\n🧪 Testing Jina AI Reader (FREE Webpage Fetcher)\n")
    
    # Test 1: Fetch Python.org
    print("1️⃣ Fetching: https://www.python.org")
    result = fetch_webpage("https://www.python.org", max_chars=500)
    
    print(f"Status: {result['status']}")
    if result.get('markdown'):
        print(f"Title: {result.get('title', 'N/A')}")
        print(f"Length: {result['length']} chars")
        print(f"\nPreview:")
        print(result['markdown'][:300] + "...\n")
    
    # Test 2: Fetch ArXiv paper page
    print("2️⃣ Fetching: https://arxiv.org/abs/1706.03762 (Attention Is All You Need)")
    result2 = fetch_webpage("https://arxiv.org/abs/1706.03762", max_chars=800)
    
    print(f"Status: {result2['status']}")
    if result2.get('markdown'):
        print(f"Title: {result2.get('title', 'N/A')}")
        print(f"Length: {result2['length']} chars")
        print(f"\nPreview:")
        print(result2['markdown'][:400] + "...")

