#!/usr/bin/env python3
"""
ArXiv Research Tool - Academic Paper Search 📚

Access to 2+ million scientific papers - completely FREE!
Perfect for:
- AI/ML research
- Academic literature reviews
- Technical deep-dives
- Staying current with latest research

API: https://arxiv.org
Docs: https://info.arxiv.org/help/api/index.html
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    import arxiv
    ARXIV_AVAILABLE = True
except ImportError:
    ARXIV_AVAILABLE = False
    print("⚠️ arxiv library not installed. Run: pip install arxiv")

logger = logging.getLogger(__name__)


class ArXivSearch:
    """
    ArXiv Research Tool - Search 2M+ scientific papers.
    
    Completely FREE! No API key needed! 🎉
    """
    
    def __init__(self):
        """Initialize ArXiv search"""
        if not ARXIV_AVAILABLE:
            logger.warning("⚠️ ArXiv library not available")
        else:
            logger.info("✅ ArXiv Search initialized (2M+ papers available)")
    
    def search(
        self,
        query: str,
        max_results: int = 10,
        sort_by: str = "relevance",  # "relevance", "lastUpdatedDate", "submittedDate"
        sort_order: str = "descending"  # "ascending" or "descending"
    ) -> Dict[str, Any]:
        """
        Search ArXiv for academic papers.
        
        Args:
            query: Search query (keywords, authors, titles)
            max_results: Max papers to return (default: 10)
            sort_by: Sort criteria ("relevance", "lastUpdatedDate", "submittedDate")
            sort_order: "ascending" or "descending"
        
        Returns:
            {
                'status': 'OK' or 'error',
                'query': str,
                'results': [
                    {
                        'title': str,
                        'authors': List[str],
                        'summary': str,  # Abstract
                        'published': str,  # Date
                        'updated': str,  # Last update date
                        'pdf_url': str,
                        'arxiv_url': str,
                        'arxiv_id': str,
                        'categories': List[str],  # E.g., ['cs.AI', 'cs.LG']
                        'comment': str  # Paper comments (e.g., "Published in NeurIPS 2024")
                    },
                    ...
                ],
                'total_results': int
            }
        """
        if not ARXIV_AVAILABLE:
            return {
                "status": "error",
                "message": "ArXiv library not installed. Run: pip install arxiv",
                "query": query
            }
        
        try:
            logger.info(f"📚 ArXiv Search: '{query}' (max={max_results}, sort={sort_by})")
            
            # Map sort_by to arxiv.SortCriterion
            sort_criterion = {
                "relevance": arxiv.SortCriterion.Relevance,
                "lastUpdatedDate": arxiv.SortCriterion.LastUpdatedDate,
                "submittedDate": arxiv.SortCriterion.SubmittedDate
            }.get(sort_by, arxiv.SortCriterion.Relevance)
            
            # Map sort_order to arxiv.SortOrder
            sort_order_enum = {
                "ascending": arxiv.SortOrder.Ascending,
                "descending": arxiv.SortOrder.Descending
            }.get(sort_order, arxiv.SortOrder.Descending)
            
            # Create search client
            client = arxiv.Client()
            
            # Perform search
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=sort_criterion,
                sort_order=sort_order_enum
            )
            
            # Collect results
            results = []
            for paper in client.results(search):
                results.append({
                    'title': paper.title,
                    'authors': [author.name for author in paper.authors],
                    'summary': paper.summary,
                    'published': paper.published.strftime('%Y-%m-%d'),
                    'updated': paper.updated.strftime('%Y-%m-%d'),
                    'pdf_url': paper.pdf_url,
                    'arxiv_url': paper.entry_id,
                    'arxiv_id': paper.get_short_id(),
                    'categories': paper.categories,
                    'comment': paper.comment if paper.comment else None,
                    'source': 'arxiv'
                })
            
            logger.info(f"✅ Found {len(results)} ArXiv papers")
            
            return {
                "status": "OK",
                "query": query,
                "results": results,
                "total_results": len(results),
                "source": "ArXiv (Free Academic Papers)"
            }
        
        except Exception as e:
            error_msg = f"ArXiv search failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "query": query
            }
    
    def search_by_category(
        self,
        category: str,
        max_results: int = 10,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search ArXiv by category.
        
        Common categories:
        - cs.AI: Artificial Intelligence
        - cs.LG: Machine Learning
        - cs.CL: Computation and Language (NLP)
        - cs.CV: Computer Vision
        - stat.ML: Machine Learning (Statistics)
        - q-bio: Quantitative Biology
        
        Full list: https://arxiv.org/category_taxonomy
        
        Args:
            category: ArXiv category code (e.g., "cs.AI")
            max_results: Max papers
            query: Optional additional query terms
        
        Returns:
            Search results
        """
        # Build query with category filter
        if query:
            full_query = f"cat:{category} AND {query}"
        else:
            full_query = f"cat:{category}"
        
        logger.info(f"📂 ArXiv Category Search: {category} (query='{query}')")
        
        return self.search(
            query=full_query,
            max_results=max_results,
            sort_by="submittedDate"  # Most recent first
        )
    
    def search_by_author(
        self,
        author: str,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Search ArXiv by author name.
        
        Args:
            author: Author name (e.g., "Andrej Karpathy")
            max_results: Max papers
        
        Returns:
            Search results
        """
        # Build author query
        query = f"au:{author}"
        
        logger.info(f"👤 ArXiv Author Search: {author}")
        
        return self.search(
            query=query,
            max_results=max_results,
            sort_by="submittedDate"
        )
    
    def get_paper_by_id(
        self,
        arxiv_id: str
    ) -> Dict[str, Any]:
        """
        Get specific paper by ArXiv ID.
        
        Args:
            arxiv_id: ArXiv ID (e.g., "2103.14030" or "arXiv:2103.14030")
        
        Returns:
            Paper details
        """
        if not ARXIV_AVAILABLE:
            return {
                "status": "error",
                "message": "ArXiv library not installed"
            }
        
        try:
            # Clean ID (remove "arXiv:" prefix if present)
            clean_id = arxiv_id.replace("arXiv:", "").replace("arxiv:", "")
            
            logger.info(f"📄 Getting ArXiv paper: {clean_id}")
            
            # Create search by ID
            search = arxiv.Search(id_list=[clean_id])
            client = arxiv.Client()
            
            # Get paper
            paper = next(client.results(search))
            
            result = {
                'title': paper.title,
                'authors': [author.name for author in paper.authors],
                'summary': paper.summary,
                'published': paper.published.strftime('%Y-%m-%d'),
                'updated': paper.updated.strftime('%Y-%m-%d'),
                'pdf_url': paper.pdf_url,
                'arxiv_url': paper.entry_id,
                'arxiv_id': paper.get_short_id(),
                'categories': paper.categories,
                'comment': paper.comment if paper.comment else None,
                'source': 'arxiv'
            }
            
            logger.info(f"✅ Found paper: {result['title'][:50]}...")
            
            return {
                "status": "OK",
                "paper": result
            }
        
        except StopIteration:
            return {
                "status": "not_found",
                "message": f"No paper found with ID: {arxiv_id}"
            }
        except Exception as e:
            error_msg = f"Failed to get ArXiv paper: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg
            }


# Singleton
_arxiv_search: Optional[ArXivSearch] = None


def get_arxiv_search() -> ArXivSearch:
    """Get or create ArXiv search singleton"""
    global _arxiv_search
    if _arxiv_search is None:
        _arxiv_search = ArXivSearch()
    return _arxiv_search


def arxiv_search(query: str, max_results: int = 10, **kwargs) -> Dict[str, Any]:
    """
    Search ArXiv for academic papers (FREE!).
    
    Args:
        query: Search query
        max_results: Max results
    
    Returns:
        ArXiv search results
    """
    searcher = get_arxiv_search()
    return searcher.search(query, max_results=max_results, **kwargs)


if __name__ == "__main__":
    # Test
    print("\n🧪 Testing ArXiv Search\n")
    
    searcher = ArXivSearch()
    
    # Test 1: General search
    print("1️⃣ Search: 'large language models'")
    result = searcher.search("large language models", max_results=3)
    print(f"Status: {result['status']}")
    print(f"Results: {len(result.get('results', []))}\n")
    
    if result.get('results'):
        for i, paper in enumerate(result['results'], 1):
            print(f"{i}. {paper['title'][:70]}...")
            print(f"   Authors: {', '.join(paper['authors'][:3])}")
            print(f"   Published: {paper['published']}")
            print(f"   Categories: {', '.join(paper['categories'][:3])}")
            print(f"   PDF: {paper['pdf_url']}")
            print()
    
    # Test 2: Category search
    print("2️⃣ Category Search: cs.AI (Artificial Intelligence)")
    cat_result = searcher.search_by_category("cs.AI", max_results=2)
    print(f"Status: {cat_result['status']}")
    print(f"Results: {len(cat_result.get('results', []))}\n")
    
    if cat_result.get('results'):
        paper = cat_result['results'][0]
        print(f"Latest AI paper: {paper['title'][:70]}...")
        print(f"Published: {paper['published']}\n")
    
    # Test 3: Author search
    print("3️⃣ Author Search: 'Yann LeCun'")
    author_result = searcher.search_by_author("Yann LeCun", max_results=2)
    print(f"Status: {author_result['status']}")
    print(f"Results: {len(author_result.get('results', []))}")

