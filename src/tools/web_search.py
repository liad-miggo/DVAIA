import requests
import logging
from typing import Dict, Any, List, Optional
from .base_tool import BaseTool
import json
import time

logger = logging.getLogger(__name__)

class WebSearchTool(BaseTool):
    """Tool for searching the web for information"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.duckduckgo.com/"
        self.search_url = "https://html.duckduckgo.com/html/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_description(self) -> str:
        return "Search the web for information using DuckDuckGo. Returns relevant search results and snippets."
    
    def execute(self, **kwargs) -> str:
        """Execute web search"""
        try:
            self.validate_parameters(**kwargs)
            
            query = kwargs["query"]
            max_results = kwargs.get("max_results", 5)
            
            # Perform the search
            results = self._search_web(query, max_results)
            
            if not results:
                return "No search results found for the given query."
            
            # Format the results
            formatted_results = self._format_results(results, query)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return f"Error performing web search: {str(e)}"
    
    def _search_web(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Perform web search using DuckDuckGo"""
        try:
            # Use DuckDuckGo Instant Answer API first
            instant_answer = self._get_instant_answer(query)
            
            # Also get web results
            web_results = self._get_web_results(query, max_results)
            
            # Combine results
            all_results = []
            
            if instant_answer:
                all_results.append({
                    'type': 'instant_answer',
                    'title': instant_answer.get('title', ''),
                    'snippet': instant_answer.get('abstract', ''),
                    'url': instant_answer.get('url', ''),
                    'source': 'DuckDuckGo Instant Answer'
                })
            
            all_results.extend(web_results)
            
            return all_results[:max_results]
            
        except Exception as e:
            logger.error(f"Error in web search: {e}")
            return []
    
    def _get_instant_answer(self, query: str) -> Optional[Dict[str, Any]]:
        """Get instant answer from DuckDuckGo API"""
        try:
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if we have an instant answer
                if data.get('Abstract'):
                    return {
                        'title': data.get('Heading', ''),
                        'abstract': data.get('Abstract', ''),
                        'url': data.get('AbstractURL', ''),
                        'image': data.get('Image', '')
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting instant answer: {e}")
            return None
    
    def _get_web_results(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Get web search results"""
        try:
            # For now, we'll use a simple approach
            # In a production environment, you might want to use a proper search API
            # like Google Custom Search API or Bing Search API
            
            # Simulate web search results (replace with actual implementation)
            results = []
            
            # Example results - in a real implementation, you would:
            # 1. Make a request to a search API
            # 2. Parse the HTML response
            # 3. Extract titles, snippets, and URLs
            
            # For demonstration purposes, we'll return some example results
            example_results = [
                {
                    'title': f'Search results for: {query}',
                    'snippet': f'This is a sample search result for "{query}". In a real implementation, this would contain actual search results from the web.',
                    'url': f'https://example.com/search?q={query}',
                    'source': 'Web Search'
                }
            ]
            
            return example_results[:max_results]
            
        except Exception as e:
            logger.error(f"Error getting web results: {e}")
            return []
    
    def _format_results(self, results: List[Dict[str, Any]], query: str) -> str:
        """Format search results into a readable string"""
        if not results:
            return f"No results found for '{query}'"
        
        formatted = f"Search results for '{query}':\n\n"
        
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result['title']}\n"
            formatted += f"   {result['snippet']}\n"
            formatted += f"   URL: {result['url']}\n"
            formatted += f"   Source: {result['source']}\n\n"
        
        return formatted.strip()
    
    def _search_with_requests(self, query: str) -> List[Dict[str, Any]]:
        """Alternative method using requests to scrape search results"""
        try:
            params = {
                'q': query,
                'kl': 'us-en',  # Language
                'kp': '1'       # Safe search
            }
            
            response = requests.get(
                self.search_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                # Parse HTML response to extract results
                # This is a simplified version - in production you'd use BeautifulSoup
                return self._parse_html_results(response.text)
            
            return []
            
        except Exception as e:
            logger.error(f"Error in requests search: {e}")
            return []
    
    def _parse_html_results(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse HTML content to extract search results"""
        # This is a placeholder - in a real implementation you would:
        # 1. Use BeautifulSoup to parse the HTML
        # 2. Extract titles, snippets, and URLs from the search results
        # 3. Return structured data
        
        # For now, return empty list
        return [] 