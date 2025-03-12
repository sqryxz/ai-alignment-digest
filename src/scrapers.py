import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, UTC
import logging
from typing import List, Dict, Optional
import json
import feedparser
from html2text import HTML2Text
from email.utils import parsedate_to_datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Post:
    def __init__(self, title: str, url: str, author: str, content: str, 
                 published_date: datetime, source: str):
        self.title = title
        self.url = url
        self.author = author
        self.content = content
        self.published_date = published_date
        self.source = source

    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'url': self.url,
            'author': self.author,
            'content': self.content,
            'published_date': self.published_date.isoformat(),
            'source': self.source
        }

class BaseScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'AI Alignment Digest Bot/1.0'
        }
        self.timeout = 30  # seconds
        self.html_converter = HTML2Text()
        self.html_converter.ignore_links = True
        self.html_converter.ignore_images = True
        self.html_converter.body_width = 0  # Don't wrap text

    def get_recent_posts(self, days: int = 1) -> List[Post]:
        raise NotImplementedError

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object."""
        try:
            # First try ISO format
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            try:
                # Then try RFC 2822 format (common in RSS feeds)
                return parsedate_to_datetime(date_str)
            except (TypeError, ValueError):
                logger.error(f"Failed to parse date: {date_str}")
                return datetime.now(UTC)

    def _clean_html(self, html: str) -> str:
        """Convert HTML to plain text while preserving important formatting."""
        return self.html_converter.handle(html).strip()

    def _get_content(self, entry: Dict) -> str:
        """Extract content from a feed entry."""
        # Try different possible content locations
        if 'content' in entry and entry.content:
            # Some feeds use content array
            if isinstance(entry.content, list):
                return entry.content[0].value
            # Some feeds use content directly
            return entry.content
        
        # Try summary or description
        if 'summary' in entry:
            return entry.summary
        if 'description' in entry:
            return entry.description
            
        # If no content found
        return ''

class AlignmentForumScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.alignmentforum.org"
        self.rss_url = f"{self.base_url}/feed.xml"

    def get_recent_posts(self, days: int = 1) -> List[Post]:
        cutoff_date = datetime.now(UTC) - timedelta(days=days)
        
        try:
            response = requests.get(self.rss_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            feed = feedparser.parse(response.text)
            posts = []
            
            for entry in feed.entries:
                try:
                    published_date = self._parse_date(entry.get('published', ''))
                    
                    if published_date >= cutoff_date:
                        content = self._get_content(entry)
                        post = Post(
                            title=entry.get('title', ''),
                            url=entry.get('link', ''),
                            author=entry.get('author', 'Unknown'),
                            content=self._clean_html(content),
                            published_date=published_date,
                            source='Alignment Forum'
                        )
                        posts.append(post)
                except Exception as e:
                    logger.error(f"Error processing AF post: {str(e)}")
                    continue
            
            return posts
            
        except Exception as e:
            logger.error(f"Error fetching Alignment Forum posts: {str(e)}")
            return []

class LessWrongScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.lesswrong.com"
        self.rss_url = f"{self.base_url}/feed.xml"

    def get_recent_posts(self, days: int = 1) -> List[Post]:
        cutoff_date = datetime.now(UTC) - timedelta(days=days)
        
        try:
            response = requests.get(self.rss_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            feed = feedparser.parse(response.text)
            posts = []
            
            for entry in feed.entries:
                try:
                    published_date = self._parse_date(entry.get('published', ''))
                    
                    if published_date >= cutoff_date:
                        content = self._get_content(entry)
                        post = Post(
                            title=entry.get('title', ''),
                            url=entry.get('link', ''),
                            author=entry.get('author', 'Unknown'),
                            content=self._clean_html(content),
                            published_date=published_date,
                            source='LessWrong'
                        )
                        posts.append(post)
                except Exception as e:
                    logger.error(f"Error processing LW post: {str(e)}")
                    continue
            
            return posts
            
        except Exception as e:
            logger.error(f"Error fetching LessWrong posts: {str(e)}")
            return [] 