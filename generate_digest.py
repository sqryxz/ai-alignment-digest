import json
from datetime import datetime
from src.summarizer import Summarizer

def format_digest_as_markdown(digest_data: dict) -> str:
    """Format the digest data as a markdown document."""
    md = f"# AI Alignment Digest - {digest_data['summary']['date_range']}\n\n"
    
    # Add overview
    md += "## Overview\n\n"
    md += f"{digest_data['summary']['overview']}\n\n"
    
    # Add key topics
    for topic in digest_data['summary']['key_topics']:
        md += f"## {topic['name']}\n\n"
        md += f"{topic['summary']}\n\n"
        if topic['key_posts']:
            md += "### Key Posts\n"
            for url in topic['key_posts']:
                md += f"- {url}\n"
        md += "\n"
    
    return md

def main():
    # Load posts from sample_posts.json
    with open('sample_posts.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        posts = data['posts']
    
    # Initialize summarizer
    summarizer = Summarizer()
    
    # Generate digest
    print("Generating digest...")
    digest_data = summarizer.create_digest(posts)
    
    # Format as markdown
    digest_md = format_digest_as_markdown(digest_data)
    
    # Save digest
    today = datetime.now().strftime('%Y-%m-%d')
    digest_path = f'data/digests/digest_{today}.md'
    latest_path = 'data/digests/latest.md'
    
    # Save to both dated file and latest.md
    for path in [digest_path, latest_path]:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(digest_md)
    
    print(f"Digest saved to {digest_path} and {latest_path}")

if __name__ == '__main__':
    main() 