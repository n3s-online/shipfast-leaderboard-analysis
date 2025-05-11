# Ship Fast Analysis

A sentiment analysis tool for evaluating marketing taglines and product descriptions. This project uses NLTK's VADER (Valence Aware Dictionary and sEntiment Reasoner) to analyze the sentiment of text data.

## Project Overview

This tool helps evaluate the emotional tone of marketing copy, product descriptions, or other text content. It categorizes text as positive, negative, or neutral based on sentiment analysis, which can be valuable for:

- Testing marketing messages before publication
- Analyzing competitor messaging
- Evaluating customer feedback
- Optimizing product descriptions

## Installation

### Prerequisites

- Python 3.6 or higher

### Setting up a Virtual Environment

It's recommended to use a virtual environment for this project:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Installing Dependencies

Once your virtual environment is activated, install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

### Sentiment Analysis

1. Prepare your data in one of two ways:
   - Place your text data in the `initial_data.txt` file (one statement per line), or
   - Create a `data.json` file with an array of objects containing a "headline" property

2. Run the sentiment analysis script:

```bash
python sentiment_analysis.py
```

3. View the results in the terminal output and check the updated JSON file:
   - The script will read from and write to `data.json`, adding sentiment analysis to each object:

```json
[
  {
    "headline": "Your text here",
    "sentiment_analysis": {
      "sentiment": "Positive|Negative|Neutral",
      "negative": 0.0,
      "neutral": 0.693,
      "positive": 0.307,
      "compound": 0.2732
    }
  },
  ...
]
```

Note: If `data.json` doesn't exist, the script will create it from `initial_data.txt`.

### Data Visualization

After running the sentiment analysis, you can generate visualizations:

1. Make sure you have the required visualization libraries installed:

```bash
pip install -r requirements.txt
```

2. Run the sentiment visualization script:

```bash
python visualize_sentiment_analysis.py
```

3. The script will generate several square PNG visualizations in the `visualizations` directory:
   - `sentiment_distribution.png` - Pie chart showing the distribution of sentiment categories
   - `compound_score_histogram.png` - Histogram of compound sentiment scores
   - `sentiment_components.png` - Bar chart of average positive, neutral, and negative scores
   - `sentiment_boxplot.png` - Box plot showing the distribution of compound scores
   - `most_positive_headlines.png` - Bar chart of the most positive headlines
   - `most_negative_headlines.png` - Bar chart of the most negative headlines

Note: The visualization script will throw an error if any object in `data.json` is missing sentiment analysis data.

### Word Cloud Generation

You can also generate a word cloud from the headlines:

1. Make sure you have the required libraries installed:

```bash
pip install -r requirements.txt
```

2. Run the word cloud script:

```bash
python generate_wordcloud.py
```

3. The script will generate a square PNG word cloud in the `visualizations` directory:
   - `headline_wordcloud.png` - Word cloud showing the most common words in the headlines

The script also prints the top 20 most common words found in the headlines.

### Fetching Headlines

You can fetch headlines for startups in the `startups.json` file:

1. Make sure you have the required libraries installed:

```bash
pip install -r requirements.txt
```

2. Set your OpenAI API key in one of two ways:

   a. Create a `.env` file in the project root (recommended):
   ```
   OPENAI_API_KEY=your-api-key
   ```

   b. Or set it as an environment variable:
   ```bash
   export OPENAI_API_KEY='your-api-key'
   ```

   Note: A `.env.example` file is provided as a template.

3. Run the headline fetching script:

```bash
python fetch-headlines.py
```

The script will:
- Process only entries in `startups.json` that don't have a headline field
- Try to extract headlines using web scraping (BeautifulSoup)
- If web scraping fails, use OpenAI to extract headlines
- Skip entries that already have headlines
- Save the updated data back to `startups.json`

Note: If the script encounters errors while fetching a headline, it will move on to the next startup.

## Project Structure

- `sentiment_analysis.py` - Main script for analyzing sentiment
- `visualize_sentiment_analysis.py` - Script for generating data visualizations
- `generate_wordcloud.py` - Script for generating a word cloud from headlines
- `fetch-headlines.py` - Script for fetching headlines from startup websites
- `initial_data.txt` - Input file containing text to analyze
- `data.json` - JSON file with headlines and sentiment analysis results
- `startups.json` - JSON file with startup data
- `.env.example` - Example environment variables file
- `visualizations/` - Directory containing generated visualization images
- `requirements.txt` - List of Python dependencies
- `README.md` - This documentation file

## Dependencies

- NLTK - Natural Language Toolkit for sentiment analysis
- Matplotlib - Data visualization library
- Seaborn - Statistical data visualization
- Pandas - Data manipulation and analysis
- WordCloud - Word cloud generator
- Requests - HTTP library for web scraping
- BeautifulSoup4 - HTML parsing library
- OpenAI - API client for OpenAI services
- tqdm - Progress bar library
- python-dotenv - Environment variable management

## License

[MIT License](LICENSE)
