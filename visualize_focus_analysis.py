#!/usr/bin/env python3
"""
Visualize the distribution and revenue impact of headline focus (features vs. benefit).
Generates multiple visualizations as PNG files.
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
sns.set_theme(font_scale=1.2)  # Using set_theme instead of deprecated set

# Create output directory if it doesn't exist
OUTPUT_DIR = 'visualizations/focus_analysis'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_data():
    """Load data from startups.json and validate it has focus metadata."""
    try:
        with open('startups.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        sys.exit("Error: startups.json file not found.")
    except json.JSONDecodeError:
        sys.exit("Error: startups.json is not a valid JSON file.")

    # Filter out entries without headlines or focus metadata
    filtered_data = []
    for i, item in enumerate(data):
        if 'headline' not in item:
            print(f"Skipping item at index {i} ({item.get('startup', 'Unknown')}) - missing headline")
            continue
        if 'focus' not in item:
            print(f"Skipping item at index {i} ({item.get('startup', 'Unknown')}) - missing focus metadata")
            continue
        filtered_data.append(item)

    if not filtered_data:
        sys.exit("Error: No valid items with both headline and focus metadata found.")

    print(f"Found {len(filtered_data)} valid items with both headline and focus metadata")
    return filtered_data

def create_dataframe(data):
    """
    Convert JSON data to a pandas DataFrame for easier analysis.

    Args:
        data (list): List of startup dictionaries

    Returns:
        pd.DataFrame: DataFrame with focus metadata and revenue data
    """
    # Filter for items with headlines and focus metadata
    filtered_data = [
        item for item in data
        if 'headline' in item and 'focus' in item
    ]

    print(f"Filtered to {len(filtered_data)} headlines with focus metadata")

    # Convert to DataFrame
    df = pd.DataFrame([
        {
            'headline': item['headline'],
            'startup': item.get('startup', 'Unknown'),
            'maker': item.get('maker', ''),
            'revenue': item.get('revenue', 0),
            'language': item.get('language', 'Unknown'),
            'focus': item.get('focus', 'Unknown'),
            'phraseType': item.get('phraseType', 'Unknown'),
            'usesStats': item.get('usesStats', False),
            'benefitKeywords': len(item.get('benefitKeywords', [])),
            'actionVerbs': len(item.get('actionVerbs', []))
        }
        for item in filtered_data
    ])

    return df

def save_plot(fig, filename):
    """Save the figure as a PNG."""
    # Make the plot square
    fig.set_size_inches(10, 10)
    plt.tight_layout()

    # Save the figure
    filepath = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {filepath}")

def plot_focus_distribution(df):
    """Create a pie chart of focus distribution (features vs. benefit)."""
    focus_counts = df['focus'].value_counts()

    # Create a custom color map for the focus types
    colors = {'benefit': '#4CAF50', 'features': '#1976D2'}
    focus_colors = [colors[focus] for focus in focus_counts.index]

    fig, ax = plt.subplots()
    _, texts, autotexts = ax.pie(
        focus_counts,
        labels=focus_counts.index,
        autopct='%1.1f%%',
        startangle=90,
        colors=focus_colors,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )

    # Style the text
    for text in texts:
        text.set_fontsize(14)
    for autotext in autotexts:
        autotext.set_fontsize(12)
        autotext.set_color('white')
        autotext.set_fontweight('bold')

    plt.title('Distribution of Headline Focus', fontsize=18, pad=20)

    save_plot(fig, 'focus_distribution.png')

def plot_revenue_by_focus(df):
    """Create a bar chart showing average revenue by focus type."""
    # Group by focus and calculate mean revenue
    revenue_by_focus = df.groupby('focus')['revenue'].mean().reset_index()

    # Sort by average revenue (descending)
    revenue_by_focus = revenue_by_focus.sort_values('revenue', ascending=False)

    # Create a custom color map for the focus types
    colors = {'benefit': '#4CAF50', 'features': '#1976D2'}
    bar_colors = [colors[focus] for focus in revenue_by_focus['focus']]

    # Create the figure
    fig, ax = plt.subplots()

    # Create the bar chart
    bars = ax.bar(
        revenue_by_focus['focus'],
        revenue_by_focus['revenue'],
        color=bar_colors,
        edgecolor='white',
        linewidth=1.5,
        width=0.6
    )

    # Add value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2.,
            height + 1000,  # Offset for visibility
            f'${height:,.0f}',
            ha='center',
            va='bottom',
            fontsize=12,
            fontweight='bold'
        )

    # Add count labels below the category names
    for i, (focus, group) in enumerate(df.groupby('focus')):
        count = len(group)
        percentage = (count / len(df)) * 100
        ax.text(
            i,
            -5000,  # Offset below x-axis
            f'n={count} ({percentage:.1f}%)',
            ha='center',
            va='top',
            fontsize=10,
            color='dimgray'
        )

    # Customize the plot
    plt.title('Average Revenue by Headline Focus', fontsize=18, pad=20)
    plt.ylabel('Average Revenue ($)', fontsize=14)
    plt.xlabel('Focus Type', fontsize=14)

    # Add grid lines for better readability
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Adjust y-axis to start from 0
    plt.ylim(bottom=0)

    # Add some padding to the top for the labels
    y_max = revenue_by_focus['revenue'].max() * 1.2
    plt.ylim(top=y_max)

    save_plot(fig, 'revenue_by_focus.png')

def plot_revenue_boxplot_by_focus(df):
    """Create a boxplot showing revenue distribution by focus type."""
    # Create a custom color map for the focus types
    colors = {'benefit': '#4CAF50', 'features': '#1976D2'}

    # Create the figure
    fig, ax = plt.subplots()

    # Create the boxplot
    sns.boxplot(
        x='focus',
        y='revenue',
        data=df,
        palette=colors,
        hue='focus',  # Use focus for both x and hue to avoid deprecation warning
        legend=False,  # No need for legend since colors are obvious
        width=0.5,
        linewidth=1.5,
        fliersize=5,
        ax=ax
    )

    # Add individual data points with jitter for better visibility
    sns.stripplot(
        x='focus',
        y='revenue',
        data=df,
        color='black',
        size=4,
        alpha=0.5,
        jitter=True,
        ax=ax
    )

    # Add median value labels
    for i, focus in enumerate(df['focus'].unique()):
        median_revenue = df[df['focus'] == focus]['revenue'].median()
        ax.text(
            i,
            median_revenue + 5000,  # Offset for visibility
            f'${median_revenue:,.0f}',
            ha='center',
            va='bottom',
            fontsize=10,
            fontweight='bold',
            color='darkblue'
        )

    # Add count labels below the category names
    for i, focus in enumerate(df['focus'].unique()):
        count = len(df[df['focus'] == focus])
        percentage = (count / len(df)) * 100
        ax.text(
            i,
            ax.get_ylim()[0] + 1000,  # Offset from bottom
            f'n={count} ({percentage:.1f}%)',
            ha='center',
            va='bottom',
            fontsize=10,
            color='dimgray'
        )

    # Customize the plot
    plt.title('Revenue Distribution by Headline Focus', fontsize=18, pad=20)
    plt.ylabel('Revenue ($)', fontsize=14)
    plt.xlabel('Focus Type', fontsize=14)

    # Add grid lines for better readability
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Use linear scale for y-axis
    # Set y-axis limits to focus on the main distribution (excluding extreme outliers)
    # Calculate the 95th percentile as the upper limit to exclude extreme outliers
    upper_limit = df['revenue'].quantile(0.95)
    plt.ylim(0, upper_limit * 1.1)  # Add 10% padding at the top

    # Add a horizontal line at the overall median revenue
    median_revenue = df['revenue'].median()
    plt.axhline(y=median_revenue, color='gray', linestyle='--', linewidth=1.5, alpha=0.7)
    plt.text(
        ax.get_xlim()[1] - 0.1,
        median_revenue,
        f'Overall Median: ${median_revenue:,.0f}',
        ha='right',
        va='bottom',
        fontsize=10,
        fontweight='bold',
        color='gray'
    )

    # Add a note about outliers
    plt.figtext(
        0.5, 0.01,
        f"Note: Plot is limited to the 95th percentile (${upper_limit:,.0f}). Some outliers above this value are not shown.",
        ha='center',
        fontsize=9,
        color='dimgray',
        style='italic'
    )

    save_plot(fig, 'revenue_boxplot_by_focus.png')

def generate_focus_analysis_report(df):
    """Generate a text report with statistical analysis of focus vs. revenue."""
    # Calculate basic statistics by focus
    stats_by_focus = df.groupby('focus')['revenue'].agg([
        'count', 'mean', 'median', 'min', 'max', 'std', 'sum'
    ]).reset_index()

    # Calculate percentiles
    percentiles = df.groupby('focus')['revenue'].quantile([0.25, 0.75, 0.95]).unstack()
    stats_by_focus = stats_by_focus.merge(percentiles, on='focus')

    # Calculate total revenue and percentage of total revenue by focus
    total_revenue = df['revenue'].sum()
    stats_by_focus['revenue_percentage'] = (stats_by_focus['sum'] / total_revenue) * 100

    # Format the report
    report = "Focus Analysis Report\n"
    report += "===================\n\n"

    report += "1. Overall Distribution\n"
    report += "----------------------\n"
    for focus, group in df.groupby('focus'):
        count = len(group)
        percentage = (count / len(df)) * 100
        report += f"{focus.capitalize()}: {count} startups ({percentage:.1f}%)\n"

    report += "\n2. Revenue Analysis\n"
    report += "------------------\n"

    # Add total revenue information
    report += f"Total Revenue Across All Startups: ${total_revenue:,.2f}\n\n"

    for _, row in stats_by_focus.iterrows():
        focus = row['focus'].capitalize()
        report += f"{focus} Focus:\n"
        report += f"  Count: {row['count']} startups\n"
        report += f"  Total Revenue: ${row['sum']:,.2f} ({row['revenue_percentage']:.1f}% of all revenue)\n"
        report += f"  Average Revenue: ${row['mean']:,.2f}\n"
        report += f"  Median Revenue: ${row['median']:,.2f}\n"
        report += f"  Revenue Range: ${row['min']:,.2f} to ${row['max']:,.2f}\n"
        report += f"  Standard Deviation: ${row['std']:,.2f}\n"
        report += f"  25th Percentile: ${row[0.25]:,.2f}\n"
        report += f"  75th Percentile: ${row[0.75]:,.2f}\n"
        report += f"  95th Percentile: ${row[0.95]:,.2f}\n\n"

    # Calculate and add revenue difference
    benefit_mean = stats_by_focus[stats_by_focus['focus'] == 'benefit']['mean'].values[0]
    features_mean = stats_by_focus[stats_by_focus['focus'] == 'features']['mean'].values[0]
    difference = benefit_mean - features_mean
    percentage_diff = (difference / features_mean) * 100

    report += "3. Comparison\n"
    report += "------------\n"
    if difference > 0:
        report += f"Benefit-focused headlines generate ${difference:,.2f} more revenue on average "
        report += f"({percentage_diff:.1f}% higher) than feature-focused headlines.\n\n"
    else:
        report += f"Feature-focused headlines generate ${-difference:,.2f} more revenue on average "
        report += f"({-percentage_diff:.1f}% higher) than benefit-focused headlines.\n\n"

    # Save the report
    report_path = os.path.join(OUTPUT_DIR, 'focus_analysis_report.txt')
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"Saved analysis report to {report_path}")

    return report

def main():
    """Main function to generate all visualizations."""
    print("Loading and validating data...")
    data = load_data()

    print("Converting to DataFrame...")
    df = create_dataframe(data)

    if len(df) == 0:
        print("Error: No headlines with focus metadata found.")
        return

    print(f"Generating visualizations for {len(df)} headlines...")

    plot_focus_distribution(df)
    plot_revenue_by_focus(df)
    plot_revenue_boxplot_by_focus(df)
    report = generate_focus_analysis_report(df)

    print("\nAnalysis Report:")
    print(report)

    print(f"\nAll visualizations and reports saved to the '{OUTPUT_DIR}' directory.")

if __name__ == "__main__":
    main()
