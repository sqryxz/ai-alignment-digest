import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional
import json

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

    def get_recent_posts(self, days: int = 1) -> List[Post]:
        raise NotImplementedError

class AlignmentForumScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.alignmentforum.org"
        self.graphql_url = f"{self.base_url}/graphql"

    def get_recent_posts(self, days: int = 1) -> List[Post]:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # GraphQL query for recent posts
        query = """
        {
            posts(input: {
                limit: 50,
                sortedBy: "new"
            }) {
                results {
                    _id
                    title
                    url
                    htmlBody
                    postedAt
                    user {
                        displayName
                    }
                }
            }
        }
        """
        
        try:
            response = requests.post(
                self.graphql_url,
                json={'query': query},
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            posts = []
            for post_data in data['data']['posts']['results']:
                post_date = datetime.fromisoformat(post_data['postedAt'].replace('Z', '+00:00'))
                if post_date >= cutoff_date:
                    post = Post(
                        title=post_data['title'],
                        url=f"{self.base_url}{post_data['url']}",
                        author=post_data['user']['displayName'],
                        content=post_data['htmlBody'],
                        published_date=post_date,
                        source='Alignment Forum'
                    )
                    posts.append(post)
            
            return posts
        except Exception as e:
            logger.error(f"Error fetching Alignment Forum posts: {e}")
            return []

class LessWrongScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.lesswrong.com"
        self.graphql_url = f"{self.base_url}/graphql"

    def get_recent_posts(self, days: int = 1) -> List[Post]:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # GraphQL query for recent posts
        query = """
        {
            posts(input: {
                limit: 50,
                sortedBy: "new"
            }) {
                results {
                    _id
                    title
                    url
                    htmlBody
                    postedAt
                    user {
                        displayName
                    }
                }
            }
        }
        """
        
        try:
            response = requests.post(
                self.graphql_url,
                json={'query': query},
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            posts = []
            for post_data in data['data']['posts']['results']:
                post_date = datetime.fromisoformat(post_data['postedAt'].replace('Z', '+00:00'))
                if post_date >= cutoff_date:
                    post = Post(
                        title=post_data['title'],
                        url=f"{self.base_url}{post_data['url']}",
                        author=post_data['user']['displayName'],
                        content=post_data['htmlBody'],
                        published_date=post_date,
                        source='LessWrong'
                    )
                    posts.append(post)
            
            return posts
        except Exception as e:
            logger.error(f"Error fetching LessWrong posts: {e}")
            return [] 