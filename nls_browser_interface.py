#!/usr/bin/env python3
"""
NLS Browser API Text-Browser Interface
Provides text-based web browsing capabilities for the BitChat multimedia system
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import json
from typing import Dict, List, Optional
import time

class NLSBrowser:
    """NLS Browser API for text-based web interaction"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NLS Browser API / Cursor Agents IDE'
        })
        self.history = []
        self.bookmarks = {}

    def browse_url(self, url: str, render_js: bool = False) -> Dict:
        """
        Browse a URL and return text-based representation
        """
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            response = self.session.get(url, timeout=10)

            if response.status_code != 200:
                return {
                    'error': f'HTTP {response.status_code}',
                    'url': url
                }

            # Add to history
            self.history.append({
                'url': url,
                'timestamp': time.time(),
                'title': self._extract_title(response.text)
            })

            # Extract text content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text content
            text_content = soup.get_text()

            # Clean up whitespace
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            clean_text = '\n'.join(lines[:100])  # Limit to first 100 lines

            # Extract links
            links = []
            for a in soup.find_all('a', href=True):
                href = urljoin(url, a['href'])
                text = a.get_text().strip()
                if text and href.startswith(('http://', 'https://')):
                    links.append({
                        'text': text[:50],  # Limit text length
                        'url': href
                    })

            return {
                'url': url,
                'title': self._extract_title(response.text),
                'content': clean_text,
                'links': links[:20],  # Limit to 20 links
                'status': 'success'
            }

        except Exception as e:
            return {
                'error': str(e),
                'url': url,
                'status': 'error'
            }

    def search_web(self, query: str) -> Dict:
        """
        Perform a web search and return results
        """
        try:
            # Use a simple search approach (in production, use actual search API)
            search_url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"

            result = self.browse_url(search_url)

            if result.get('status') == 'success':
                # Extract search results from DuckDuckGo HTML
                soup = BeautifulSoup(self.session.get(search_url).text, 'html.parser')
                results = []

                for result_div in soup.find_all('div', class_='result')[:5]:
                    title_elem = result_div.find('a', class_='result__a')
                    snippet_elem = result_div.find('a', class_='result__snippet')

                    if title_elem and snippet_elem:
                        results.append({
                            'title': title_elem.get_text().strip(),
                            'url': title_elem['href'],
                            'snippet': snippet_elem.get_text().strip()
                        })

                return {
                    'query': query,
                    'results': results,
                    'status': 'success'
                }
            else:
                return result

        except Exception as e:
            return {
                'error': str(e),
                'query': query,
                'status': 'error'
            }

    def add_bookmark(self, name: str, url: str):
        """Add a URL to bookmarks"""
        self.bookmarks[name] = url
        return f"Bookmark '{name}' added: {url}"

    def get_bookmarks(self) -> Dict:
        """Get all bookmarks"""
        return self.bookmarks.copy()

    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get browsing history"""
        return self.history[-limit:]

    def _extract_title(self, html: str) -> str:
        """Extract page title from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.find('title')
            return title.get_text().strip() if title else "Untitled"
        except:
            return "Untitled"

class NLSBrowserAPI:
    """API wrapper for NLS Browser integration with BitChat"""

    def __init__(self):
        self.browser = NLSBrowser()

    def process_command(self, command: str, context: str = "") -> Dict:
        """
        Process NLS browser commands for chat integration
        """
        parts = command.split()
        if not parts:
            return {'error': 'No command provided'}

        cmd = parts[0].lower()

        if cmd == 'browse' and len(parts) > 1:
            url = parts[1]
            return self.browser.browse_url(url)

        elif cmd == 'search' and len(parts) > 1:
            query = ' '.join(parts[1:])
            return self.browser.search_web(query)

        elif cmd == 'bookmark' and len(parts) > 2:
            name = parts[1]
            url = parts[2]
            return {'result': self.browser.add_bookmark(name, url)}

        elif cmd == 'bookmarks':
            return {'bookmarks': self.browser.get_bookmarks()}

        elif cmd == 'history':
            limit = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 10
            return {'history': self.browser.get_history(limit)}

        else:
            return {
                'help': {
                    'browse <url>': 'Browse a webpage',
                    'search <query>': 'Search the web',
                    'bookmark <name> <url>': 'Add bookmark',
                    'bookmarks': 'List bookmarks',
                    'history [limit]': 'Show browsing history'
                }
            }

# Global NLS Browser instance
nls_browser = NLSBrowserAPI()

def nls_browser_request(command: str, context: str = "") -> Optional[Dict]:
    """
    Main entry point for NLS browser requests
    """
    return nls_browser.process_command(command, context)

if __name__ == "__main__":
    # Test the NLS browser
    browser = NLSBrowserAPI()

    # Test browsing
    result = browser.process_command("browse example.com")
    print("Browse result:", json.dumps(result, indent=2))

    # Test search
    result = browser.process_command("search python programming")
    print("Search result:", json.dumps(result, indent=2))
