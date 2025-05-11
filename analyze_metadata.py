#!/usr/bin/env python3
"""
Analyze the metadata in startups.json and generate statistics.
"""

import json
import sys
import matplotlib.pyplot as plt
import os
from collections import Counter

# Create output directory if it doesn't exist
OUTPUT_DIR = 'visualizations/metadata'
os.makedirs(OUTPUT_DIR, exist_ok=True)

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

def analyze_metadata(data):
    """Analyze the metadata in the data."""
    # Filter for items with headlines
    items_with_headlines = [item for item in data if 'headline' in item]
    print(f"Found {len(items_with_headlines)} items with headlines")

    # Filter for English items
    english_items = [item for item in items_with_headlines if item.get('language') == 'English']
    print(f"Found {len(english_items)} English items")

    # Count phrase types
    phrase_types = Counter([item.get('phraseType', 'unknown') for item in english_items])
    print("\nPhrase Types:")
    for phrase_type, count in phrase_types.items():
        print(f"  {phrase_type}: {count} ({count/len(english_items)*100:.1f}%)")

    # Count focus types
    focus_types = Counter([item.get('focus', 'unknown') for item in english_items])
    print("\nFocus Types:")
    for focus_type, count in focus_types.items():
        print(f"  {focus_type}: {count} ({count/len(english_items)*100:.1f}%)")

    # Count items with stats
    items_with_stats = [item for item in english_items if item.get('usesStats', False)]
    print(f"\nItems with stats: {len(items_with_stats)} ({len(items_with_stats)/len(english_items)*100:.1f}%)")

    # Count benefit keywords (case insensitive)
    all_benefit_keywords = []
    for item in english_items:
        # Convert all keywords to lowercase for case-insensitive counting
        all_benefit_keywords.extend([keyword.lower() for keyword in item.get('benefitKeywords', [])])

    benefit_keywords_counter = Counter(all_benefit_keywords)
    print("\nTop 10 Benefit Keywords (case insensitive):")
    for keyword, count in benefit_keywords_counter.most_common(10):
        print(f"  {keyword}: {count}")

    # Count action verbs (case insensitive)
    all_action_verbs = []
    for item in english_items:
        # Convert all verbs to lowercase for case-insensitive counting
        all_action_verbs.extend([verb.lower() for verb in item.get('actionVerbs', [])])

    action_verbs_counter = Counter(all_action_verbs)
    print("\nTop 10 Action Verbs (case insensitive):")
    for verb, count in action_verbs_counter.most_common(10):
        print(f"  {verb}: {count}")

    # Generate visualizations
    generate_visualizations(english_items, benefit_keywords_counter, action_verbs_counter, phrase_types, focus_types)

def generate_visualizations(english_items, benefit_keywords_counter, action_verbs_counter, phrase_types, focus_types):
    """Generate visualizations of the metadata."""
    # Create a pie chart of phrase types
    plt.figure(figsize=(10, 6))
    plt.pie(phrase_types.values(), labels=phrase_types.keys(), autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('Phrase Types')
    plt.savefig(os.path.join(OUTPUT_DIR, 'phrase_types.png'))
    plt.close()

    # Create a pie chart of focus types
    plt.figure(figsize=(10, 6))
    plt.pie(focus_types.values(), labels=focus_types.keys(), autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('Focus Types')
    plt.savefig(os.path.join(OUTPUT_DIR, 'focus_types.png'))
    plt.close()

    # Create a bar chart of top benefit keywords
    plt.figure(figsize=(12, 8))
    top_keywords = dict(benefit_keywords_counter.most_common(15))
    plt.bar(top_keywords.keys(), top_keywords.values())
    plt.xticks(rotation=45, ha='right')
    plt.title('Top 15 Benefit Keywords (Case Insensitive)')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'top_benefit_keywords.png'))
    plt.close()

    # Create a bar chart of top action verbs
    plt.figure(figsize=(12, 8))
    top_verbs = dict(action_verbs_counter.most_common(15))
    plt.bar(top_verbs.keys(), top_verbs.values())
    plt.xticks(rotation=45, ha='right')
    plt.title('Top 15 Action Verbs (Case Insensitive)')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'top_action_verbs.png'))
    plt.close()

    # Create a bar chart of items with stats by revenue
    items_with_stats = [item for item in english_items if item.get('usesStats', False)]
    items_without_stats = [item for item in english_items if not item.get('usesStats', False)]

    avg_revenue_with_stats = sum(item.get('revenue', 0) for item in items_with_stats) / len(items_with_stats) if items_with_stats else 0
    avg_revenue_without_stats = sum(item.get('revenue', 0) for item in items_without_stats) / len(items_without_stats) if items_without_stats else 0

    plt.figure(figsize=(10, 6))
    plt.bar(['With Stats', 'Without Stats'], [avg_revenue_with_stats, avg_revenue_without_stats])
    plt.title('Average Revenue by Use of Stats')
    plt.ylabel('Average Revenue ($)')
    plt.savefig(os.path.join(OUTPUT_DIR, 'revenue_by_stats.png'))
    plt.close()

    print(f"\nVisualizations saved to {OUTPUT_DIR}")

def main():
    """Main function."""
    data = load_data()
    analyze_metadata(data)

if __name__ == "__main__":
    main()
