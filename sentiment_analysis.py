import nltk
import json
import os
from nltk.sentiment import SentimentIntensityAnalyzer

# Download required NLTK data packages
nltk.download('vader_lexicon', quiet=True)

def analyze_sentiment(text):
    """Analyze the sentiment of the given text using NLTK's VADER."""
    sia = SentimentIntensityAnalyzer()
    sentiment_scores = sia.polarity_scores(text)

    # Determine sentiment category based on compound score
    if sentiment_scores['compound'] >= 0.05:
        sentiment = 'Positive'
    elif sentiment_scores['compound'] <= -0.05:
        sentiment = 'Negative'
    else:
        sentiment = 'Neutral'

    return sentiment, sentiment_scores

def main():
    json_file_path = 'startups.json'

    # Read the existing data from startups.json
    try:
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
        print(f"Loaded {len(data)} startups from {json_file_path}")
    except FileNotFoundError:
        print(f"Error: {json_file_path} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: {json_file_path} is not a valid JSON file.")
        return

    # Process each item in the data
    processed_count = 0
    skipped_count = 0
    english_count = 0
    non_english_count = 0
    removed_count = 0

    for i, item in enumerate(data):
        headline = item.get('headline', '')
        if not headline:
            print(f"Warning: Item {i+1} ({item.get('startup', 'Unknown')}) has no headline. Skipping...")
            skipped_count += 1

            # Remove sentiment_analysis if it exists
            if 'sentiment_analysis' in item:
                del item['sentiment_analysis']
                removed_count += 1

            continue

        # Check if the language is English
        language = item.get('language', 'Unknown')

        if language != 'English':
            print(f"Item {i+1} ({item.get('startup', 'Unknown')}): Non-English headline ({language}). Skipping sentiment analysis.")
            non_english_count += 1

            # Remove sentiment_analysis if it exists
            if 'sentiment_analysis' in item:
                del item['sentiment_analysis']
                removed_count += 1

            continue

        # Analyze sentiment for English headlines
        sentiment, scores = analyze_sentiment(headline)

        # Add or update sentiment_analysis to the existing object
        item['sentiment_analysis'] = {
            "sentiment": sentiment,
            "negative": scores['neg'],
            "neutral": scores['neu'],
            "positive": scores['pos'],
            "compound": scores['compound']
        }

        # Print results to console
        print(f"Item {i+1} ({item.get('startup', 'Unknown')}) [English]: {headline}")
        print(f"Sentiment: {sentiment}")
        print(f"Scores: {scores}")
        print("-" * 50)

        processed_count += 1
        english_count += 1

    # Save updated data back to startups.json
    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=2)

    print(f"\nSummary:")
    print(f"- Processed {english_count} English headlines with sentiment analysis")
    print(f"- Skipped {skipped_count} items without headlines")
    print(f"- Skipped {non_english_count} non-English headlines")
    print(f"- Removed sentiment analysis from {removed_count} non-English items")
    print(f"- Total items: {len(data)}")
    print(f"\nResults saved to {json_file_path}")

if __name__ == "__main__":
    main()