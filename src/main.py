import os
import logging
from datetime import datetime
import schedule
import time
from pathlib import Path
from dotenv import load_dotenv

from scrapers import AlignmentForumScraper, LessWrongScraper
from summarizer import Summarizer

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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

    def generate_daily_digest(self):
        """Generate the daily digest of AI alignment posts."""
        logger.info("Starting daily digest generation...")
        
        try:
            # Collect posts from both sources
            af_posts = self.af_scraper.get_recent_posts(days=1)
            lw_posts = self.lw_scraper.get_recent_posts(days=1)
            
            # Combine and convert to dict format
            all_posts = [post.to_dict() for post in af_posts + lw_posts]
            
            # Generate digest
            digest_content = self.summarizer.create_daily_digest(all_posts)
            
            # Save digest
            date_str = datetime.now().strftime('%Y-%m-%d')
            output_file = self.output_dir / f"digest_{date_str}.md"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(digest_content)
            
            logger.info(f"Daily digest generated successfully: {output_file}")
            
            # Also save as latest.md for easy access
            latest_file = self.output_dir / "latest.md"
            with open(latest_file, 'w', encoding='utf-8') as f:
                f.write(digest_content)
                
        except Exception as e:
            logger.error(f"Error generating daily digest: {e}")

def main():
    if not os.getenv('DEEPSEEK_API_KEY'):
        logger.error("DEEPSEEK_API_KEY environment variable is not set!")
        return

    generator = DigestGenerator()
    
    # Schedule the job to run daily at 00:00 UTC
    schedule.every().day.at("00:00").do(generator.generate_daily_digest)
    
    # Also run immediately on startup
    generator.generate_daily_digest()
    
    logger.info("Digest generator started. Running daily at 00:00 UTC.")
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main() 