#!/usr/bin/env python3
"""
Analyze headline word length in startups.json and generate statistics.
"""

import json
import sys
import os
from collections import Counter
import statistics

def load_data():
    """Load data from startups.json."""
    try:
        with open('startups.json', 'r') as file:
            data = json.load(file)
        print(f"Loaded {len(data)} startups from startups.json")
    except FileNotFoundError:
        sys.exit("Error: startups.json file not found.")
    except json.JSONDecodeError:
        sys.exit("Error: startups.json is not a valid JSON file.")

    return data

def count_words(headline):
    """Count words in a headline, excluding punctuation."""
    if not headline:
        return 0
    
    # Simple word counting - split by whitespace and filter out empty strings
    words = [word.strip('.,!?;:"()[]{}') for word in headline.split()]
    words = [word for word in words if word]  # Remove empty strings
    return len(words)

def analyze_word_length(data):
    """Analyze word length statistics for headlines."""
    # Filter for items with headlines
    items_with_headlines = [item for item in data if 'headline' in item and item['headline']]
    print(f"Found {len(items_with_headlines)} items with headlines")

    if not items_with_headlines:
        print("No headlines found to analyze.")
        return

    # Calculate word counts for all headlines
    word_counts = [count_words(item['headline']) for item in items_with_headlines]
    
    # Filter for English items
    english_items = [item for item in items_with_headlines if item.get('language') == 'English']
    english_word_counts = [count_words(item['headline']) for item in english_items]
    
    print(f"Found {len(english_items)} English items with headlines")

    # Overall statistics
    print("\n=== ALL HEADLINES ===")
    print_word_length_stats(word_counts, items_with_headlines)
    
    if english_word_counts:
        print("\n=== ENGLISH HEADLINES ONLY ===")
        print_word_length_stats(english_word_counts, english_items)
        
        # Analyze by revenue ranges
        analyze_by_revenue_ranges(english_items)
        
        # Analyze by sentiment
        analyze_by_sentiment(english_items)
        
        # Show examples
        show_examples(english_items)

def print_word_length_stats(word_counts, items):
    """Print statistical summary of word lengths."""
    if not word_counts:
        print("No word counts to analyze.")
        return
        
    print(f"Total headlines: {len(word_counts)}")
    print(f"Mean word count: {statistics.mean(word_counts):.2f}")
    print(f"Median word count: {statistics.median(word_counts):.2f}")
    print(f"Mode word count: {statistics.mode(word_counts)}")
    print(f"Min word count: {min(word_counts)}")
    print(f"Max word count: {max(word_counts)}")
    print(f"Standard deviation: {statistics.stdev(word_counts):.2f}")
    
    # Word count distribution
    word_count_distribution = Counter(word_counts)
    print("\nWord count distribution:")
    for count in sorted(word_count_distribution.keys()):
        percentage = (word_count_distribution[count] / len(word_counts)) * 100
        print(f"  {count} words: {word_count_distribution[count]} headlines ({percentage:.1f}%)")

def analyze_by_revenue_ranges(english_items):
    """Analyze word length by revenue ranges."""
    print("\n=== ANALYSIS BY REVENUE RANGES ===")
    
    # Define revenue ranges
    ranges = [
        (0, 50000, "Low ($0-$50k)"),
        (50000, 150000, "Medium ($50k-$150k)"),
        (150000, float('inf'), "High ($150k+)")
    ]
    
    for min_rev, max_rev, label in ranges:
        items_in_range = [
            item for item in english_items 
            if min_rev <= item.get('revenue', 0) < max_rev
        ]
        
        if items_in_range:
            word_counts = [count_words(item['headline']) for item in items_in_range]
            avg_words = statistics.mean(word_counts)
            print(f"{label}: {len(items_in_range)} items, avg {avg_words:.2f} words")

def analyze_by_sentiment(english_items):
    """Analyze word length by sentiment."""
    print("\n=== ANALYSIS BY SENTIMENT ===")
    
    items_with_sentiment = [
        item for item in english_items 
        if 'sentiment_analysis' in item
    ]
    
    if not items_with_sentiment:
        print("No sentiment analysis data found.")
        return
    
    sentiment_groups = {}
    for item in items_with_sentiment:
        sentiment = item['sentiment_analysis']['sentiment']
        if sentiment not in sentiment_groups:
            sentiment_groups[sentiment] = []
        sentiment_groups[sentiment].append(count_words(item['headline']))
    
    for sentiment, word_counts in sentiment_groups.items():
        if word_counts:
            avg_words = statistics.mean(word_counts)
            print(f"{sentiment}: {len(word_counts)} items, avg {avg_words:.2f} words")

def show_examples(english_items):
    """Show examples of headlines by word count."""
    print("\n=== EXAMPLES BY WORD COUNT ===")
    
    # Group headlines by word count
    by_word_count = {}
    for item in english_items:
        word_count = count_words(item['headline'])
        if word_count not in by_word_count:
            by_word_count[word_count] = []
        by_word_count[word_count].append(item)
    
    # Show examples for interesting word counts
    interesting_counts = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15]
    
    for count in interesting_counts:
        if count in by_word_count:
            examples = by_word_count[count][:3]  # Show up to 3 examples
            print(f"\n{count} words ({len(by_word_count[count])} total):")
            for item in examples:
                revenue = item.get('revenue', 0)
                print(f"  \"{item['headline']}\" (${revenue:,})")

def main():
    """Main function."""
    data = load_data()
    analyze_word_length(data)

if __name__ == "__main__":
    main() 