from src.scrapers import AlignmentForumScraper, LessWrongScraper
import json
from datetime import datetime

def display_post(post):
    """Format and display a single post"""
    print("\n" + "="*80)
    print(f"Title: {post.title}")
    print(f"Author: {post.author}")
    print(f"Source: {post.source}")
    print(f"Date: {post.published_date.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"URL: {post.url}")
    print("-"*80)
    # Show first 500 characters of content with ellipsis if truncated
    content_preview = post.content[:500]
    if len(post.content) > 500:
        content_preview += "..."
    print(f"Content Preview:\n{content_preview}")
    print("="*80)

def main():
    # Initialize scrapers
    af_scraper = AlignmentForumScraper()
    lw_scraper = LessWrongScraper()
    
    # Get posts from last 2 days to ensure we have some content
    days = 2
    
    print(f"\nFetching posts from the last {days} days...")
    
    # Fetch posts from Alignment Forum
    print("\nAlignment Forum Posts:")
    af_posts = af_scraper.get_recent_posts(days=days)
    print(f"Found {len(af_posts)} posts from Alignment Forum")
    for post in af_posts[:2]:  # Show first 2 posts
        display_post(post)
    
    # Fetch posts from LessWrong
    print("\nLessWrong Posts:")
    lw_posts = lw_scraper.get_recent_posts(days=days)
    print(f"Found {len(lw_posts)} posts from LessWrong")
    for post in lw_posts[:2]:  # Show first 2 posts
        display_post(post)
    
    # Save all posts to a JSON file
    all_posts = af_posts + lw_posts
    output = {
        'fetch_time': datetime.now().isoformat(),
        'total_posts': len(all_posts),
        'posts': [post.to_dict() for post in all_posts]
    }
    
    with open('sample_posts.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(all_posts)} posts to sample_posts.json")

if __name__ == '__main__':
    main() 