import os
import logging
import json
from datetime import datetime
import schedule
import time
from pathlib import Path
from dotenv import load_dotenv
import sys
from typing import List, Dict

from scrapers import AlignmentForumScraper, LessWrongScraper, Post
from summarizer import Summarizer

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ai_alignment_digest.log')
    ]
)
logger = logging.getLogger(__name__)

class DigestGenerator:
    def __init__(self):
        self.af_scraper = AlignmentForumScraper()
        self.lw_scraper = LessWrongScraper()
        self.summarizer = Summarizer()
        
        # Create output directory if it doesn't exist
        self.output_dir = Path("data/digests")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _fetch_posts(self, scraper, source_name: str) -> List[Post]:
        """Fetch posts from a scraper with error handling."""
        try:
            logger.info(f"Fetching posts from {source_name}...")
            posts = scraper.get_recent_posts(days=1)
            logger.info(f"Successfully fetched {len(posts)} posts from {source_name}")
            return posts
        except Exception as e:
            logger.error(f"Failed to fetch posts from {source_name}: {str(e)}")
            return []

    def _generate_markdown(self, digest_data: Dict) -> str:
        """Convert the digest data to markdown format."""
        md = f"# AI Alignment Daily Digest - {digest_data['summary']['date_range']}\n\n"
        
        # Add overview
        md += "## Overview\n\n"
        md += f"{digest_data['summary']['overview']}\n\n"
        
        # Add key topics
        md += "## Key Topics\n\n"
        for topic in digest_data['summary']['key_topics']:
            md += f"### {topic['name']}\n\n"
            md += f"{topic['summary']}\n\n"
            if topic.get('key_posts'):
                md += "**Key Posts:**\n"
                for post_url in topic['key_posts']:
                    post = next((p for p in digest_data['posts'] if p['url'] == post_url), None)
                    if post:
                        md += f"- [{post['title']}]({post_url}) by {post['author']}\n"
                md += "\n"
        
        # Add all posts
        md += "## All Posts\n\n"
        for post in digest_data['posts']:
            md += f"### [{post['title']}]({post['url']})\n"
            md += f"**Author:** {post['author']}  \n"
            md += f"**Published:** {datetime.fromisoformat(post['published_date']).strftime('%Y-%m-%d %H:%M')} UTC  \n"
            md += f"**Source:** {post['source']}\n\n"
            md += f"{post['summary']}\n\n"
            md += "---\n\n"
        
        return md

    def generate_daily_digest(self):
        """Generate the daily digest of AI alignment posts."""
        logger.info("Starting daily digest generation...")
        
        try:
            # Collect posts from both sources with proper error handling
            af_posts = self._fetch_posts(self.af_scraper, "Alignment Forum")
            lw_posts = self._fetch_posts(self.lw_scraper, "LessWrong")
            
            # Combine and convert to dict format
            all_posts = [post.to_dict() for post in af_posts + lw_posts]
            
            if not all_posts:
                logger.warning("No posts were fetched from any source")
            
            # Generate digest
            digest_data = self.summarizer.create_digest(all_posts)
            
            # Save JSON digest
            date_str = datetime.now().strftime('%Y-%m-%d')
            json_file = self.output_dir / f"digest_{date_str}.json"
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(digest_data, f, indent=2, ensure_ascii=False)
            
            # Generate and save markdown version
            markdown_content = self._generate_markdown(digest_data)
            md_file = self.output_dir / f"digest_{date_str}.md"
            
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            # Save latest versions
            latest_json = self.output_dir / "latest.json"
            latest_md = self.output_dir / "latest.md"
            
            with open(latest_json, 'w', encoding='utf-8') as f:
                json.dump(digest_data, f, indent=2, ensure_ascii=False)
            
            with open(latest_md, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Daily digest generated successfully: {json_file}, {md_file}")
                
        except Exception as e:
            logger.error(f"Error generating daily digest: {str(e)}", exc_info=True)

def main():
    try:
        # Check for required environment variables
        if not os.getenv('DEEPSEEK_API_KEY'):
            logger.error("DEEPSEEK_API_KEY environment variable is not set!")
            return

        generator = DigestGenerator()
        
        # Schedule the job to run daily at 00:00 UTC
        schedule.every().day.at("00:00").do(generator.generate_daily_digest)
        
        # Also run immediately on startup
        generator.generate_daily_digest()
        
        logger.info("Digest generator started. Running daily at 00:00 UTC.")
        
        # Keep the script running with proper signal handling
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Received shutdown signal. Stopping gracefully...")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 