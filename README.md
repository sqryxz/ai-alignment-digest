# AI Alignment Digest

A tool for aggregating and summarizing posts from AI alignment forums (LessWrong and Alignment Forum).

## Overview

This project scrapes and processes posts from major AI alignment discussion forums, creating structured JSON output with summaries and key topics. It helps track and analyze discussions in the AI alignment community.

## Features

- Fetches posts from LessWrong and Alignment Forum
- Processes and structures content with metadata
- Generates summaries of key topics and themes
- Preserves original formatting and links
- Includes metadata like publication date, author, and source

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-alignment-digest.git
cd ai-alignment-digest
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the scraper:
```bash
python scraper.py
```

The script will generate a `sample_posts.json` file containing the processed posts.

## Output Format

The output JSON file has the following structure:

```json
{
  "fetch_time": "2025-03-12T13:07:18.299038",
  "summary": {
    "date_range": "March 11-12, 2025",
    "key_topics": [
      {
        "name": "AI Safety & Alignment",
        "key_points": [
          "New 'waystations' framework for AI alignment",
          "Monitoring AI reasoning and detecting misbehavior",
          "Analysis of security factors in AI development"
        ],
        "key_posts": [
          "https://www.alignmentforum.org/posts/kBgySGcASWa4FWdD9/paths-and-waystations-in-ai-safety-1",
          "https://www.alignmentforum.org/posts/7wFdXj9oR8M9AiFht/openai-detecting-misbehavior-in-frontier-reasoning-models"
        ]
      },
      {
        "name": "Technical Research",
        "key_points": [
          "Analysis of AI reasoning models and scratchpads",
          "Investigation of encoded reasoning in language models",
          "Model interpretability studies"
        ]
      }
    ]
  },
  "total_posts": 14,
  "posts": [
    {
      "title": "Example Post Title",
      "url": "https://example.com/post",
      "author": "Author Name",
      "content": "Post content...",
      "published_date": "2025-03-11T18:52:57+00:00",
      "source": "LessWrong"
    }
  ]
}
```

## Sample Output

Here's a real example of processed posts from March 11-12, 2025:

### Key Topics Covered

1. **AI Safety Strategy & Theory**
   - New 'waystations' framework for approaching AI alignment
   - Analysis of civilizational competence regarding AI risks
   - Discussion of security factors in AI development

2. **Technical Research & Monitoring**
   - Investigation of reasoning models' use of scratchpads
   - Detection of misbehavior in frontier AI models
   - Analysis of encoded reasoning in language models

3. **Policy & Governance**
   - Analysis of evidence-based approaches to AI safety
   - Discussion of coordination mechanisms
   - Institutional developments in AI safety research

### Notable Posts

1. "Paths and waystations in AI safety" by Joe Carlsmith
   - Introduces framework for addressing AI alignment
   - Analyzes security factors and competence profiles
   - Discusses potential intermediate milestones

2. "OpenAI: Detecting Misbehavior in Frontier Reasoning Models"
   - Documents instances of reward hacking
   - Analyzes effectiveness of monitoring strategies
   - Provides recommendations for model oversight

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 