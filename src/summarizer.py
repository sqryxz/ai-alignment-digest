import os
import requests
import html2text
from typing import Dict, List
import logging
from datetime import datetime
import yaml

logger = logging.getLogger(__name__)

class Summarizer:
    def __init__(self):
        # Load config
        with open('config/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Set up Deepseek API key
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is not set")
        
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
        
    def _clean_content(self, html_content: str) -> str:
        """Convert HTML to markdown and clean the content."""
        return self.html_converter.handle(html_content)

    def _call_deepseek_api(self, messages: List[Dict], max_tokens: int = 300, temperature: float = 0.7) -> Dict:
        """Make a call to the Deepseek API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.config['summarization']['model'],
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error calling Deepseek API: {e}")
            raise

    def summarize_post(self, content: str, title: str) -> Dict:
        """Summarize a single post using the Deepseek API."""
        try:
            cleaned_content = self._clean_content(content)
            
            # Truncate content if it's too long
            if len(cleaned_content) > 8000:
                cleaned_content = cleaned_content[:8000] + "..."
            
            # System prompt for main summary
            system_prompt = """You are a helpful AI that explains complex AI alignment concepts in simple terms. Your goal is to make these ideas accessible to a younger audience (around 12 years old). Break down technical ideas into clear, engaging explanations using everyday examples. Focus on why these ideas matter and how they connect to things people already understand."""

            # User prompt for main summary
            user_prompt = f"""Please summarize this AI alignment blog post in simple terms for a layperson. Focus on:
1. The main idea in 1-2 sentences using everyday language
2. Why this matters, using a real-world example or analogy
3. The key points, explained simply

Title: {title}
Content: {cleaned_content}"""

            # Get main summary
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            summary_response = self._call_deepseek_api(messages)
            
            # System prompt for topic categorization
            topic_system_prompt = """You are a helpful AI that explains AI alignment topics in simple terms. Your goal is to identify the main topic of a post and explain why it matters in a way that's easy to understand."""
            
            # User prompt for topic categorization
            topic_user_prompt = f"""Based on this summary, what is the main topic category of this post? Choose from:
- Making AI Safe & Aligned (about making sure AI systems do what we want)
- Technical Research (about the specific ways we're trying to make AI safe)
- Policy & Rules (about how society should handle AI)

Explain your choice in 1-2 simple sentences.

Summary: {summary_response["choices"][0]["message"]["content"]}"""

            # Get topic categorization
            topic_messages = [
                {"role": "system", "content": topic_system_prompt},
                {"role": "user", "content": topic_user_prompt}
            ]
            topic_response = self._call_deepseek_api(topic_messages)
            
            return {
                "summary": summary_response["choices"][0]["message"]["content"].strip(),
                "topic": topic_response["choices"][0]["message"]["content"].strip()
            }
        except Exception as e:
            logger.error(f"Error summarizing post: {e}")
            return {
                "summary": "Error generating summary.",
                "topic": "Uncategorized"
            }

    def create_digest(self, posts: List[Dict]) -> Dict:
        """Create a structured digest from a list of posts."""
        if not posts:
            return {
                "fetch_time": datetime.now().isoformat(),
                "summary": {
                    "date_range": datetime.now().strftime("%B %d, %Y"),
                    "overview": "No new posts today.",
                    "key_topics": []
                },
                "total_posts": 0,
                "posts": []
            }

        # Process all posts
        processed_posts = []
        topics = {}
        
        for post in posts:
            summary_data = self.summarize_post(post['content'], post['title'])
            topic_name = summary_data['topic']
            
            if topic_name not in topics:
                topics[topic_name] = {
                    "name": topic_name,
                    "summaries": [],
                    "posts": [],
                    "context": summary_data['topic']
                }
            
            topics[topic_name]['summaries'].append(summary_data['summary'])
            topics[topic_name]['posts'].append(post['url'])
            
            processed_posts.append({
                **post,
                "summary": summary_data['summary']
            })

        # Create overview of all topics
        overview = self._generate_overview([t['context'] for t in topics.values()])

        # Format the final digest
        return {
            "fetch_time": datetime.now().isoformat(),
            "summary": {
                "date_range": f"{datetime.now().strftime('%B %d, %Y')}",
                "overview": overview,
                "key_topics": [
                    {
                        "name": topic_data['name'],
                        "summary": self._combine_summaries(topic_data['summaries']),
                        "key_posts": topic_data['posts'][:2]  # Include up to 2 key posts per topic
                    }
                    for topic_data in topics.values()
                ]
            },
            "total_posts": len(posts),
            "posts": processed_posts
        }

    def _generate_overview(self, topic_contexts: List[str]) -> str:
        """Generate an overview of the key developments and themes."""
        try:
            system_prompt = """You are a helpful AI that makes complex AI safety discussions easy to understand. Your goal is to explain the big picture in a way that's clear and engaging for a younger audience (around 12 years old)."""
            
            user_prompt = f"""Based on these summaries of recent AI alignment posts, write a short overview that:
1. Explains the main themes in simple terms
2. Uses clear examples to help understand why these ideas matter
3. Avoids technical jargon and complex language

Summaries: {topic_contexts}"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            response = self._call_deepseek_api(messages)
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"Error generating overview: {e}")
            return "Error generating overview."

    def _combine_summaries(self, summaries: List[str]) -> str:
        """Combine multiple summaries into a coherent narrative."""
        try:
            system_prompt = """You are a helpful AI that makes complex ideas easy to understand. Your goal is to combine multiple summaries into a clear story that a 12-year-old could follow."""
            
            user_prompt = f"""Please combine these summaries into a clear narrative that:
1. Uses simple, everyday language
2. Explains why these ideas matter
3. Connects different ideas in a way that's easy to follow
4. Uses examples and analogies to make abstract concepts concrete

Summaries: {summaries}"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            response = self._call_deepseek_api(messages)
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"Error combining summaries: {e}")
            return "Error combining summaries." 