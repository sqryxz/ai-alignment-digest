import os
from openai import OpenAI
import html2text
from typing import Dict, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Summarizer:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv('DEEPSEEK_API_KEY'),
            base_url="https://api.deepseek.com"
        )
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
        
    def _clean_content(self, html_content: str) -> str:
        """Convert HTML to markdown and clean the content."""
        return self.html_converter.handle(html_content)

    def summarize_post(self, content: str, title: str) -> str:
        """Summarize a single post using DeepSeek's API."""
        cleaned_content = self._clean_content(content)
        
        # Truncate content if it's too long
        if len(cleaned_content) > 8000:
            cleaned_content = cleaned_content[:8000] + "..."

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",  # Using DeepSeek's latest chat model
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise, informative summaries of AI alignment blog posts. Focus on the key ideas, arguments, and conclusions."},
                    {"role": "user", "content": f"Please provide a concise summary (2-3 sentences) of this AI alignment blog post titled '{title}':\n\n{cleaned_content}"}
                ],
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error summarizing post: {e}")
            return "Error generating summary."

    def create_daily_digest(self, posts: List[Dict]) -> str:
        """Create a formatted daily digest from a list of posts."""
        if not posts:
            return "No new posts today."

        digest = f"# AI Alignment Daily Digest - {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        # Group posts by source
        posts_by_source = {}
        for post in posts:
            source = post['source']
            if source not in posts_by_source:
                posts_by_source[source] = []
            posts_by_source[source].append(post)

        # Create digest for each source
        for source, source_posts in posts_by_source.items():
            digest += f"## {source}\n\n"
            for post in source_posts:
                summary = self.summarize_post(post['content'], post['title'])
                digest += f"### [{post['title']}]({post['url']})\n"
                digest += f"**Author:** {post['author']}  \n"
                digest += f"**Published:** {datetime.fromisoformat(post['published_date']).strftime('%Y-%m-%d %H:%M')} UTC\n\n"
                digest += f"{summary}\n\n"
                digest += "---\n\n"

        return digest 