import os
import requests
import html2text
from typing import Dict, List
import logging
from datetime import datetime
import yaml
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize

# Set up logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_alignment_digest.log'),
        logging.StreamHandler()
    ]
)
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

        # Initialize NLTK for fallback summarization
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
    def _clean_content(self, html_content: str) -> str:
        """Convert HTML to markdown and clean the content."""
        # First convert to plain text
        text = self.html_converter.handle(html_content)
        
        # Clean up extra whitespace
        text = ' '.join(text.split())
        return text

    def _fallback_summarize(self, content: str, num_sentences: int = 5) -> str:
        """Generate a fallback summary using extractive summarization techniques."""
        try:
            # Ensure NLTK data is available
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt')
                
            # Tokenize the content into sentences
            sentences = nltk.sent_tokenize(content)
            
            if not sentences:
                return "Could not generate summary: no valid sentences found."
                
            # If content is very short, return it as is
            if len(sentences) <= num_sentences:
                return " ".join(sentences)
                
            # Calculate sentence scores based on position and length
            scores = {}
            for i, sentence in enumerate(sentences):
                # Position score - favor early sentences but also include some later ones
                position_score = 1.0 / (1 + i * 0.1)
                
                # Length score - penalize very short or very long sentences
                words = len(sentence.split())
                length_score = 1.0 if 10 <= words <= 30 else 0.5
                
                # Title word score - favor sentences containing important capitalized terms
                title_words = set(word for word in sentence.split() 
                                if word[0].isupper() and len(word) > 1)
                title_score = len(title_words) * 0.1
                
                # Technical term score - favor sentences with likely technical terms
                technical_indicators = ['AI', 'ML', 'algorithm', 'model', 'training',
                                     'neural', 'network', 'optimization', 'loss',
                                     'function', 'probability', 'distribution',
                                     'parameter', 'gradient', 'objective']
                technical_score = sum(1 for term in technical_indicators 
                                   if term.lower() in sentence.lower()) * 0.2
                
                # Combine scores
                scores[i] = position_score + length_score + title_score + technical_score
            
            # Select top sentences while preserving order
            top_indices = sorted(sorted(scores, key=scores.get, reverse=True)[:num_sentences])
            summary_sentences = [sentences[i] for i in top_indices]
            
            return " ".join(summary_sentences)
            
        except Exception as e:
            logger.error(f"Error in fallback summarization: {str(e)}")
            # If all else fails, return the first few sentences
            sentences = content.split('.')[:num_sentences]
            return '. '.join(sentences) + '.'

    def _call_deepseek_api(self, messages: List[Dict], max_tokens: int = 300, temperature: float = 0.7) -> Dict:
        """Make a call to the Deepseek API with improved error handling."""
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
            
            logger.info(f"Making API call to Deepseek with model {self.config['summarization']['model']}")
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30  # Add timeout
            )
            
            # Log response status
            logger.info(f"API response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"API error: {response.status_code} - {response.text}")
                raise requests.exceptions.RequestException(f"API returned status code {response.status_code}")
                
            return response.json()
        except requests.exceptions.Timeout:
            logger.error("API call timed out")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in API call: {str(e)}")
            raise

    def summarize_post(self, content: str, title: str) -> Dict:
        """Summarize a single post using the Deepseek API with fallback options."""
        try:
            cleaned_content = self._clean_content(content)
            
            # Truncate content if it's too long
            if len(cleaned_content) > 8000:
                cleaned_content = cleaned_content[:8000] + "..."
            
            # System prompt for main summary
            system_prompt = """You are an expert in AI alignment and rationality who creates precise, technical summaries of research posts. Focus on:
1. Key technical concepts and arguments
2. Main conclusions and their implications
3. Novel insights or methodologies
4. Connections to existing research

Keep the technical accuracy high while being concise."""

            # User prompt for main summary
            user_prompt = f"""Please provide a technical summary of this AI alignment post that:
1. Preserves the key technical details and mathematical/logical arguments
2. Highlights the main contributions or insights
3. Maintains technical precision
4. Connects to broader AI alignment discourse

Title: {title}
Content: {cleaned_content}"""

            try:
                # Try main API call
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
                summary_response = self._call_deepseek_api(messages)
                main_summary = summary_response["choices"][0]["message"]["content"].strip()
                
                # System prompt for topic categorization
                topic_system_prompt = """You are an expert in categorizing AI alignment research. Identify the primary research area and explain its significance to the field."""
                
                # User prompt for topic categorization
                topic_user_prompt = f"""Based on this summary, what is the main research category? Choose from:
- Technical AI Safety (mathematical frameworks, formal methods, ML architecture)
- AI Alignment Theory (value learning, preference learning, goal structures)
- AI Governance & Policy (coordination, regulation, deployment frameworks)
- AI Capabilities Analysis (progress evaluation, capability assessment)
- Methodological Contributions (research approaches, experimental design)

Explain the categorization in terms of the post's technical contributions.

Summary: {main_summary}"""

                # Try topic categorization
                topic_messages = [
                    {"role": "system", "content": topic_system_prompt},
                    {"role": "user", "content": topic_user_prompt}
                ]
                topic_response = self._call_deepseek_api(topic_messages)
                topic_result = topic_response["choices"][0]["message"]["content"].strip()
                
                return {
                    "summary": main_summary,
                    "topic": topic_result,
                    "method": "api"
                }
                
            except Exception as api_error:
                logger.warning(f"API summarization failed, falling back to extractive summary: {str(api_error)}")
                fallback_summary = self._fallback_summarize(cleaned_content)
                return {
                    "summary": fallback_summary,
                    "topic": "Uncategorized (Fallback)",
                    "method": "fallback"
                }
                
        except Exception as e:
            logger.error(f"Error in summarize_post: {str(e)}")
            return {
                "summary": "Error generating summary.",
                "topic": "Error",
                "method": "error"
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