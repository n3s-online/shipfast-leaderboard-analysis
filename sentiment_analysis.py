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
    json_file_path = 'data.json'

    # Check if data.json exists, if not, create it from initial_data.txt
    if not os.path.exists(json_file_path):
        print(f"{json_file_path} not found. Creating it from initial_data.txt...")
        data = []

        # Read the file line by line
        with open('initial_data.txt', 'r') as file:
            for line in file:
                line = line.strip()
                if not line:  # Skip empty lines
                    continue

                # Add each line as an object with headline property
                data.append({"headline": line})

        # Save initial data to JSON file
        with open(json_file_path, 'w') as json_file:
            json.dump(data, json_file, indent=2)

    # Read the existing data from data.json
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)

    # Process each item in the data
    for i, item in enumerate(data):
        headline = item.get('headline', '')
        if not headline:
            print(f"Warning: Item {i+1} has no headline. Skipping...")
            continue

        # Analyze sentiment
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
        print(f"Item {i+1}: {headline}")
        print(f"Sentiment: {sentiment}")
        print(f"Scores: {scores}")
        print("-" * 50)

    # Save updated data back to data.json
    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=2)

    print(f"\nResults saved to {json_file_path}")

if __name__ == "__main__":
    main()