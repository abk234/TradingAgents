"""
Web Crawler - Autonomous Researcher

Eddie v2.0's autonomous researcher that crawls the web to learn new market terms,
events, and information. Uses Crawl4AI for rendering and DuckDuckGo for search.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
import asyncio
import re

logger = logging.getLogger(__name__)


@dataclass
class CrawlResult:
    """Result of a web crawl operation."""
    url: str
    title: str
    content: str  # Extracted text content
    markdown: Optional[str] = None  # Markdown representation
    metadata: Dict[str, Any] = field(default_factory=dict)
    crawled_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content[:1000],  # Truncate for storage
            "markdown": self.markdown[:1000] if self.markdown else None,
            "metadata": self.metadata,
            "crawled_at": self.crawled_at.isoformat()
        }


@dataclass
class SearchResult:
    """Result from web search."""
    title: str
    url: str
    snippet: str
    rank: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "rank": self.rank
        }


class WebCrawler:
    """
    Web crawler for autonomous learning.
    
    Capabilities:
    - Search the web (DuckDuckGo)
    - Crawl and render pages (Crawl4AI)
    - Extract knowledge from web content
    - Store learned information
    """
    
    def __init__(self):
        """Initialize web crawler."""
        self._crawler = None
        self._initialized = False
    
    def _initialize_crawler(self):
        """Lazy initialization of Crawl4AI."""
        if self._initialized:
            return
        
        try:
            from crawl4ai import AsyncWebCrawler
            
            logger.info("Initializing Crawl4AI web crawler...")
            # Initialize crawler (will be created async)
            self._crawler_available = True
            self._initialized = True
            logger.info("Web crawler initialized")
            
        except ImportError:
            logger.warning("Crawl4AI not installed. Install with: pip install crawl4ai")
            self._crawler_available = False
            self._initialized = True
    
    async def search(
        self,
        query: str,
        max_results: int = 5
    ) -> List[SearchResult]:
        """
        Search the web using DuckDuckGo.
        
        Args:
            query: Search query
            max_results: Maximum number of results
        
        Returns:
            List of SearchResult objects
        """
        try:
            from duckduckgo_search import DDGS
            
            logger.info(f"Searching web for: {query}")
            
            results = []
            with DDGS() as ddgs:
                search_results = ddgs.text(query, max_results=max_results)
                
                for idx, result in enumerate(search_results, 1):
                    search_result = SearchResult(
                        title=result.get('title', ''),
                        url=result.get('href', ''),
                        snippet=result.get('body', ''),
                        rank=idx
                    )
                    results.append(search_result)
            
            logger.info(f"Found {len(results)} search results")
            return results
            
        except ImportError:
            logger.error("duckduckgo-search not installed. Install with: pip install duckduckgo-search")
            return []
        except Exception as e:
            logger.error(f"Error searching web: {e}")
            return []
    
    async def crawl_page(
        self,
        url: str,
        extract_markdown: bool = True,
        wait_for: Optional[str] = None
    ) -> Optional[CrawlResult]:
        """
        Crawl a single web page and extract content.
        
        Args:
            url: URL to crawl
            extract_markdown: If True, extract markdown representation
            wait_for: CSS selector or text to wait for (for JS-rendered content)
        
        Returns:
            CrawlResult or None if failed
        """
        if not self._initialized:
            self._initialize_crawler()
        
        if not self._crawler_available:
            logger.warning("Crawl4AI not available, cannot crawl pages")
            return None
        
        try:
            from crawl4ai import AsyncWebCrawler
            
            logger.info(f"Crawling page: {url}")
            
            async with AsyncWebCrawler(verbose=False) as crawler:
                # Crawl the page
                result = await crawler.arun(
                    url=url,
                    word_count_threshold=10,
                    extraction_strategy="cosine",
                    wait_for=wait_for
                )
                
                if result.success:
                    crawl_result = CrawlResult(
                        url=url,
                        title=result.metadata.get('title', '') if result.metadata else '',
                        content=result.cleaned_html or result.html or '',
                        markdown=result.markdown if extract_markdown else None,
                        metadata={
                            "status_code": result.status_code,
                            "links": len(result.links) if result.links else 0,
                            "images": len(result.media) if result.media else 0
                        }
                    )
                    
                    logger.info(f"Successfully crawled: {url} ({len(crawl_result.content)} chars)")
                    return crawl_result
                else:
                    logger.warning(f"Failed to crawl {url}: {result.error_message}")
                    return None
                    
        except ImportError:
            logger.error("Crawl4AI not installed")
            return None
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            return None
    
    async def search_and_crawl(
        self,
        query: str,
        max_results: int = 3,
        crawl_top_n: int = 3
    ) -> Tuple[List[SearchResult], List[CrawlResult]]:
        """
        Search the web and crawl top results.
        
        Args:
            query: Search query
            max_results: Maximum search results
            crawl_top_n: Number of top results to crawl
        
        Returns:
            Tuple of (search_results, crawl_results)
        """
        # Search
        search_results = await self.search(query, max_results=max_results)
        
        # Crawl top results
        crawl_results = []
        for result in search_results[:crawl_top_n]:
            crawl_result = await self.crawl_page(result.url)
            if crawl_result:
                crawl_results.append(crawl_result)
        
        return search_results, crawl_results
    
    def extract_knowledge(
        self,
        crawl_results: List[CrawlResult],
        topic: str
    ) -> Dict[str, Any]:
        """
        Extract knowledge from crawled content.
        
        Simple extraction for now. Could be enhanced with LLM-based extraction.
        
        Args:
            crawl_results: List of crawl results
            topic: Topic being researched
        
        Returns:
            Extracted knowledge dictionary
        """
        knowledge = {
            "topic": topic,
            "sources": [],
            "summary": "",
            "key_points": [],
            "extracted_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Combine content from all results
        all_content = []
        for result in crawl_results:
            knowledge["sources"].append({
                "url": result.url,
                "title": result.title
            })
            
            # Extract text content (first 500 chars)
            content = result.content[:500] if result.content else ""
            if content:
                all_content.append(content)
        
        # Simple extraction: combine content
        knowledge["summary"] = "\n\n".join(all_content[:3])  # First 3 sources
        
        # Extract key points (simple: look for bullet points or numbered lists)
        for result in crawl_results:
            if result.markdown:
                # Look for bullet points or numbered lists
                lines = result.markdown.split('\n')
                for line in lines:
                    if re.match(r'^[-*•]\s+', line) or re.match(r'^\d+\.\s+', line):
                        point = re.sub(r'^[-*•\d.]\s+', '', line).strip()
                        if point and len(point) > 20:  # Meaningful point
                            knowledge["key_points"].append(point)
                            if len(knowledge["key_points"]) >= 5:
                                break
        
        return knowledge


class AutonomousResearcher:
    """
    Autonomous researcher that learns from the web.
    
    Triggers:
    - Unknown terms mentioned by user
    - Market crash events
    - User requests for information not in knowledge base
    """
    
    def __init__(self):
        """Initialize autonomous researcher."""
        self.crawler = WebCrawler()
        self.learned_knowledge: Dict[str, Dict[str, Any]] = {}  # topic -> knowledge
    
    async def learn_about(
        self,
        topic: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Learn about a topic by searching and crawling the web.
        
        Args:
            topic: Topic to learn about (e.g., "0DTE options", "Death Cross")
            context: Additional context (e.g., "user mentioned this term")
        
        Returns:
            Learned knowledge dictionary
        """
        logger.info(f"Learning about: {topic}")
        
        # Search and crawl
        search_results, crawl_results = await self.crawler.search_and_crawl(
            query=topic,
            max_results=5,
            crawl_top_n=3
        )
        
        if not crawl_results:
            return {
                "topic": topic,
                "learned": False,
                "error": "No crawl results"
            }
        
        # Extract knowledge
        knowledge = self.crawler.extract_knowledge(crawl_results, topic)
        
        # Store learned knowledge
        self.learned_knowledge[topic.lower()] = knowledge
        
        logger.info(f"Learned about {topic}: {len(knowledge.get('key_points', []))} key points")
        
        return {
            "topic": topic,
            "learned": True,
            "knowledge": knowledge,
            "sources": len(crawl_results)
        }
    
    def get_learned_knowledge(self, topic: str) -> Optional[Dict[str, Any]]:
        """Get previously learned knowledge about a topic."""
        return self.learned_knowledge.get(topic.lower())
    
    def has_learned(self, topic: str) -> bool:
        """Check if we've learned about a topic."""
        return topic.lower() in self.learned_knowledge


# Global instance
_autonomous_researcher: Optional[AutonomousResearcher] = None


def get_autonomous_researcher() -> AutonomousResearcher:
    """Get the global autonomous researcher instance."""
    global _autonomous_researcher
    if _autonomous_researcher is None:
        _autonomous_researcher = AutonomousResearcher()
    return _autonomous_researcher

