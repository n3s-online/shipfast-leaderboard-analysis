#!/usr/bin/env python3
"""
Generate a word cloud from English headlines in startups.json.
Creates a square PNG image with the most common words in the English headlines.
"""

import json
import os
import sys
import re
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from collections import Counter

# Create output directory if it doesn't exist
OUTPUT_DIR = 'visualizations'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Output file path
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'english_headline_wordcloud.png')

# Define additional stopwords (common words to exclude)
ADDITIONAL_STOPWORDS = {
}

def load_data():
    """Load data from startups.json and filter for English headlines."""
    try:
        with open('startups.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        sys.exit("Error: startups.json file not found.")
    except json.JSONDecodeError:
        sys.exit("Error: startups.json is not a valid JSON file.")

    # Filter for English-only startups with headlines
    english_startups = []
    for item in data:
        if 'headline' in item and 'language' in item and item['language'] == 'English':
            english_startups.append(item)

    if not english_startups:
        sys.exit("Error: No English startups with headlines found.")

    return english_startups

def preprocess_text(text):
    """Preprocess text by removing special characters and converting to lowercase."""
    # Convert to lowercase
    text = text.lower()

    # Remove special characters and numbers
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)

    return text

def generate_wordcloud(headlines):
    """Generate a word cloud from the headlines."""
    # Combine all headlines into a single text
    all_text = ' '.join([preprocess_text(headline) for headline in headlines])

    # Create a set of stopwords by combining the default stopwords with additional ones
    stopwords = set(STOPWORDS).union(ADDITIONAL_STOPWORDS)

    # Create a word cloud
    wordcloud = WordCloud(
        width=1000,
        height=1000,
        background_color='white',
        stopwords=stopwords,
        min_font_size=10,
        max_font_size=150,
        colormap='viridis',
        random_state=42,
        collocations=False,  # Don't include bigrams
        contour_width=1,
        contour_color='steelblue'
    ).generate(all_text)

    # Create a figure
    plt.figure(figsize=(10, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)

    # Save the figure
    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Word cloud saved to {OUTPUT_FILE}")

    # Print the top 20 most common words
    words = all_text.split()
    word_counts = Counter(word for word in words if word.lower() not in stopwords)
    print("\nTop 20 most common words:")
    for word, count in word_counts.most_common(20):
        print(f"{word}: {count}")

    # Print all words that appear 2 or more times
    words_with_2_plus = [(word, count) for word, count in word_counts.items() if count >= 2]
    words_with_2_plus.sort(key=lambda x: x[1], reverse=True)  # Sort by count (descending)

    print(f"\nAll words appearing 2 or more times ({len(words_with_2_plus)} words):")
    for word, count in words_with_2_plus:
        print(f"{word}: {count}")

def main():
    """Main function to generate the word cloud."""
    print("Loading data from startups.json...")
    data = load_data()

    print("Extracting English headlines...")
    headlines = [item['headline'] for item in data]

    print(f"Generating word cloud from {len(headlines)} English headlines...")
    generate_wordcloud(headlines)

    # Print some statistics
    total_startups = len(data)
    print(f"\nTotal English startups with headlines: {total_startups}")

    # Count startups by revenue range
    revenue_ranges = {
        "0-1K": 0,
        "1K-5K": 0,
        "5K-10K": 0,
        "10K-50K": 0,
        "50K-100K": 0,
        "100K+": 0
    }

    for startup in data:
        revenue = startup.get('revenue', 0)
        if revenue < 1000:
            revenue_ranges["0-1K"] += 1
        elif revenue < 5000:
            revenue_ranges["1K-5K"] += 1
        elif revenue < 10000:
            revenue_ranges["5K-10K"] += 1
        elif revenue < 50000:
            revenue_ranges["10K-50K"] += 1
        elif revenue < 100000:
            revenue_ranges["50K-100K"] += 1
        else:
            revenue_ranges["100K+"] += 1

    print("\nEnglish startups by revenue range:")
    for range_name, count in revenue_ranges.items():
        print(f"{range_name}: {count} startups")

if __name__ == "__main__":
    main()
