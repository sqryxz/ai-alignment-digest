#!/usr/bin/env python3
import os
import sys
import json
from datetime import datetime
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_workflow.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_test_environment():
    """Create necessary directories and test data."""
    logger.info("Setting up test environment")
    
    # Create directories
    Path('data/posts').mkdir(parents=True, exist_ok=True)
    Path('data/digests').mkdir(parents=True, exist_ok=True)
    
    # Create sample test posts
    test_posts = [
        {
            "title": "Test Post 1: UDT and Bayesianism",
            "content": """Epistemic status: Using UDT as a case study for the tools developed in my meta-theory of rationality sequence so far.
            
            The core problem of UDT is that it's trying to be consistent in a way that Bayesianism can't handle. Specifically:
            1. UDT wants to make decisions that are consistent across possible worlds
            2. But Bayesianism can only handle uncertainty about what world you're in
            3. This creates interesting challenges for AI alignment""",
            "author": "Test Author",
            "source": "LessWrong",
            "url": "https://example.com/post1",
            "published_date": datetime.now().isoformat(),
            "categories": ["AI Safety", "Philosophy"]
        },
        {
            "title": "Test Post 2: AI Interpretability",
            "content": """The Most Forbidden Technique is training an AI using interpretability techniques. 
            An AI produces a final output [X] via some method [M]. You can analyze [M] using technique [T], 
            to learn what the AI is up to. You could train on that. Never do that. You train on [X]. 
            Only [X]. Never [M], never [T]. Why? Because [T] is how you figure out when the model is misbehaving.""",
            "author": "Another Author",
            "source": "AI Alignment Forum",
            "url": "https://example.com/post2",
            "published_date": datetime.now().isoformat(),
            "categories": ["AI Safety", "Technical"]
        }
    ]
    
    # Save test posts
    for i, post in enumerate(test_posts):
        with open(f'data/posts/test_post_{i+1}.json', 'w') as f:
            json.dump(post, f, indent=2)
    
    logger.info(f"Created {len(test_posts)} test posts")
    return len(test_posts)

def verify_digest_output():
    """Verify that the digest was created and contains expected content."""
    logger.info("Verifying digest output")
    
    # Check for digest file
    digest_dir = Path('data/digests')
    digest_files = list(digest_dir.glob('digest_*.txt'))
    
    if not digest_files:
        logger.error("No digest files found")
        return False
    
    # Get most recent digest
    latest_digest = max(digest_files, key=lambda x: x.stat().st_mtime)
    logger.info(f"Found digest file: {latest_digest}")
    
    # Read and verify content
    with open(latest_digest, 'r') as f:
        content = f.read()
        
    # Check for expected sections
    checks = [
        ("Header", "AI Alignment Daily Digest" in content),
        ("Key Themes", "Key Themes:" in content),
        ("Detailed Posts", "Detailed Posts by Category:" in content),
        ("Test Post 1", "Test Post 1: UDT and Bayesianism" in content),
        ("Test Post 2", "Test Post 2: AI Interpretability" in content)
    ]
    
    all_passed = True
    for section, passed in checks:
        if passed:
            logger.info(f"✓ {section} check passed")
        else:
            logger.error(f"✗ {section} check failed")
            all_passed = False
    
    return all_passed

def main():
    try:
        # Setup test environment
        num_posts = setup_test_environment()
        logger.info(f"Test environment setup complete with {num_posts} posts")
        
        # Run the summarizer
        logger.info("Running summarizer")
        os.system('python summarizer.py')
        
        # Verify output
        if verify_digest_output():
            logger.info("All tests passed successfully!")
            return 0
        else:
            logger.error("Some tests failed")
            return 1
            
    except Exception as e:
        logger.error(f"Error in test workflow: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 