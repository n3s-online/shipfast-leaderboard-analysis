#!/usr/bin/env python3
"""
Generate a word cloud from headlines in data.json.
Creates a square PNG image with the most common words in the headlines.
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
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'headline_wordcloud.png')

# Define additional stopwords (common words to exclude)
ADDITIONAL_STOPWORDS = {
    'get', 'with', 'without', 'using', 'use', 'used', 'uses',
    'and', 'the', 'for', 'your', 'you', 'our', 'we', 'their',
    'in', 'on', 'at', 'to', 'from', 'of', 'by', 'a', 'an',
    'any', 'all', 'more', 'most', 'some', 'that', 'this', 'these', 'those',
    'it', 'its', 'it\'s', 'they', 'them', 'their', 'theirs',
    'as', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
    'can', 'could', 'will', 'would', 'should', 'shall', 'may', 'might',
    'must', 'ought', 'i', 'me', 'my', 'mine', 'myself',
    'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
    'we', 'us', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
    'yourself', 'yourselves', 'they', 'them', 'their', 'theirs', 'themselves',
    'what', 'which', 'who', 'whom', 'whose', 'when', 'where', 'why', 'how',
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
    'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
    'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to',
    'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
    'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
    'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
    'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
    's', 't', 'just', 'don', 'don\'t', 'now', 'd', 'll', 'm', 'o', 're',
    've', 'y', 'ain', 'aren', 'aren\'t', 'couldn', 'couldn\'t', 'didn',
    'didn\'t', 'doesn', 'doesn\'t', 'hadn', 'hadn\'t', 'hasn', 'hasn\'t',
    'haven', 'haven\'t', 'isn', 'isn\'t', 'ma', 'mightn', 'mightn\'t', 'mustn',
    'mustn\'t', 'needn', 'needn\'t', 'shan', 'shan\'t', 'shouldn', 'shouldn\'t',
    'wasn', 'wasn\'t', 'weren', 'weren\'t', 'won', 'won\'t', 'wouldn', 'wouldn\'t'
}

def load_data():
    """Load data from data.json and validate it has headlines."""
    try:
        with open('data.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        sys.exit("Error: data.json file not found.")
    except json.JSONDecodeError:
        sys.exit("Error: data.json is not a valid JSON file.")
    
    # Validate that all entries have headlines
    for i, item in enumerate(data):
        if 'headline' not in item:
            sys.exit(f"Error: Item at index {i} is missing the 'headline' field.")
    
    return data

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

def main():
    """Main function to generate the word cloud."""
    print("Loading data...")
    data = load_data()
    
    print("Extracting headlines...")
    headlines = [item['headline'] for item in data]
    
    print(f"Generating word cloud from {len(headlines)} headlines...")
    generate_wordcloud(headlines)

if __name__ == "__main__":
    main()
