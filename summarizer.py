#!/usr/bin/env python3
import os
import sys
from datetime import datetime
import json
from src.summarizer import Summarizer
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_alignment_digest.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_posts(posts_dir: str) -> list:
    """Load posts from the posts directory."""
    posts = []
    try:
        posts_path = Path(posts_dir)
        if not posts_path.exists():
            logger.warning(f"Posts directory {posts_dir} does not exist")
            return posts

        for file in posts_path.glob('*.json'):
            try:
                with open(file, 'r') as f:
                    post_data = json.load(f)
                    posts.append(post_data)
            except Exception as e:
                logger.error(f"Error loading post from {file}: {str(e)}")
                continue

        return posts
    except Exception as e:
        logger.error(f"Error loading posts: {str(e)}")
        return posts

def save_digest(digest: dict, output_dir: str):
    """Save the digest to a file."""
    try:
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate filename with date
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = f"digest_{date_str}.txt"
        filepath = Path(output_dir) / filename
        
        # Format digest content
        content = []
        content.append("=" * 80)
        content.append(f"AI Alignment Daily Digest - {digest['summary']['date_range']}\n")
        
        # Add overview
        if digest['total_posts'] > 0:
            content.append(f"Today's digest contains {digest['total_posts']} unique posts across {len(digest['summary']['key_topics'])} topics.")
            content.append("Some posts appear in multiple categories based on their content.\n")
            
            # Add key themes section
            content.append("Key Themes:")
            content.append("-" * 11)
            for topic in digest['summary']['key_topics']:
                content.append(f"• {topic['name']}")
                if len(topic['key_posts']) > 0:
                    content.append("  " + topic['summary'])
                    content.append("  " + str(len(topic['key_posts'])) + " related posts, including:")
                    for post_url in topic['key_posts']:
                        post_title = next((p['title'] for p in digest['posts'] if p['url'] == post_url), None)
                        if post_title:
                            content.append(f"  - {post_title}")
                content.append("")
            
            # Add detailed posts section
            content.append("\nDetailed Posts by Category:")
            content.append("------------------------\n")
            
            # Group posts by category
            categories = {}
            for post in digest['posts']:
                for category in post.get('categories', ['Uncategorized']):
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(post)
            
            # Add posts under each category
            for category, posts in sorted(categories.items()):
                content.append(f"=== {category} ({len(posts)} posts) ===\n")
                for post in posts:
                    content.append(f"• {post['title']}")
                    content.append(f"  By {post.get('author', 'Unknown')} ({post.get('source', 'Unknown')}) - {post.get('date', 'Unknown date')}")
                    
                    # Add cross-references to other categories
                    other_categories = [c for c in post.get('categories', []) if c != category]
                    if other_categories:
                        content.append(f"  Also appears in: {', '.join(other_categories)}")
                    
                    # Add summary
                    if 'summary' in post:
                        content.append(f"  {post['summary']}\n")
        else:
            content.append("No new posts today.")
        
        # Write to file
        with open(filepath, 'w') as f:
            f.write('\n'.join(content))
            
        logger.info(f"Saved digest to {filepath}")
        
    except Exception as e:
        logger.error(f"Error saving digest: {str(e)}")
        raise

def main():
    try:
        # Initialize summarizer
        summarizer = Summarizer()
        logger.info("Summarizer initialized successfully")
        
        # Load posts
        posts = load_posts('data/posts')
        logger.info(f"Loaded {len(posts)} posts")
        
        # Generate digest
        digest = summarizer.create_digest(posts)
        logger.info("Generated digest")
        
        # Save digest
        save_digest(digest, 'data/digests')
        logger.info("Saved digest")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 