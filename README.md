# AI Alignment Digest Generator

A minimal AI alignment forum aggregator that scrapes public AI alignment sources, summarizes recent posts daily, and outputs a concise digest.

## Features

- Scrapes posts from:
  - Alignment Forum (alignmentforum.org)
  - LessWrong (lesswrong.com)
- Generates concise summaries using DeepSeek's AI models
- Creates daily digests in markdown format
- Automatically runs daily at 00:00 UTC
- Stores historical digests and maintains a latest digest

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-alignment-digest.git
cd ai-alignment-digest
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your DeepSeek API key:
```
DEEPSEEK_API_KEY=your_api_key_here
```

## Usage

To start the digest generator:

```bash
python src/main.py
```

The script will:
1. Generate a digest immediately upon starting
2. Schedule future digests to run daily at 00:00 UTC
3. Save digests to `data/digests/` directory
   - Daily digests are saved as `digest_YYYY-MM-DD.md`
   - The most recent digest is also saved as `latest.md`

## Output Format

The digest is formatted in markdown and includes:
- Date of generation
- Sections for each source (Alignment Forum, LessWrong)
- For each post:
  - Title (with link)
  - Author
  - Publication date/time
  - Concise summary
  - Separator between posts

## Dependencies

- Python 3.8+
- DeepSeek API access
- See `requirements.txt` for full list of dependencies

## Contributing

Feel free to open issues or submit pull requests for improvements or bug fixes.

## License

MIT License - feel free to use and modify as needed. 