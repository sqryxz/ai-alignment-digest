import os
import openai
import html2text
from typing import Dict, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Summarizer:
    def __init__(self):
        openai.api_key = os.getenv('DEEPSEEK_API_KEY')
        openai.api_base = "https://api.deepseek.com/v1"
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
        
    def _clean_content(self, html_content: str) -> str:
        """Convert HTML to markdown and clean the content."""
        return self.html_converter.handle(html_content)

    def summarize_post(self, content: str, title: str) -> Dict:
        """Summarize a single post using DeepSeek's API."""
        cleaned_content = self._clean_content(content)
        
        # Truncate content if it's too long
        if len(cleaned_content) > 8000:
            cleaned_content = cleaned_content[:8000] + "..."

        try:
            response = openai.ChatCompletion.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates detailed, narrative-style summaries of AI alignment blog posts. Focus on explaining the key ideas, arguments, and conclusions in clear, flowing paragraphs that a general audience can understand."},
                    {"role": "user", "content": f"Please provide a comprehensive summary (2-3 paragraphs) of this AI alignment blog post titled '{title}'. Focus on explaining the main ideas in clear language that connects thoughts naturally:\n\n{cleaned_content}"}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            # Get topic categorization
            topic_response = openai.ChatCompletion.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that categorizes AI alignment content into key topics."},
                    {"role": "user", "content": f"Based on this post titled '{title}', what is the main topic category it belongs to (e.g. 'AI Safety & Alignment', 'Technical Research', 'Policy & Governance')? Also provide a one-paragraph explanation of how it contributes to this topic:\n\n{cleaned_content}"}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return {
                "summary": response.choices[0].message['content'].strip(),
                "topic": {
                    "name": topic_response.choices[0].message['content'].split('\n')[0].strip(),
                    "context": topic_response.choices[0].message['content'].split('\n', 1)[1].strip() if '\n' in topic_response.choices[0].message['content'] else ""
                }
            }
        except Exception as e:
            logger.error(f"Error summarizing post: {e}")
            return {
                "summary": "Error generating summary.",
                "topic": {
                    "name": "Uncategorized",
                    "context": ""
                }
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
            topic_name = summary_data['topic']['name']
            
            if topic_name not in topics:
                topics[topic_name] = {
                    "name": topic_name,
                    "summaries": [],
                    "posts": [],
                    "context": summary_data['topic']['context']
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
        """Generate an overall summary from topic contexts."""
        try:
            response = openai.ChatCompletion.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates high-level overviews of AI alignment discussions."},
                    {"role": "user", "content": f"Based on these topic summaries, provide a concise overview paragraph of the main themes and developments:\n\n{' '.join(topic_contexts)}"}
                ],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            logger.error(f"Error generating overview: {e}")
            return "Error generating overview."

    def _combine_summaries(self, summaries: List[str]) -> str:
        """Combine multiple summaries into a coherent paragraph."""
        try:
            response = openai.ChatCompletion.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that combines multiple summaries into a coherent narrative."},
                    {"role": "user", "content": f"Please combine these summaries into a single coherent paragraph that flows naturally:\n\n{' '.join(summaries)}"}
                ],
                max_tokens=250,
                temperature=0.7
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            logger.error(f"Error combining summaries: {e}")
            return "Error combining summaries." 