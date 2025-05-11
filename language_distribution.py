#!/usr/bin/env python3
"""
Generate a pie chart showing the distribution of languages in startups.json.
"""

import json
import os
import sys
import matplotlib.pyplot as plt
from collections import Counter

# Create output directory if it doesn't exist
OUTPUT_DIR = 'visualizations'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Output file path
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'language_distribution.png')

def load_data():
    """Load data from startups.json."""
    try:
        with open('startups.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        sys.exit("Error: startups.json file not found.")
    except json.JSONDecodeError:
        sys.exit("Error: startups.json is not a valid JSON file.")
    
    return data

def generate_language_pie_chart(data):
    """Generate a pie chart showing the distribution of languages."""
    # Count languages
    languages = [item.get('language', 'Unknown') for item in data]
    language_counts = Counter(languages)
    
    # Sort by count (descending)
    sorted_languages = sorted(language_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Separate small slices (less than 2%) into 'Other'
    total_count = len(languages)
    threshold = total_count * 0.02  # 2% threshold
    
    main_languages = []
    main_counts = []
    other_count = 0
    
    for language, count in sorted_languages:
        if count >= threshold:
            main_languages.append(language)
            main_counts.append(count)
        else:
            other_count += count
    
    if other_count > 0:
        main_languages.append('Other')
        main_counts.append(other_count)
    
    # Create a pie chart
    plt.figure(figsize=(10, 8))
    
    # Use a colorful color map
    colors = plt.cm.tab10.colors
    
    # Create the pie chart
    wedges, texts, autotexts = plt.pie(
        main_counts, 
        labels=main_languages,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        shadow=True,
        wedgeprops={'edgecolor': 'w', 'linewidth': 1}
    )
    
    # Style the percentage text
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(12)
        autotext.set_fontweight('bold')
    
    # Equal aspect ratio ensures that pie is drawn as a circle
    plt.axis('equal')
    
    # Add a title
    plt.title('Language Distribution of Startup Headlines', fontsize=16, fontweight='bold')
    
    # Add a legend with counts
    legend_labels = [f"{language} ({count})" for language, count in zip(main_languages, main_counts)]
    plt.legend(wedges, legend_labels, title="Languages", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Language distribution pie chart saved to {OUTPUT_FILE}")
    
    # Print language statistics
    print("\nLanguage distribution:")
    for language, count in sorted_languages:
        percentage = (count / total_count) * 100
        print(f"{language}: {count} startups ({percentage:.1f}%)")

def main():
    """Main function to generate the language distribution pie chart."""
    print("Loading data from startups.json...")
    data = load_data()
    
    print("Generating language distribution pie chart...")
    generate_language_pie_chart(data)
    
    # Print some statistics
    total_startups = len(data)
    startups_with_headlines = sum(1 for item in data if 'headline' in item)
    startups_without_headlines = total_startups - startups_with_headlines
    
    print(f"\nTotal startups: {total_startups}")
    print(f"Startups with headlines: {startups_with_headlines} ({(startups_with_headlines / total_startups) * 100:.1f}%)")
    print(f"Startups without headlines: {startups_without_headlines} ({(startups_without_headlines / total_startups) * 100:.1f}%)")

if __name__ == "__main__":
    main()
