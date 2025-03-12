# AI Alignment Daily Digest

A Python script that generates daily digests of AI alignment-related posts. The script processes posts from various sources, categorizes them by topic, identifies key themes, and creates a well-organized digest.

## Features

- Processes posts from multiple sources (currently supporting JSON input)
- Categorizes posts into topics based on content analysis
- Identifies key themes across all posts using weighted keyword matching
- Generates summaries of post content
- Shows cross-references between categories
- Sorts posts by date and relevance
- Maintains a record of processed posts to avoid duplicates

## Usage

1. Prepare your posts in JSON format:
```json
{
    "fetch_time": "2025-03-13T00:16:29.895598",
    "total_posts": 14,
    "posts": [
        {
            "title": "Post Title",
            "url": "https://example.com/post",
            "author": "Author Name",
            "content": "Post content...",
            "published_date": "2025-03-12T15:24:47+00:00",
            "source": "Source Name"
        }
    ]
}
```

2. Run the script:
```bash
python summarizer.py
```

The script will generate a digest file named `digest_YYYY-MM-DD.txt` containing:
- Overview of posts and topics
- Key themes with descriptions and example posts
- Detailed posts organized by category
- Cross-references between categories

## Requirements

- Python 3.6+
- No external dependencies required

## Configuration

The script includes configurable parameters:
- `max_words`: Maximum words in post summaries (default: 75)
- `days_lookback`: Number of days to look back for posts (default: 1)

Topic keywords and theme detection can be customized by modifying the respective dictionaries in the code. 