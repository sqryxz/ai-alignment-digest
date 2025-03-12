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
    "overview": "Recent discussions in the AI alignment community have focused on three main areas: AI safety strategy and theory, technical research and monitoring, and policy considerations. The discourse has been particularly active around new frameworks for understanding AI alignment progress and novel approaches to detecting and preventing problematic AI behaviors.",
    "key_topics": [
      {
        "name": "AI Safety & Alignment",
        "summary": "A significant development in AI alignment theory has emerged with the introduction of the 'waystations' framework, which provides a new approach to understanding and measuring progress in AI safety. This framework emphasizes the importance of civilizational competence in managing AI risks and introduces several key security factors that need to be considered. The community has also made progress in monitoring AI systems and detecting potential misbehavior, with new research showing both promising results and concerning challenges.",
        "key_posts": [
          "https://www.alignmentforum.org/posts/kBgySGcASWa4FWdD9/paths-and-waystations-in-ai-safety-1",
          "https://www.alignmentforum.org/posts/7wFdXj9oR8M9AiFht/openai-detecting-misbehavior-in-frontier-reasoning-models"
        ]
      },
      {
        "name": "Technical Research",
        "summary": "Recent technical research has focused on understanding how AI models process information and make decisions. Particularly noteworthy is the investigation into how reasoning models use their scratchpads, with new evidence suggesting interesting patterns in how these models approach problem-solving. Additionally, researchers have made progress in studying encoded reasoning in language models and advancing model interpretability techniques."
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

Here's a real example of processed posts from March 12, 2025:

```markdown
# AI Alignment Daily Digest - March 12, 2025

## Overview

Recently, AI safety researchers have been talking about important ideas like how to make AI systems safer while still allowing them to learn and develop properly. They're discussing the balance between control and natural safety, kind of like how we need to find the right balance between protecting kids and letting them learn from experience.

## Key Topics

### Making AI Safe & Aligned

This post talks about how we need to balance control and safety when developing AI. It's like finding the right way to teach good behavior rather than just using strict rules.

**Key Posts:**
- [Paths and waystations in AI safety](https://www.alignmentforum.org/posts/kBgySGcASWa4FWdD9/paths-and-waystations-in-ai-safety-1) by Joe Carlsmith
- [AI Control May Increase Existential Risk](https://www.alignmentforum.org/posts/rZcyemEpBHgb2hqLP/ai-control-may-increase-existential-risk) by Jan_Kulveit

## Notable Posts

### [Paths and waystations in AI safety](https://www.alignmentforum.org/posts/kBgySGcASWa4FWdD9/paths-and-waystations-in-ai-safety-1)
**Author:** Joe Carlsmith  
**Published:** 2025-03-11 18:52 UTC  
**Source:** Alignment Forum

### [AI Control May Increase Existential Risk](https://www.alignmentforum.org/posts/rZcyemEpBHgb2hqLP/ai-control-may-increase-existential-risk)
**Author:** Jan_Kulveit  
**Published:** 2025-03-11 14:30 UTC  
**Source:** Alignment Forum

### [Do reasoning models use their scratchpad like we do?](https://www.alignmentforum.org/posts/ywzLszRuGRDpabjCk/do-reasoning-models-use-their-scratchpad-like-we-do-evidence)
**Author:** Fabien Roger  
**Published:** 2025-03-11 11:52 UTC  
**Source:** Alignment Forum
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 