#!/usr/bin/env python3
"""
Analyze benefit keywords and action verbs in startups.json.
Generate a markdown report and visualizations showing the relationship between words and revenue.
"""

import json
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter, defaultdict

# Set the style for all plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_theme(font_scale=1.2)

# Create output directories if they don't exist
OUTPUT_DIR = 'visualizations/keywords_analysis'
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

def extract_keywords_and_verbs(data):
    """Extract benefit keywords and action verbs from the data."""
    # Initialize counters and revenue trackers
    benefit_keywords_counter = Counter()
    action_verbs_counter = Counter()
    
    # Track total revenue associated with each keyword/verb
    keyword_revenue = defaultdict(int)
    verb_revenue = defaultdict(int)
    
    # Track number of startups using each keyword/verb
    keyword_startup_count = defaultdict(int)
    verb_startup_count = defaultdict(int)
    
    # Process each startup
    for item in data:
        if 'benefitKeywords' not in item or 'actionVerbs' not in item:
            continue
        
        revenue = item.get('revenue', 0)
        
        # Process benefit keywords
        for keyword in item.get('benefitKeywords', []):
            # Convert to lowercase for case-insensitive counting
            keyword = keyword.lower()
            benefit_keywords_counter[keyword] += 1
            keyword_revenue[keyword] += revenue
            keyword_startup_count[keyword] += 1
        
        # Process action verbs
        for verb in item.get('actionVerbs', []):
            # Convert to lowercase for case-insensitive counting
            verb = verb.lower()
            action_verbs_counter[verb] += 1
            verb_revenue[verb] += revenue
            verb_startup_count[verb] += 1
    
    return {
        'benefit_keywords': {
            'counter': benefit_keywords_counter,
            'revenue': keyword_revenue,
            'startup_count': keyword_startup_count
        },
        'action_verbs': {
            'counter': action_verbs_counter,
            'revenue': verb_revenue,
            'startup_count': verb_startup_count
        }
    }

def calculate_average_revenue(total_revenue, startup_count):
    """Calculate average revenue per startup for each keyword/verb."""
    avg_revenue = {}
    for word, revenue in total_revenue.items():
        count = startup_count[word]
        if count > 0:
            avg_revenue[word] = revenue / count
    return avg_revenue

def generate_markdown_report(keywords_data, min_count=2):
    """Generate a markdown report of the most common benefit keywords and action verbs."""
    benefit_keywords = keywords_data['benefit_keywords']
    action_verbs = keywords_data['action_verbs']
    
    # Calculate average revenue
    keyword_avg_revenue = calculate_average_revenue(
        benefit_keywords['revenue'], 
        benefit_keywords['startup_count']
    )
    verb_avg_revenue = calculate_average_revenue(
        action_verbs['revenue'], 
        action_verbs['startup_count']
    )
    
    # Start building the markdown report
    report = "# Benefit Keywords and Action Verbs Analysis\n\n"
    
    # Add benefit keywords section
    report += "## Most Common Benefit Keywords\n\n"
    report += "| Keyword | Count | Total Revenue | Avg Revenue per Startup |\n"
    report += "|---------|-------|--------------|-------------------------|\n"
    
    # Sort by count (descending)
    for keyword, count in benefit_keywords['counter'].most_common():
        if count >= min_count:  # Only include keywords that appear at least min_count times
            total_rev = benefit_keywords['revenue'][keyword]
            avg_rev = keyword_avg_revenue[keyword]
            report += f"| {keyword} | {count} | ${total_rev:,.2f} | ${avg_rev:,.2f} |\n"
    
    # Add action verbs section
    report += "\n## Most Common Action Verbs\n\n"
    report += "| Verb | Count | Total Revenue | Avg Revenue per Startup |\n"
    report += "|------|-------|--------------|-------------------------|\n"
    
    # Sort by count (descending)
    for verb, count in action_verbs['counter'].most_common():
        if count >= min_count:  # Only include verbs that appear at least min_count times
            total_rev = action_verbs['revenue'][verb]
            avg_rev = verb_avg_revenue[verb]
            report += f"| {verb} | {count} | ${total_rev:,.2f} | ${avg_rev:,.2f} |\n"
    
    # Add insights section
    report += "\n## Insights\n\n"
    
    # Top revenue-generating keywords
    report += "### Top Revenue-Generating Benefit Keywords\n\n"
    top_revenue_keywords = sorted(
        [(k, v) for k, v in benefit_keywords['revenue'].items() if benefit_keywords['counter'][k] >= min_count],
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    for keyword, revenue in top_revenue_keywords:
        count = benefit_keywords['counter'][keyword]
        avg_rev = keyword_avg_revenue[keyword]
        report += f"- **{keyword}**: ${revenue:,.2f} total revenue across {count} startups (${avg_rev:,.2f} avg)\n"
    
    # Top revenue-generating verbs
    report += "\n### Top Revenue-Generating Action Verbs\n\n"
    top_revenue_verbs = sorted(
        [(v, r) for v, r in action_verbs['revenue'].items() if action_verbs['counter'][v] >= min_count],
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    for verb, revenue in top_revenue_verbs:
        count = action_verbs['counter'][verb]
        avg_rev = verb_avg_revenue[verb]
        report += f"- **{verb}**: ${revenue:,.2f} total revenue across {count} startups (${avg_rev:,.2f} avg)\n"
    
    # Save the report
    report_path = os.path.join(OUTPUT_DIR, 'keywords_analysis.md')
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"Saved markdown report to {report_path}")
    
    return report

def plot_top_keywords_by_revenue(keywords_data, min_count=2):
    """Create bar charts showing top keywords and verbs by total revenue."""
    benefit_keywords = keywords_data['benefit_keywords']
    action_verbs = keywords_data['action_verbs']
    
    # Filter for keywords/verbs that appear at least min_count times
    filtered_keywords = {
        k: v for k, v in benefit_keywords['revenue'].items() 
        if benefit_keywords['counter'][k] >= min_count
    }
    filtered_verbs = {
        v: r for v, r in action_verbs['revenue'].items() 
        if action_verbs['counter'][v] >= min_count
    }
    
    # Sort by revenue (descending) and take top 15
    top_keywords = dict(sorted(filtered_keywords.items(), key=lambda x: x[1], reverse=True)[:15])
    top_verbs = dict(sorted(filtered_verbs.items(), key=lambda x: x[1], reverse=True)[:15])
    
    # Plot benefit keywords
    plt.figure(figsize=(12, 8))
    plt.bar(top_keywords.keys(), top_keywords.values(), color='#4CAF50')
    plt.xticks(rotation=45, ha='right')
    plt.title('Top 15 Benefit Keywords by Total Revenue', fontsize=16)
    plt.ylabel('Total Revenue ($)', fontsize=14)
    plt.xlabel('Benefit Keyword', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'top_keywords_by_revenue.png'), dpi=300)
    plt.close()
    
    # Plot action verbs
    plt.figure(figsize=(12, 8))
    plt.bar(top_verbs.keys(), top_verbs.values(), color='#1976D2')
    plt.xticks(rotation=45, ha='right')
    plt.title('Top 15 Action Verbs by Total Revenue', fontsize=16)
    plt.ylabel('Total Revenue ($)', fontsize=14)
    plt.xlabel('Action Verb', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'top_verbs_by_revenue.png'), dpi=300)
    plt.close()
    
    print("Saved revenue visualizations")

def plot_avg_revenue_comparison(keywords_data, min_count=2, min_startups=3):
    """Create a scatter plot comparing count vs. average revenue for keywords and verbs."""
    benefit_keywords = keywords_data['benefit_keywords']
    action_verbs = keywords_data['action_verbs']
    
    # Calculate average revenue
    keyword_avg_revenue = calculate_average_revenue(
        benefit_keywords['revenue'], 
        benefit_keywords['startup_count']
    )
    verb_avg_revenue = calculate_average_revenue(
        action_verbs['revenue'], 
        action_verbs['startup_count']
    )
    
    # Filter for keywords/verbs that appear at least min_count times and have at least min_startups
    keyword_data = []
    for keyword, count in benefit_keywords['counter'].items():
        if count >= min_count and benefit_keywords['startup_count'][keyword] >= min_startups:
            keyword_data.append({
                'word': keyword,
                'count': count,
                'avg_revenue': keyword_avg_revenue[keyword],
                'type': 'Benefit Keyword'
            })
    
    verb_data = []
    for verb, count in action_verbs['counter'].items():
        if count >= min_count and action_verbs['startup_count'][verb] >= min_startups:
            verb_data.append({
                'word': verb,
                'count': count,
                'avg_revenue': verb_avg_revenue[verb],
                'type': 'Action Verb'
            })
    
    # Combine data
    all_data = pd.DataFrame(keyword_data + verb_data)
    
    if len(all_data) == 0:
        print("Not enough data for scatter plot")
        return
    
    # Create scatter plot
    plt.figure(figsize=(12, 8))
    sns.scatterplot(
        data=all_data,
        x='count',
        y='avg_revenue',
        hue='type',
        size='count',
        sizes=(50, 300),
        alpha=0.7
    )
    
    # Add labels for points
    for _, row in all_data.iterrows():
        plt.annotate(
            row['word'],
            (row['count'], row['avg_revenue']),
            xytext=(5, 5),
            textcoords='offset points',
            fontsize=9
        )
    
    plt.title('Word Frequency vs. Average Revenue', fontsize=16)
    plt.xlabel('Word Frequency (Count)', fontsize=14)
    plt.ylabel('Average Revenue per Startup ($)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'word_frequency_vs_avg_revenue.png'), dpi=300)
    plt.close()
    
    print("Saved scatter plot visualization")

def main():
    """Main function to generate the analysis."""
    print("Loading data...")
    data = load_data()
    
    print("Extracting keywords and verbs...")
    keywords_data = extract_keywords_and_verbs(data)
    
    print("Generating markdown report...")
    generate_markdown_report(keywords_data, min_count=2)
    
    print("Creating visualizations...")
    plot_top_keywords_by_revenue(keywords_data, min_count=2)
    plot_avg_revenue_comparison(keywords_data, min_count=2, min_startups=2)
    
    print(f"\nAll analysis files saved to the '{OUTPUT_DIR}' directory.")

if __name__ == "__main__":
    main()
