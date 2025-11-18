#!/usr/bin/env python3
"""
Deep Research Tool - Multi-Step Autonomous Research

Inspired by GPT Researcher pattern:
1. Query Decomposition - Break complex questions into sub-questions
2. Parallel Search - Search multiple sources simultaneously  
3. Content Analysis - Extract key information
4. Synthesis - Combine findings into comprehensive report

Perfect for: Market research, technical deep-dives, competitive analysis
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from tools.free_web_search import get_free_search
    FREE_WEB_AVAILABLE = True
except ImportError:
    FREE_WEB_AVAILABLE = False

try:
    from tools.arxiv_search import get_arxiv_search
    ARXIV_AVAILABLE = True
except ImportError:
    ARXIV_AVAILABLE = False

logger = logging.getLogger(__name__)


class DeepResearch:
    """
    Deep Research Tool - Autonomous multi-step research.
    
    Process:
    1. Analyze query → generate sub-questions
    2. Search each sub-question
    3. Extract key information
    4. Synthesize final report
    """
    
    def __init__(self, web_search_func=None, llm_func=None, use_free_tools=True):
        """
        Initialize deep research tool.
        
        Args:
            web_search_func: Function for web search (optional, uses free tools if None)
            llm_func: Function for LLM calls (for analysis/synthesis)
            use_free_tools: Use free DuckDuckGo + Wikipedia + ArXiv (default: True)
        """
        # Use free tools if available and no custom web_search provided
        if use_free_tools and not web_search_func:
            if FREE_WEB_AVAILABLE:
                self.free_search = get_free_search()
                # Wrap free_search.search to match expected interface
                self.web_search = lambda query, max_results=10, **kwargs: self.free_search.search(query, max_results)
                logger.info("✅ Using FREE web search (DuckDuckGo)")
            else:
                logger.warning("⚠️ Free web search not available")
                self.web_search = web_search_func
                self.free_search = None
            
            if ARXIV_AVAILABLE:
                self.arxiv_search = get_arxiv_search()
                logger.info("✅ ArXiv search enabled")
            else:
                self.arxiv_search = None
        else:
            self.web_search = web_search_func
            self.free_search = None
            self.arxiv_search = None
        
        self.llm = llm_func
        logger.info("✅ Deep Research Tool initialized")
    
    def research(
        self,
        query: str,
        depth: int = 2,  # How many sub-questions per query
        max_sources: int = 10,  # Max sources to gather
        report_format: str = "markdown",  # "markdown" or "json"
        include_academic: bool = True  # Include ArXiv papers (FREE!)
    ) -> Dict[str, Any]:
        """
        Perform deep research on a topic.
        
        Args:
            query: Research question
            depth: How many sub-questions to generate (1-5)
            max_sources: Max sources to gather per sub-question
            report_format: "markdown" or "json"
        
        Returns:
            {
                'query': str,
                'sub_questions': List[str],
                'sources': List[Dict],  # All sources gathered
                'findings': Dict,  # Key findings per sub-question
                'report': str,  # Final synthesized report
                'research_time': float
            }
        """
        start_time = datetime.utcnow()
        
        logger.info(f"🔬 Starting deep research: '{query}'")
        logger.info(f"   Depth: {depth} sub-questions, Max sources: {max_sources}")
        
        try:
            # Step 1: Generate sub-questions
            sub_questions = self._generate_sub_questions(query, depth)
            logger.info(f"📋 Generated {len(sub_questions)} sub-questions")
            
            # Step 2: Search each sub-question
            all_sources = []
            findings = {}
            
            for i, sub_q in enumerate(sub_questions, 1):
                logger.info(f"🔍 Researching sub-question {i}/{len(sub_questions)}: {sub_q}")
                
                # Search for this sub-question
                search_results = self._search_sub_question(sub_q, max_results=max_sources)
                
                if search_results.get('status') == 'OK':
                    sources = search_results.get('results', [])
                    all_sources.extend(sources)
                    
                    # Extract key findings
                    key_info = self._extract_key_information(sub_q, sources)
                    findings[sub_q] = key_info
                    
                    logger.info(f"   ✅ Found {len(sources)} sources, extracted key info")
                else:
                    logger.warning(f"   ⚠️ Search failed for: {sub_q}")
                    findings[sub_q] = {
                        "error": search_results.get('message', 'Search failed')
                    }
            
            # Step 3: BONUS - ArXiv Academic Papers (if enabled)
            academic_sources = []
            if include_academic and self.arxiv_search:
                logger.info(f"📄 Searching ArXiv for academic papers...")
                try:
                    arxiv_result = self.arxiv_search.search(query, max_results=5)
                    if arxiv_result.get('status') == 'OK':
                        academic_sources = arxiv_result.get('results', [])
                        logger.info(f"   ✅ Found {len(academic_sources)} ArXiv papers")
                except Exception as e:
                    logger.warning(f"   ⚠️ ArXiv search failed: {e}")
            
            # Step 4: Synthesize final report
            logger.info(f"📝 Synthesizing final report from {len(all_sources)} sources + {len(academic_sources)} papers...")
            report = self._synthesize_report(
                query=query,
                sub_questions=sub_questions,
                findings=findings,
                sources=all_sources,
                academic_sources=academic_sources,
                format=report_format
            )
            
            research_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"✅ Deep research complete in {research_time:.1f}s")
            
            return {
                "status": "OK",
                "query": query,
                "sub_questions": sub_questions,
                "sources": all_sources,
                "academic_sources": academic_sources,
                "findings": findings,
                "report": report,
                "research_time": research_time,
                "total_sources": len(all_sources) + len(academic_sources)
            }
        
        except Exception as e:
            error_msg = f"Deep research failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "query": query
            }
    
    def _generate_sub_questions(self, query: str, depth: int) -> List[str]:
        """
        Generate sub-questions for deep research.
        
        Uses heuristics if no LLM available, otherwise uses LLM.
        """
        # If LLM available, use it to generate sub-questions
        if self.llm:
            try:
                prompt = f"""Break down this research question into {depth} specific sub-questions that would help answer it comprehensively:

Research Question: {query}

Generate {depth} focused sub-questions (one per line):"""
                
                response = self.llm(prompt)
                sub_questions = [q.strip() for q in response.split('\n') if q.strip() and '?' in q]
                
                if len(sub_questions) >= depth:
                    return sub_questions[:depth]
            
            except Exception as e:
                logger.warning(f"LLM sub-question generation failed: {e}, using heuristics")
        
        # Fallback: Use heuristic sub-question templates
        templates = [
            f"What is {query}?",
            f"Why is {query} important?",
            f"How does {query} work?",
            f"What are the best practices for {query}?",
            f"What are the latest developments in {query}?",
            f"What are the challenges with {query}?",
            f"What are alternatives to {query}?",
            f"What is the future of {query}?"
        ]
        
        return templates[:depth]
    
    def _search_sub_question(self, sub_question: str, max_results: int) -> Dict[str, Any]:
        """Search for a sub-question"""
        if not self.web_search:
            return {
                "status": "error",
                "message": "Web search not available"
            }
        
        try:
            return self.web_search(
                query=sub_question,
                max_results=max_results,
                include_answer=True
            )
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _extract_key_information(self, sub_question: str, sources: List[Dict]) -> Dict[str, Any]:
        """Extract key information from sources"""
        # Simple extraction: collect all content
        key_points = []
        urls = []
        
        for source in sources[:5]:  # Top 5 sources
            content = source.get('content', '')
            if content:
                key_points.append(content[:500])  # First 500 chars
            
            url = source.get('url')
            if url:
                urls.append(url)
        
        return {
            "sub_question": sub_question,
            "key_points": key_points,
            "source_urls": urls,
            "num_sources": len(sources)
        }
    
    def _synthesize_report(
        self,
        query: str,
        sub_questions: List[str],
        findings: Dict[str, Any],
        sources: List[Dict],
        academic_sources: List[Dict] = None,
        format: str = "markdown"
    ) -> str:
        """Synthesize final research report"""
        
        academic_sources = academic_sources or []
        total_sources = len(sources) + len(academic_sources)
        
        if format == "json":
            # Return structured JSON
            import json
            return json.dumps({
                "research_question": query,
                "sub_questions": sub_questions,
                "findings": findings,
                "total_sources": total_sources,
                "web_sources": len(sources),
                "academic_sources": len(academic_sources)
            }, indent=2)
        
        # Markdown report
        report = f"""# Deep Research Report: {query}

**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}  
**Total Sources:** {total_sources} ({len(sources)} web + {len(academic_sources)} academic)  
**Sub-Questions Explored:** {len(sub_questions)}

---

## Research Findings

"""
        
        for i, sub_q in enumerate(sub_questions, 1):
            report += f"### {i}. {sub_q}\n\n"
            
            finding = findings.get(sub_q, {})
            
            if 'error' in finding:
                report += f"⚠️ *Research incomplete: {finding['error']}*\n\n"
                continue
            
            key_points = finding.get('key_points', [])
            source_urls = finding.get('source_urls', [])
            
            if key_points:
                report += "**Key Findings:**\n\n"
                for j, point in enumerate(key_points[:3], 1):  # Top 3 points
                    report += f"{j}. {point[:200]}...\n\n"
            
            if source_urls:
                report += "**Sources:**\n"
                for url in source_urls[:3]:  # Top 3 URLs
                    report += f"- {url}\n"
            
            report += "\n"
        
        # Add Academic Papers section (if any)
        if academic_sources:
            report += "## 📄 Academic Research (ArXiv)\n\n"
            for i, paper in enumerate(academic_sources[:5], 1):  # Top 5 papers
                report += f"### {i}. {paper['title']}\n\n"
                report += f"**Authors:** {', '.join(paper['authors'][:3])}"
                if len(paper['authors']) > 3:
                    report += " et al."
                report += f"\n**Published:** {paper['published']}\n"
                report += f"**Categories:** {', '.join(paper['categories'][:3])}\n\n"
                report += f"{paper['summary'][:300]}...\n\n"
                report += f"🔗 [View on ArXiv]({paper['arxiv_url']})\n\n"
        
        report += f"""---

## Summary

This research explored {len(sub_questions)} key aspects of "{query}" using {total_sources} sources ({len(sources)} web sources + {len(academic_sources)} academic papers).

**Next Steps:**
- Review the findings above for detailed insights
- Click source links for full context
- Check ArXiv papers for academic depth
- Use findings to inform your decision-making

---

*Research powered by Substrate Deep Research Tool (FREE - DuckDuckGo + Wikipedia + ArXiv)*
"""
        
        return report


# Global instance
_deep_research: Optional[DeepResearch] = None


def init_deep_research(web_search_func=None, llm_func=None) -> DeepResearch:
    """Initialize global deep research instance"""
    global _deep_research
    _deep_research = DeepResearch(web_search_func=web_search_func, llm_func=llm_func)
    return _deep_research


def get_deep_research() -> Optional[DeepResearch]:
    """Get global deep research instance"""
    return _deep_research


if __name__ == "__main__":
    # Test (without real web search)
    print("\n🧪 Testing Deep Research Tool\n")
    
    # Mock web search
    def mock_search(query, max_results=5, **kwargs):
        return {
            "status": "OK",
            "results": [
                {
                    "title": f"Result for: {query}",
                    "url": "https://example.com",
                    "content": f"This is mock content about {query}. In a real implementation, this would be actual search results.",
                    "score": 0.95
                }
            ]
        }
    
    researcher = DeepResearch(web_search_func=mock_search)
    
    result = researcher.research(
        query="How to build AI agents with LLMs in 2025?",
        depth=3,
        max_sources=5
    )
    
    print(f"Status: {result['status']}")
    print(f"\n📋 Sub-questions: {len(result['sub_questions'])}")
    for i, q in enumerate(result['sub_questions'], 1):
        print(f"   {i}. {q}")
    
    print(f"\n📊 Total sources: {result['total_sources']}")
    print(f"⏱️  Research time: {result['research_time']:.1f}s")
    
    print(f"\n📝 Report Preview:\n")
    print(result['report'][:500] + "...\n")

