#!/usr/bin/env python3
"""
Visualize headline word length data from startups.json.
Generates multiple visualizations as PNG files.
"""

import json
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter
import statistics

# Set the style for all plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set(font_scale=1.2)

# Create output directory if it doesn't exist
OUTPUT_DIR = 'visualizations/word_length'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_data():
    """Load data from startups.json."""
    try:
        with open('startups.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        sys.exit("Error: startups.json file not found.")
    except json.JSONDecodeError:
        sys.exit("Error: startups.json is not a valid JSON file.")

    # Filter for items with headlines
    filtered_data = [item for item in data if 'headline' in item and item['headline']]
    
    if not filtered_data:
        sys.exit("Error: No items with headlines found.")

    print(f"Found {len(filtered_data)} items with headlines")
    return filtered_data

def count_words(headline):
    """Count words in a headline, excluding punctuation."""
    if not headline:
        return 0
    
    # Simple word counting - split by whitespace and filter out empty strings
    words = [word.strip('.,!?;:"()[]{}') for word in headline.split()]
    words = [word for word in words if word]  # Remove empty strings
    return len(words)

def create_dataframe(data, english_only=True):
    """Convert JSON data to a pandas DataFrame for easier analysis."""
    # Filter for English-only if requested
    if english_only:
        filtered_data = [
            item for item in data
            if 'language' in item and item['language'] == 'English'
        ]
        print(f"Filtered to {len(filtered_data)} English headlines")
    else:
        filtered_data = data

    # Convert to DataFrame
    df = pd.DataFrame([
        {
            'headline': item['headline'],
            'startup': item.get('startup', 'Unknown'),
            'revenue': item.get('revenue', 0),
            'language': item.get('language', 'Unknown'),
            'word_count': count_words(item['headline']),
            'sentiment': item.get('sentiment_analysis', {}).get('sentiment', 'Unknown') if 'sentiment_analysis' in item else 'Unknown',
            'compound_score': item.get('sentiment_analysis', {}).get('compound', 0) if 'sentiment_analysis' in item else 0
        }
        for item in filtered_data
    ])

    return df

def save_plot(fig, filename):
    """Save the figure as a PNG."""
    fig.set_size_inches(12, 8)
    plt.tight_layout()

    filepath = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {filepath}")

def plot_word_count_distribution(df):
    """Create a histogram of word count distribution."""
    fig, ax = plt.subplots()

    # Create histogram
    word_counts = df['word_count'].values
    bins = range(1, max(word_counts) + 2)  # From 1 to max+1
    
    ax.hist(word_counts, bins=bins, edgecolor='white', linewidth=1.5, alpha=0.7, color='skyblue')
    
    # Add mean and median lines
    mean_words = np.mean(word_counts)
    median_words = np.median(word_counts)
    
    ax.axvline(mean_words, color='red', linestyle='--', linewidth=2, alpha=0.8, label=f'Mean: {mean_words:.1f}')
    ax.axvline(median_words, color='orange', linestyle='--', linewidth=2, alpha=0.8, label=f'Median: {median_words:.1f}')
    
    ax.set_xlabel('Number of Words in Headline', fontsize=14)
    ax.set_ylabel('Number of Headlines', fontsize=14)
    ax.set_title('Distribution of Headline Word Counts', fontsize=16, pad=20)
    ax.legend()
    
    # Set integer ticks on x-axis
    ax.set_xticks(range(1, max(word_counts) + 1))
    
    save_plot(fig, 'word_count_distribution.png')

def plot_word_count_by_revenue(df):
    """Create a scatter plot of word count vs revenue."""
    fig, ax = plt.subplots()

    # Create scatter plot
    scatter = ax.scatter(df['word_count'], df['revenue'], alpha=0.6, s=50, c='steelblue')
    
    # Add trend line
    z = np.polyfit(df['word_count'], df['revenue'], 1)
    p = np.poly1d(z)
    ax.plot(df['word_count'], p(df['word_count']), "r--", alpha=0.8, linewidth=2)
    
    # Calculate correlation
    correlation = df['word_count'].corr(df['revenue'])
    
    ax.set_xlabel('Number of Words in Headline', fontsize=14)
    ax.set_ylabel('Revenue ($)', fontsize=14)
    ax.set_title(f'Headline Word Count vs Revenue (r={correlation:.3f})', fontsize=16, pad=20)
    
    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    save_plot(fig, 'word_count_vs_revenue.png')

def plot_word_count_by_revenue_ranges(df):
    """Create a box plot of word count by revenue ranges."""
    fig, ax = plt.subplots()

    # Define revenue ranges
    df['revenue_range'] = pd.cut(df['revenue'], 
                                bins=[0, 50000, 150000, float('inf')], 
                                labels=['Low ($0-$50k)', 'Medium ($50k-$150k)', 'High ($150k+)'])
    
    # Create box plot
    sns.boxplot(data=df, x='revenue_range', y='word_count', ax=ax)
    
    ax.set_xlabel('Revenue Range', fontsize=14)
    ax.set_ylabel('Number of Words in Headline', fontsize=14)
    ax.set_title('Headline Word Count by Revenue Range', fontsize=16, pad=20)
    
    save_plot(fig, 'word_count_by_revenue_ranges.png')

def plot_word_count_by_sentiment(df):
    """Create a box plot of word count by sentiment."""
    # Filter out items without sentiment analysis
    sentiment_df = df[df['sentiment'] != 'Unknown']
    
    if sentiment_df.empty:
        print("No sentiment data available for visualization")
        return
    
    fig, ax = plt.subplots()

    # Create box plot
    sns.boxplot(data=sentiment_df, x='sentiment', y='word_count', ax=ax)
    
    ax.set_xlabel('Sentiment', fontsize=14)
    ax.set_ylabel('Number of Words in Headline', fontsize=14)
    ax.set_title('Headline Word Count by Sentiment', fontsize=16, pad=20)
    
    save_plot(fig, 'word_count_by_sentiment.png')

def plot_average_word_count_by_revenue_bins(df):
    """Create a bar chart of average word count by revenue bins."""
    fig, ax = plt.subplots()

    # Create revenue bins
    df['revenue_bin'] = pd.cut(df['revenue'], 
                              bins=10, 
                              precision=0)
    
    # Calculate average word count per bin
    avg_by_bin = df.groupby('revenue_bin')['word_count'].mean()
    
    # Create bar chart
    bars = ax.bar(range(len(avg_by_bin)), avg_by_bin.values, alpha=0.7, color='lightcoral')
    
    # Customize x-axis labels
    bin_labels = [f'${int(interval.left/1000)}k-{int(interval.right/1000)}k' 
                  for interval in avg_by_bin.index]
    ax.set_xticks(range(len(avg_by_bin)))
    ax.set_xticklabels(bin_labels, rotation=45, ha='right')
    
    ax.set_xlabel('Revenue Range', fontsize=14)
    ax.set_ylabel('Average Word Count', fontsize=14)
    ax.set_title('Average Headline Word Count by Revenue Bins', fontsize=16, pad=20)
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{height:.1f}', ha='center', va='bottom')
    
    save_plot(fig, 'avg_word_count_by_revenue_bins.png')

def plot_word_count_heatmap(df):
    """Create a heatmap showing word count distribution by revenue and sentiment."""
    # Filter out items without sentiment analysis
    sentiment_df = df[df['sentiment'] != 'Unknown']
    
    if sentiment_df.empty:
        print("No sentiment data available for heatmap")
        return
    
    fig, ax = plt.subplots()

    # Create revenue ranges
    sentiment_df['revenue_range'] = pd.cut(sentiment_df['revenue'], 
                                          bins=[0, 50000, 150000, float('inf')], 
                                          labels=['Low', 'Medium', 'High'])
    
    # Create pivot table
    pivot_table = sentiment_df.groupby(['revenue_range', 'sentiment'])['word_count'].mean().unstack()
    
    # Create heatmap
    sns.heatmap(pivot_table, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax)
    
    ax.set_xlabel('Sentiment', fontsize=14)
    ax.set_ylabel('Revenue Range', fontsize=14)
    ax.set_title('Average Word Count by Revenue Range and Sentiment', fontsize=16, pad=20)
    
    save_plot(fig, 'word_count_heatmap.png')

def plot_top_word_counts(df):
    """Create a bar chart of the most common word counts."""
    fig, ax = plt.subplots()

    # Count frequency of each word count
    word_count_freq = df['word_count'].value_counts().head(15)
    
    # Create bar chart
    bars = ax.bar(word_count_freq.index, word_count_freq.values, alpha=0.7, color='mediumseagreen')
    
    ax.set_xlabel('Number of Words', fontsize=14)
    ax.set_ylabel('Number of Headlines', fontsize=14)
    ax.set_title('Most Common Headline Word Counts', fontsize=16, pad=20)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{int(height)}', ha='center', va='bottom')
    
    save_plot(fig, 'top_word_counts.png')

def generate_summary_stats(df):
    """Generate and save summary statistics."""
    stats_file = os.path.join(OUTPUT_DIR, 'word_length_stats.txt')
    
    with open(stats_file, 'w') as f:
        f.write("HEADLINE WORD LENGTH ANALYSIS SUMMARY\n")
        f.write("=" * 40 + "\n\n")
        
        f.write(f"Total headlines analyzed: {len(df)}\n")
        f.write(f"Mean word count: {df['word_count'].mean():.2f}\n")
        f.write(f"Median word count: {df['word_count'].median():.2f}\n")
        f.write(f"Standard deviation: {df['word_count'].std():.2f}\n")
        f.write(f"Min word count: {df['word_count'].min()}\n")
        f.write(f"Max word count: {df['word_count'].max()}\n\n")
        
        # Word count distribution
        f.write("Word count distribution:\n")
        word_count_dist = df['word_count'].value_counts().sort_index()
        for count, freq in word_count_dist.items():
            percentage = (freq / len(df)) * 100
            f.write(f"  {count} words: {freq} headlines ({percentage:.1f}%)\n")
        
        # Correlation with revenue
        correlation = df['word_count'].corr(df['revenue'])
        f.write(f"\nCorrelation with revenue: {correlation:.3f}\n")
        
        # By revenue ranges
        f.write("\nAverage word count by revenue range:\n")
        df['revenue_range'] = pd.cut(df['revenue'], 
                                    bins=[0, 50000, 150000, float('inf')], 
                                    labels=['Low ($0-$50k)', 'Medium ($50k-$150k)', 'High ($150k+)'])
        
        for range_name in ['Low ($0-$50k)', 'Medium ($50k-$150k)', 'High ($150k+)']:
            range_data = df[df['revenue_range'] == range_name]
            if not range_data.empty:
                avg_words = range_data['word_count'].mean()
                f.write(f"  {range_name}: {avg_words:.2f} words\n")
    
    print(f"Summary statistics saved to: {stats_file}")

def main():
    """Main function."""
    data = load_data()
    df = create_dataframe(data, english_only=True)
    
    if df.empty:
        print("No data to visualize.")
        return
    
    print(f"Creating visualizations for {len(df)} headlines...")
    
    # Generate all visualizations
    plot_word_count_distribution(df)
    plot_word_count_by_revenue(df)
    plot_word_count_by_revenue_ranges(df)
    plot_word_count_by_sentiment(df)
    plot_average_word_count_by_revenue_bins(df)
    plot_word_count_heatmap(df)
    plot_top_word_counts(df)
    
    # Generate summary statistics
    generate_summary_stats(df)
    
    print(f"\nAll visualizations saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main() 