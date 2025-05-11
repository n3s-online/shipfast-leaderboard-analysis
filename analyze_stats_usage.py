#!/usr/bin/env python3
"""
Analyze the impact of using statistics in headlines.
This script examines how the 'usesStats' attribute relates to revenue and other metrics.
"""

import json
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats

# Set the style for all plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_theme(font_scale=1.2)

# Create output directory if it doesn't exist
OUTPUT_DIR = 'visualizations/stats_analysis'
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

def create_dataframe(data):
    """
    Convert JSON data to a pandas DataFrame for easier analysis.

    Args:
        data (list): List of startup dictionaries

    Returns:
        pd.DataFrame: DataFrame with usesStats and revenue data
    """
    # Filter for items with usesStats metadata
    filtered_data = [
        item for item in data
        if 'usesStats' in item
    ]

    print(f"Filtered to {len(filtered_data)} startups with usesStats metadata")

    # Convert to DataFrame
    df = pd.DataFrame([
        {
            'headline': item.get('headline', ''),
            'startup': item.get('startup', 'Unknown'),
            'maker': item.get('maker', ''),
            'revenue': item.get('revenue', 0),
            'language': item.get('language', 'Unknown'),
            'usesStats': item.get('usesStats', False),
            'focus': item.get('focus', 'Unknown'),
            'phraseType': item.get('phraseType', 'Unknown'),
            'benefitKeywords': len(item.get('benefitKeywords', [])),
            'actionVerbs': len(item.get('actionVerbs', []))
        }
        for item in filtered_data
    ])

    return df

def save_plot(fig, filename):
    """Save the figure as a PNG."""
    # Set a consistent size for all plots
    fig.set_size_inches(12, 8)
    plt.tight_layout()

    # Save the figure
    filepath = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {filepath}")

def plot_stats_distribution(df):
    """Create a pie chart showing the distribution of startups that use statistics vs. those that don't."""
    stats_counts = df['usesStats'].value_counts()

    # Create a custom color map
    colors = {True: '#4CAF50', False: '#F44336'}
    stats_colors = [colors[uses_stats] for uses_stats in stats_counts.index]

    # Create labels that are more descriptive
    labels = {True: 'Uses Statistics', False: 'No Statistics'}
    stats_labels = [labels[uses_stats] for uses_stats in stats_counts.index]

    fig, ax = plt.subplots()
    _, texts, autotexts = ax.pie(
        stats_counts,
        labels=stats_labels,
        autopct='%1.1f%%',
        startangle=90,
        colors=stats_colors,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )

    # Style the text
    for text in texts:
        text.set_fontsize(14)
    for autotext in autotexts:
        autotext.set_fontsize(12)
        autotext.set_color('white')
        autotext.set_fontweight('bold')

    plt.title('Percentage of Startups Using Statistics in Headlines', fontsize=18, pad=20)

    save_plot(fig, 'stats_distribution.png')

def plot_revenue_by_stats(df):
    """Create a bar chart showing average revenue for startups that use statistics vs. those that don't."""
    # Group by usesStats and calculate mean revenue
    revenue_by_stats = df.groupby('usesStats')['revenue'].mean().reset_index()

    # Create more descriptive labels
    labels = {True: 'Uses Statistics', False: 'No Statistics'}
    revenue_by_stats['label'] = revenue_by_stats['usesStats'].map(labels)

    # Create a custom color map
    colors = {True: '#4CAF50', False: '#F44336'}
    bar_colors = [colors[uses_stats] for uses_stats in revenue_by_stats['usesStats']]

    # Create the figure
    fig, ax = plt.subplots()

    # Create the bar chart
    bars = ax.bar(
        revenue_by_stats['label'],
        revenue_by_stats['revenue'],
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
    for i, (uses_stats, group) in enumerate(df.groupby('usesStats')):
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
    plt.title('Average Revenue by Use of Statistics in Headlines', fontsize=18, pad=20)
    plt.ylabel('Average Revenue ($)', fontsize=14)
    plt.xlabel('', fontsize=14)  # No x-axis label needed

    # Add grid lines for better readability
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Adjust y-axis to start from 0
    plt.ylim(bottom=0)

    # Add some padding to the top for the labels
    y_max = revenue_by_stats['revenue'].max() * 1.2
    plt.ylim(top=y_max)

    save_plot(fig, 'revenue_by_stats.png')

def plot_revenue_boxplot_by_stats(df):
    """Create a boxplot showing revenue distribution by use of statistics."""
    # Create more descriptive labels
    df['stats_label'] = df['usesStats'].map({True: 'Uses Statistics', False: 'No Statistics'})

    # Create a custom color map
    colors = {True: '#4CAF50', False: '#F44336'}
    palette = {label: colors[uses_stats] for uses_stats, label in zip([True, False], ['Uses Statistics', 'No Statistics'])}

    # Create the figure
    fig, ax = plt.subplots()

    # Create the boxplot
    sns.boxplot(
        x='stats_label',
        y='revenue',
        data=df,
        palette=palette,
        width=0.5,
        linewidth=1.5,
        fliersize=5,
        ax=ax
    )

    # Add individual data points with jitter for better visibility
    sns.stripplot(
        x='stats_label',
        y='revenue',
        data=df,
        color='black',
        size=4,
        alpha=0.5,
        jitter=True,
        ax=ax
    )

    # Add median value labels
    for i, uses_stats in enumerate([True, False]):
        label = 'Uses Statistics' if uses_stats else 'No Statistics'
        median_revenue = df[df['usesStats'] == uses_stats]['revenue'].median()
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
    for i, uses_stats in enumerate([True, False]):
        count = len(df[df['usesStats'] == uses_stats])
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
    plt.title('Revenue Distribution by Use of Statistics in Headlines', fontsize=18, pad=20)
    plt.ylabel('Revenue ($)', fontsize=14)
    plt.xlabel('', fontsize=14)  # No x-axis label needed

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

    save_plot(fig, 'revenue_boxplot_by_stats.png')

def plot_stats_by_focus(df):
    """Create a stacked bar chart showing the relationship between focus type and use of statistics."""
    # Create a cross-tabulation of focus vs. usesStats
    cross_tab = pd.crosstab(
        df['focus'],
        df['usesStats'],
        normalize='index'
    ) * 100  # Convert to percentages

    # Rename the columns for clarity
    cross_tab.columns = ['No Statistics', 'Uses Statistics']

    # Create the figure
    fig, ax = plt.subplots()

    # Create the stacked bar chart
    cross_tab.plot(
        kind='bar',
        stacked=True,
        color=['#F44336', '#4CAF50'],
        ax=ax,
        width=0.6
    )

    # Add percentage labels on the bars
    for i, focus in enumerate(cross_tab.index):
        # Add label for "Uses Statistics" percentage
        uses_stats_pct = cross_tab.loc[focus, 'Uses Statistics']
        if uses_stats_pct > 0:
            ax.text(
                i,
                100 - uses_stats_pct/2,
                f'{uses_stats_pct:.1f}%',
                ha='center',
                va='center',
                fontsize=10,
                fontweight='bold',
                color='white'
            )

        # Add label for "No Statistics" percentage
        no_stats_pct = cross_tab.loc[focus, 'No Statistics']
        if no_stats_pct > 0:
            ax.text(
                i,
                no_stats_pct/2,
                f'{no_stats_pct:.1f}%',
                ha='center',
                va='center',
                fontsize=10,
                fontweight='bold',
                color='white'
            )

    # Customize the plot
    plt.title('Use of Statistics by Headline Focus Type', fontsize=18, pad=20)
    plt.ylabel('Percentage (%)', fontsize=14)
    plt.xlabel('Headline Focus', fontsize=14)
    plt.xticks(rotation=0)  # No need to rotate with just two categories
    plt.ylim(0, 100)  # Set y-axis from 0 to 100%
    plt.legend(title='')

    save_plot(fig, 'stats_by_focus.png')

def generate_stats_analysis_report(df):
    """Generate a text report with statistical analysis of usesStats vs. revenue."""
    # Calculate basic statistics by usesStats
    stats_by_stats = df.groupby('usesStats')['revenue'].agg([
        'count', 'mean', 'median', 'min', 'max', 'std', 'sum'
    ]).reset_index()

    # Calculate percentiles
    percentiles = df.groupby('usesStats')['revenue'].quantile([0.25, 0.75, 0.95]).unstack()
    stats_by_stats = stats_by_stats.merge(percentiles, on='usesStats')

    # Calculate total revenue and percentage of total revenue by usesStats
    total_revenue = df['revenue'].sum()
    stats_by_stats['revenue_percentage'] = (stats_by_stats['sum'] / total_revenue) * 100

    # Perform t-test to check if the difference in means is statistically significant
    uses_stats_revenue = df[df['usesStats'] == True]['revenue']
    no_stats_revenue = df[df['usesStats'] == False]['revenue']
    t_stat, p_value = stats.ttest_ind(uses_stats_revenue, no_stats_revenue, equal_var=False)

    # Format the report
    report = "# Statistics Usage Analysis Report\n\n"

    report += "## 1. Overall Distribution\n\n"
    for uses_stats, group in df.groupby('usesStats'):
        label = "Uses Statistics" if uses_stats else "No Statistics"
        count = len(group)
        percentage = (count / len(df)) * 100
        report += f"{label}: {count} startups ({percentage:.1f}%)\n"

    report += "\n## 2. Revenue Analysis\n\n"
    for _, row in stats_by_stats.iterrows():
        label = "Uses Statistics" if row['usesStats'] else "No Statistics"
        report += f"### {label}\n\n"
        report += f"- Count: {row['count']} startups\n"
        report += f"- Total Revenue: ${row['sum']:,.2f} ({row['revenue_percentage']:.1f}% of all revenue)\n"
        report += f"- Average Revenue: ${row['mean']:,.2f}\n"
        report += f"- Median Revenue: ${row['median']:,.2f}\n"
        report += f"- Revenue Range: ${row['min']:,.2f} to ${row['max']:,.2f}\n"
        report += f"- Standard Deviation: ${row['std']:,.2f}\n"
        report += f"- 25th Percentile: ${row[0.25]:,.2f}\n"
        report += f"- 75th Percentile: ${row[0.75]:,.2f}\n"
        report += f"- 95th Percentile: ${row[0.95]:,.2f}\n\n"

    # Calculate and add revenue difference
    uses_stats_mean = stats_by_stats[stats_by_stats['usesStats'] == True]['mean'].values[0]
    no_stats_mean = stats_by_stats[stats_by_stats['usesStats'] == False]['mean'].values[0]
    difference = uses_stats_mean - no_stats_mean
    percentage_diff = (difference / no_stats_mean) * 100

    report += "## 3. Comparison\n\n"
    if difference > 0:
        report += f"Startups that use statistics in their headlines generate ${difference:,.2f} more revenue on average "
        report += f"({percentage_diff:.1f}% higher) than those that don't.\n\n"
    else:
        report += f"Startups that don't use statistics in their headlines generate ${-difference:,.2f} more revenue on average "
        report += f"({-percentage_diff:.1f}% higher) than those that do.\n\n"

    # Add statistical significance
    report += "## 4. Statistical Significance\n\n"
    report += f"T-statistic: {t_stat:.4f}\n"
    report += f"P-value: {p_value:.4f}\n\n"

    if p_value < 0.05:
        report += "The difference in average revenue between startups that use statistics and those that don't "
        report += "is statistically significant (p < 0.05).\n"
    else:
        report += "The difference in average revenue between startups that use statistics and those that don't "
        report += "is not statistically significant (p >= 0.05).\n"

    # Add list of all headlines that use statistics
    report += "\n## 5. Headlines Using Statistics\n\n"
    stats_headlines = df[df['usesStats'] == True]

    if len(stats_headlines) > 0:
        report += "| Startup | Revenue | Headline |\n"
        report += "|---------|---------|----------|\n"

        # Sort by revenue (descending)
        for _, row in stats_headlines.sort_values('revenue', ascending=False).iterrows():
            startup = row['startup']
            revenue = row['revenue']
            headline = row['headline']
            report += f"| {startup} | ${revenue:,.2f} | {headline} |\n"
    else:
        report += "No headlines using statistics found in the dataset.\n"

    # Save the report
    report_path = os.path.join(OUTPUT_DIR, 'stats_analysis_report.md')
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"Saved analysis report to {report_path}")

    return report

def main():
    """Main function to generate all visualizations and analysis."""
    print("Loading data...")
    data = load_data()

    print("Converting to DataFrame...")
    df = create_dataframe(data)

    if len(df) == 0:
        print("Error: No startups with usesStats metadata found.")
        return

    print(f"Generating visualizations for {len(df)} startups...")

    plot_stats_distribution(df)
    plot_revenue_by_stats(df)
    plot_revenue_boxplot_by_stats(df)
    plot_stats_by_focus(df)
    report = generate_stats_analysis_report(df)

    print("\nAnalysis Report:")
    print(report[:500] + "...\n")  # Print just the beginning of the report

    print(f"\nAll visualizations and reports saved to the '{OUTPUT_DIR}' directory.")

if __name__ == "__main__":
    main()
