#!/usr/bin/env python3
"""
Visualize sentiment analysis data from data.json.
Generates multiple visualizations as square PNG files.
"""

import json
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# Set the style for all plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set(font_scale=1.2)

# Create output directory if it doesn't exist
OUTPUT_DIR = 'visualizations'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_data():
    """Load data from startups.json and validate it has sentiment analysis."""
    try:
        with open('startups.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        sys.exit("Error: startups.json file not found. Run sentiment_analysis.py first.")
    except json.JSONDecodeError:
        sys.exit("Error: startups.json is not a valid JSON file.")

    # Filter out entries without headlines or sentiment analysis
    filtered_data = []
    for i, item in enumerate(data):
        if 'headline' not in item:
            print(f"Skipping item at index {i} ({item.get('startup', 'Unknown')}) - missing headline")
            continue
        if 'sentiment_analysis' not in item:
            print(f"Skipping item at index {i} ({item.get('startup', 'Unknown')}) - missing sentiment analysis")
            continue
        filtered_data.append(item)

    if not filtered_data:
        sys.exit("Error: No valid items with both headline and sentiment analysis found.")

    # Validate that all entries have required sentiment analysis fields
    for item in filtered_data:
        sentiment_analysis = item['sentiment_analysis']
        required_fields = ['sentiment', 'negative', 'neutral', 'positive', 'compound']
        for field in required_fields:
            if field not in sentiment_analysis:
                sys.exit(f"Error: Sentiment analysis for '{item['headline']}' is missing the '{field}' field.")

    print(f"Found {len(filtered_data)} valid items with both headline and sentiment analysis")
    return filtered_data

def create_dataframe(data, english_only=True):
    """
    Convert JSON data to a pandas DataFrame for easier analysis.

    Args:
        data (list): List of startup dictionaries
        english_only (bool): If True, filter for English-only headlines

    Returns:
        pd.DataFrame: DataFrame with sentiment analysis data
    """
    # Filter for items with headlines and sentiment analysis
    filtered_data = [
        item for item in data
        if 'headline' in item and 'sentiment_analysis' in item
    ]

    # Further filter for English-only if requested
    if english_only:
        filtered_data = [
            item for item in filtered_data
            if 'language' in item and item['language'] == 'English'
        ]
        print(f"Filtered to {len(filtered_data)} English headlines")

    # Convert to DataFrame
    df = pd.DataFrame([
        {
            'headline': item['headline'],
            'startup': item.get('startup', 'Unknown'),
            'revenue': item.get('revenue', 0),
            'language': item.get('language', 'Unknown'),
            'sentiment': item['sentiment_analysis']['sentiment'],
            'negative': item['sentiment_analysis']['negative'],
            'neutral': item['sentiment_analysis']['neutral'],
            'positive': item['sentiment_analysis']['positive'],
            'compound': item['sentiment_analysis']['compound']
        }
        for item in filtered_data
    ])

    return df

def save_plot(fig, filename):
    """Save the figure as a square PNG."""
    # Make the plot square
    fig.set_size_inches(10, 10)
    plt.tight_layout()

    # Save the figure
    filepath = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {filepath}")

def plot_sentiment_distribution(df):
    """Create a pie chart of sentiment distribution."""
    sentiment_counts = df['sentiment'].value_counts()

    # Create a custom color map for the sentiments
    colors = {'Positive': '#4CAF50', 'Neutral': '#FFC107', 'Negative': '#F44336'}
    sentiment_colors = [colors[sentiment] for sentiment in sentiment_counts.index]

    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        sentiment_counts,
        labels=sentiment_counts.index,
        autopct='%1.1f%%',
        startangle=90,
        colors=sentiment_colors,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )

    # Style the text
    for text in texts:
        text.set_fontsize(14)
    for autotext in autotexts:
        autotext.set_fontsize(12)
        autotext.set_color('white')
        autotext.set_fontweight('bold')

    plt.title('Distribution of Sentiment Categories', fontsize=18, pad=20)

    save_plot(fig, 'sentiment_distribution.png')

def plot_compound_score_histogram(df):
    """Create a histogram of compound scores."""
    fig, ax = plt.subplots()

    # Create a custom colormap from red to yellow to green
    cmap = LinearSegmentedColormap.from_list('sentiment_cmap', ['#F44336', '#FFC107', '#4CAF50'])

    # Create histogram with custom bins and colors
    bins = np.linspace(-1, 1, 21)  # 20 bins from -1 to 1
    n, bins, patches = ax.hist(df['compound'], bins=bins, edgecolor='white', linewidth=1.5)

    # Color the bars based on the bin centers
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    norm = plt.Normalize(-1, 1)
    for c, p in zip(bin_centers, patches):
        plt.setp(p, 'facecolor', cmap(norm(c)))

    # Add vertical lines for sentiment thresholds
    plt.axvline(x=-0.05, color='#F44336', linestyle='--', linewidth=2, alpha=0.7)
    plt.axvline(x=0.05, color='#4CAF50', linestyle='--', linewidth=2, alpha=0.7)

    # Add text annotations for the thresholds
    plt.text(-0.05, ax.get_ylim()[1]*0.95, 'Negative Threshold',
             rotation=90, va='top', ha='right', color='#F44336', fontweight='bold')
    plt.text(0.05, ax.get_ylim()[1]*0.95, 'Positive Threshold',
             rotation=90, va='top', ha='left', color='#4CAF50', fontweight='bold')

    plt.xlabel('Compound Score', fontsize=14)
    plt.ylabel('Number of Headlines', fontsize=14)
    plt.title('Distribution of Compound Sentiment Scores', fontsize=18, pad=20)

    save_plot(fig, 'compound_score_histogram.png')

def plot_sentiment_components(df):
    """Create a stacked bar chart of positive, neutral, and negative components."""
    # Calculate the average scores for each sentiment component
    avg_scores = {
        'Positive': df['positive'].mean(),
        'Neutral': df['neutral'].mean(),
        'Negative': df['negative'].mean()
    }

    fig, ax = plt.subplots()

    # Create the bar chart
    bars = ax.bar(
        avg_scores.keys(),
        avg_scores.values(),
        color=['#4CAF50', '#FFC107', '#F44336'],
        edgecolor='white',
        linewidth=1.5
    )

    # Add value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2.,
            height + 0.01,
            f'{height:.3f}',
            ha='center',
            va='bottom',
            fontsize=12,
            fontweight='bold'
        )

    plt.ylim(0, 1)
    plt.xlabel('Sentiment Component', fontsize=14)
    plt.ylabel('Average Score', fontsize=14)
    plt.title('Average Sentiment Component Scores Across All Headlines', fontsize=18, pad=20)

    save_plot(fig, 'sentiment_components.png')

def plot_top_headlines(df, n=10):
    """Create horizontal bar charts for top positive and negative headlines."""
    # Sort by compound score
    df_sorted = df.sort_values('compound')

    # Get top n most negative and most positive headlines
    most_negative = df_sorted.head(n)
    most_positive = df_sorted.tail(n).iloc[::-1]  # Reverse to show highest first

    # Plot most negative headlines
    fig, ax = plt.subplots()
    bars = ax.barh(
        most_negative['headline'].str.slice(0, 30) + '...',
        most_negative['compound'],
        color='#F44336',
        edgecolor='white',
        linewidth=1.5,
        height=0.7
    )

    # Add value labels
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width - 0.05,
            bar.get_y() + bar.get_height()/2.,
            f'{width:.2f}',
            ha='right',
            va='center',
            color='white',
            fontsize=10,
            fontweight='bold'
        )

    plt.xlabel('Compound Score', fontsize=14)
    plt.title(f'Top {n} Most Negative Headlines', fontsize=18, pad=20)
    plt.xlim(-1, 0)

    save_plot(fig, 'most_negative_headlines.png')

    # Plot most positive headlines
    fig, ax = plt.subplots()
    bars = ax.barh(
        most_positive['headline'].str.slice(0, 30) + '...',
        most_positive['compound'],
        color='#4CAF50',
        edgecolor='white',
        linewidth=1.5,
        height=0.7
    )

    # Add value labels
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width - 0.05,
            bar.get_y() + bar.get_height()/2.,
            f'{width:.2f}',
            ha='right',
            va='center',
            color='white',
            fontsize=10,
            fontweight='bold'
        )

    plt.xlabel('Compound Score', fontsize=14)
    plt.title(f'Top {n} Most Positive Headlines', fontsize=18, pad=20)
    plt.xlim(0, 1)

    save_plot(fig, 'most_positive_headlines.png')

def plot_sentiment_boxplot(df):
    """Create a single box plot of compound sentiment scores."""
    # Create a figure
    fig, ax = plt.subplots()

    # Create a single box plot for compound scores
    sns.boxplot(
        y=df['compound'],
        color='#1976D2',  # Blue color
        linewidth=1.5,
        width=0.4,
        fliersize=5,
        ax=ax
    )

    # Add individual data points with jitter for better visibility
    sns.stripplot(
        y=df['compound'],
        color='black',
        size=4,
        alpha=0.5,
        jitter=True,
        ax=ax
    )

    # Add horizontal lines at the sentiment thresholds
    plt.axhline(y=0.05, color='#4CAF50', linestyle='--', linewidth=1.5, alpha=0.7)
    plt.axhline(y=-0.05, color='#F44336', linestyle='--', linewidth=1.5, alpha=0.7)
    plt.axhline(y=0, color='#FFC107', linestyle='--', linewidth=1.5, alpha=0.7)

    # Add text annotations for the thresholds
    plt.text(ax.get_xlim()[1]*0.95, 0.05, 'Positive Threshold',
             va='bottom', ha='right', color='#4CAF50', fontweight='bold')
    plt.text(ax.get_xlim()[1]*0.95, -0.05, 'Negative Threshold',
             va='top', ha='right', color='#F44336', fontweight='bold')
    plt.text(ax.get_xlim()[1]*0.95, 0, 'Neutral',
             va='center', ha='right', color='#FFC107', fontweight='bold')

    # Customize the plot
    plt.title('Distribution of Compound Sentiment Scores', fontsize=18, pad=20)
    plt.ylabel('Compound Score', fontsize=14)

    # Remove x-axis label and ticks
    plt.xlabel('')
    plt.xticks([])

    # Adjust y-axis limits for better visualization
    plt.ylim(-1.1, 1.1)

    save_plot(fig, 'sentiment_boxplot.png')

def main():
    """Main function to generate all visualizations."""
    print("Loading and validating data...")
    data = load_data()

    print("Converting to DataFrame with English-only filter...")
    df = create_dataframe(data, english_only=True)

    if len(df) == 0:
        print("Error: No English headlines with sentiment analysis found.")
        return

    print(f"Generating visualizations for {len(df)} English headlines...")

    # Add prefix to output filenames to indicate English-only
    global OUTPUT_DIR
    OUTPUT_DIR = os.path.join('visualizations', 'english_only')
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    plot_sentiment_distribution(df)
    plot_compound_score_histogram(df)
    plot_sentiment_components(df)
    plot_sentiment_boxplot(df)
    plot_top_headlines(df, n=5)

    print(f"\nAll visualizations saved to the '{OUTPUT_DIR}' directory.")

if __name__ == "__main__":
    main()
