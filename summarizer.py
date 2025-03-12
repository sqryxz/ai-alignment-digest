import json
import re
import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Set
from collections import defaultdict

def clean_text(text: str) -> str:
    """Clean text by removing special characters and extra whitespace."""
    # Remove markdown formatting
    text = re.sub(r'\\[.*?\\]', '', text)
    text = re.sub(r'\\(.*?\\)', '', text)
    text = re.sub(r'#', '', text)
    text = re.sub(r'\*\*', '', text)
    text = re.sub(r'\*', '', text)
    text = re.sub(r'_', '', text)
    
    # Remove multiple newlines and spaces
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    # Remove publication timestamp
    text = re.sub(r'Published on.*?GMT', '', text)
    
    return text.strip()

def extract_first_paragraph(text: str, max_words: int = 200) -> str:
    """Extract and truncate the first meaningful paragraph of text."""
    # Clean the text first
    text = clean_text(text)
    
    # Split into sentences
    sentences = text.split('. ')
    
    # Take first few sentences that fit within max_words
    summary = ''
    word_count = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        words = sentence.split()
        if word_count + len(words) <= max_words:
            summary += sentence + '. '
            word_count += len(words)
        else:
            # Only add the sentence if we have less than 40 words
            # This prevents tiny summaries for long first sentences
            if word_count < 40:
                summary += sentence + '. '
            break
            
    return summary.strip()

def categorize_post(title: str, content: str) -> List[str]:
    """Categorize post into topics based on keywords."""
    topics = []
    
    # Define topic keywords
    topic_keywords = {
        'AI Safety': ['alignment', 'ai safety', 'agi', 'superintelligence', 'ml', 'machine learning'],
        'AI Capabilities': ['language model', 'llm', 'gpt', 'claude', 'deepseek', 'reasoning', 'training'],
        'Philosophy': ['ethics', 'philosophy', 'consciousness', 'rationality', 'epistemology'],
        'Technology': ['technology', 'software', 'programming', 'engineering'],
        'Science': ['physics', 'biology', 'research', 'experiment', 'study'],
        'Economics': ['economics', 'market', 'finance', 'money', 'economy'],
        'Meta': ['lesswrong', 'rationality', 'community'],
    }
    
    # Combine title and content for keyword search
    text = (title + ' ' + content).lower()
    
    # Check each topic's keywords
    for topic, keywords in topic_keywords.items():
        if any(keyword in text for keyword in keywords):
            topics.append(topic)
    
    # If no topics found, mark as Other
    if not topics:
        topics.append('Other')
    
    return topics

def load_processed_posts() -> Set[str]:
    """Load the set of already processed post URLs."""
    try:
        with open('processed_posts.json', 'r') as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

def save_processed_posts(processed: Set[str]):
    """Save the set of processed post URLs."""
    with open('processed_posts.json', 'w') as f:
        json.dump(list(processed), f)

def format_digest(date: str, posts_by_topic: Dict[str, List[Dict]]) -> str:
    # Get unique posts across all topics
    unique_posts = set()
    for posts in posts_by_topic.values():
        for post in posts:
            unique_posts.add(post['title'])
    
    # Create header
    digest = f"""================================================================================
AI Alignment Daily Digest - {date}

Today's digest contains {len(unique_posts)} unique posts across {len(posts_by_topic)} topics.
Some posts appear in multiple categories based on their content.

Key Themes:
-----------
"""
    
    # Analyze key themes across all posts
    all_posts = []
    for posts in posts_by_topic.values():
        all_posts.extend(posts)
    
    # Remove duplicates while preserving order
    seen = set()
    all_posts = [post for post in all_posts if post['title'] not in seen and not seen.add(post['title'])]
    
    # Sort all posts by date for chronological analysis
    all_posts.sort(key=lambda x: x['published_date'], reverse=True)
    
    # Extract common themes and discussions with more specific keywords
    themes = {
        "AI Safety & Control": {
            "keywords": ["alignment", "safety", "control", "risk", "secure", "robustness", "oversight"],
            "description": "Discussion of AI safety mechanisms, alignment strategies, and risk mitigation"
        },
        "Technical Progress": {
            "keywords": ["capabilities", "model", "training", "architecture", "performance", "implementation"],
            "description": "Technical developments in AI systems and capabilities"
        },
        "Philosophical Implications": {
            "keywords": ["ethics", "philosophy", "consciousness", "theory", "values", "moral", "rationality"],
            "description": "Exploration of ethical and philosophical aspects of AI development"
        },
        "Research & Methods": {
            "keywords": ["research", "methodology", "experiment", "empirical", "study", "analysis", "results"],
            "description": "Research methodologies and experimental findings"
        },
        "Policy & Governance": {
            "keywords": ["policy", "governance", "regulation", "coordination", "institution", "standards"],
            "description": "Regulatory frameworks and governance approaches"
        }
    }
    
    # Add relevant themes based on content
    theme_relevance = {}
    
    for theme, info in themes.items():
        relevant_posts = []
        for post in all_posts:
            # Combine title and content, but give more weight to title matches
            title = post['title'].lower()
            content = post['content'].lower()
            
            # Count keyword matches
            title_matches = sum(keyword in title for keyword in info['keywords'])
            content_matches = sum(keyword in content for keyword in info['keywords'])
            
            # Weight title matches more heavily
            relevance_score = (title_matches * 2) + (content_matches * 0.5)
            
            if relevance_score > 0:
                relevant_posts.append((post['title'], relevance_score))
        
        if relevant_posts:
            # Sort by relevance score
            relevant_posts.sort(key=lambda x: x[1], reverse=True)
            theme_relevance[theme] = {
                'posts': relevant_posts,
                'score': sum(score for _, score in relevant_posts)
            }
    
    if theme_relevance:
        # Sort themes by overall relevance score
        sorted_themes = sorted(theme_relevance.items(), key=lambda x: x[1]['score'], reverse=True)
        
        for theme, data in sorted_themes:
            post_count = len(data['posts'])
            digest += f"• {theme}\n"
            digest += f"  {themes[theme]['description']}\n"
            digest += f"  {post_count} related posts, including:\n"
            # Show up to 3 most relevant posts
            for title, _ in data['posts'][:3]:
                digest += f"  - {title}\n"
            digest += "\n"
    
    # Add topic sections
    digest += "\nDetailed Posts by Category:\n"
    digest += "------------------------\n\n"
    
    for topic, posts in posts_by_topic.items():
        if not posts:
            continue
            
        digest += f"=== {topic} ({len(posts)} posts) ===\n\n"
        
        # Sort posts by date within each topic
        posts.sort(key=lambda x: x['published_date'], reverse=True)
        
        for post in posts:
            title = post['title']
            author = post['author']
            source = post['source']
            date = post['published_date']
            summary = post['summary']
            
            # Get all categories this post appears in
            categories = [t for t, p in posts_by_topic.items() if any(p_info['title'] == title for p_info in p)]
            other_categories = [c for c in categories if c != topic]
            
            digest += f"• {title}\n"
            digest += f"  By {author} ({source}) - {date}\n"
            if other_categories:
                digest += f"  Also appears in: {', '.join(other_categories)}\n"
            digest += f"  {summary}\n\n"
    
    return digest

def create_daily_digest(file_path: str, days_lookback: int = 1) -> str:
    """Create a daily digest of recent posts."""
    print("Starting digest creation...")
    
    # Clear processed posts for testing
    save_processed_posts(set())
    processed_posts = set()
    print("Cleared processed posts")
    
    # Read and parse posts
    with open(file_path, 'r') as f:
        data = json.load(f)
    print(f"Loaded {len(data['posts'])} posts from {file_path}")
    
    # Calculate cutoff date (use UTC)
    # Use the fetch time from the JSON file as reference
    fetch_time = datetime.fromisoformat(data['fetch_time']).replace(tzinfo=timezone.utc)
    cutoff_date = fetch_time - timedelta(days=days_lookback)
    print(f"Using fetch time: {fetch_time}")
    print(f"Cutoff date: {cutoff_date}")
    
    # Group posts by topic
    posts_by_topic = defaultdict(list)
    new_processed = set()
    
    for post in data['posts']:
        # Parse post date with timezone info
        post_date = datetime.fromisoformat(post['published_date']).replace(tzinfo=timezone.utc)
        print(f"Processing post: {post['title']} (date: {post_date})")
        
        # Skip if already processed
        if post['url'] in processed_posts:
            print(f"Skipping already processed post: {post['title']}")
            continue
            
        # Skip if too old
        if post_date < cutoff_date:
            print(f"Skipping old post: {post['title']}")
            continue
            
        # Get post summary
        post_summary = extract_first_paragraph(post['content'])
        
        # Create post info
        post_info = {
            'title': post['title'],
            'author': post['author'],
            'published_date': post_date.strftime('%Y-%m-%d'),
            'source': post['source'],
            'summary': post_summary,
            'content': post['content']
        }
        
        # Categorize and add to topics
        topics = categorize_post(post['title'], post['content'])
        print(f"Topics for {post['title']}: {topics}")
        
        for topic in topics:
            posts_by_topic[topic].append(post_info)
            
        # Mark as processed
        new_processed.add(post['url'])
    
    print(f"\nFound {len(posts_by_topic)} topics:")
    for topic, posts in posts_by_topic.items():
        print(f"- {topic}: {len(posts)} posts")
    
    # Sort topics by post count
    posts_by_topic = dict(sorted(
        posts_by_topic.items(),
        key=lambda x: len(x[1]),
        reverse=True
    ))
    
    # Update processed posts
    processed_posts.update(new_processed)
    save_processed_posts(processed_posts)
    
    # Format digest
    today = fetch_time.strftime('%Y-%m-%d')
    digest = format_digest(today, posts_by_topic)
    
    return digest

def main():
    """Main function to run the summarizer."""
    try:
        # Create daily digest
        digest = create_daily_digest('sample_posts.json')
        
        # Save to file
        output_file = f"digest_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.txt"
        with open(output_file, 'w') as f:
            f.write(digest)
            
        print(f"Daily digest has been saved to {output_file}")
        print("\nDigest contents:")
        print("=" * 80)
        print(digest)
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 