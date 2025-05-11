#!/usr/bin/env python3
"""
Analyze the makers (Twitter usernames) in startups.json.

This script:
1. Aggregates data by Twitter username (maker)
2. Produces a report showing all users with more than 1 entry
3. Aggregates revenue by maker
"""

import json
import sys
import matplotlib.pyplot as plt
import os
import re
from collections import defaultdict, Counter

# Create output directory if it doesn't exist
OUTPUT_DIR = 'visualizations/makers'
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

def extract_username(maker_url):
    """Extract the Twitter username from the maker URL."""
    if not maker_url or not isinstance(maker_url, str):
        return "unknown"

    # Extract username from URL like "https://x.com/username"
    match = re.search(r'x\.com/([^/]+)', maker_url)
    if match:
        return match.group(1).lower()  # Convert to lowercase for case-insensitive comparison

    return "unknown"

def analyze_makers(data):
    """Analyze the makers in the data."""
    # Group startups by maker
    startups_by_maker = defaultdict(list)
    for item in data:
        maker_url = item.get('maker', '')
        username = extract_username(maker_url)
        startups_by_maker[username].append(item)

    # Filter for makers with more than 1 entry
    makers_with_multiple_entries = {
        username: startups
        for username, startups in startups_by_maker.items()
        if len(startups) > 1 and username != "unknown"
    }

    # Count startups made by creators with more than 1 startup
    startups_by_multi_entry_makers = sum(len(startups) for startups in makers_with_multiple_entries.values())
    total_startups = len(data)
    percentage = (startups_by_multi_entry_makers / total_startups) * 100

    # Calculate total revenue from multi-startup creators
    revenue_from_multi_entry_makers = sum(
        sum(startup.get('revenue', 0) for startup in startups)
        for startups in makers_with_multiple_entries.values()
    )
    total_revenue = sum(item.get('revenue', 0) for item in data)
    revenue_percentage = (revenue_from_multi_entry_makers / total_revenue) * 100

    print(f"\nStartups by creators with multiple entries: {startups_by_multi_entry_makers} out of {total_startups} ({percentage:.1f}%)")
    print(f"Revenue from creators with multiple entries: ${revenue_from_multi_entry_makers:,} out of ${total_revenue:,} ({revenue_percentage:.1f}%)")

    # Calculate total revenue by maker
    revenue_by_maker = {}
    for username, startups in startups_by_maker.items():
        if username != "unknown":
            total_revenue = sum(startup.get('revenue', 0) for startup in startups)
            revenue_by_maker[username] = {
                'total_revenue': total_revenue,
                'num_startups': len(startups),
                'avg_revenue': total_revenue / len(startups) if startups else 0,
                'startups': [
                    {
                        'name': startup.get('startup', 'Unknown'),
                        'revenue': startup.get('revenue', 0),
                        'headline': startup.get('headline', 'No headline')
                    }
                    for startup in startups
                ]
            }

    # Print report for makers with multiple entries
    print(f"\nMakers with multiple entries: {len(makers_with_multiple_entries)}")
    print("\n" + "="*80)
    print(f"{'Username':<20} {'# Startups':<12} {'Total Revenue':<15} {'Avg Revenue':<15} {'Startups'}")
    print("-"*80)

    # Sort by total revenue (descending)
    sorted_makers = sorted(
        revenue_by_maker.items(),
        key=lambda x: x[1]['total_revenue'],
        reverse=True
    )

    for username, data in sorted_makers:
        if data['num_startups'] > 1:
            startup_names = ", ".join(startup['name'] for startup in data['startups'])
            print(f"{username:<20} {data['num_startups']:<12} ${data['total_revenue']:<14,.0f} ${data['avg_revenue']:<14,.0f} {startup_names}")

    print("="*80)

    # Generate visualizations
    generate_visualizations(revenue_by_maker, makers_with_multiple_entries)

    return revenue_by_maker, makers_with_multiple_entries

def generate_visualizations(revenue_by_maker, makers_with_multiple_entries):
    """Generate visualizations of the maker data."""
    # Create a bar chart of top makers by total revenue
    plt.figure(figsize=(14, 8))

    # Sort by total revenue and take top 15
    top_makers = dict(sorted(
        revenue_by_maker.items(),
        key=lambda x: x[1]['total_revenue'],
        reverse=True
    )[:15])

    usernames = list(top_makers.keys())
    revenues = [data['total_revenue'] for data in top_makers.values()]

    # Highlight makers with multiple startups
    colors = ['#1f77b4' if username in makers_with_multiple_entries else '#aec7e8' for username in usernames]

    plt.bar(usernames, revenues, color=colors)
    plt.xticks(rotation=45, ha='right')
    plt.title('Top 15 Makers by Total Revenue')
    plt.ylabel('Total Revenue ($)')
    plt.tight_layout()

    # Add a legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#1f77b4', label='Multiple Startups'),
        Patch(facecolor='#aec7e8', label='Single Startup')
    ]
    plt.legend(handles=legend_elements)

    plt.savefig(os.path.join(OUTPUT_DIR, 'top_makers_by_revenue.png'))
    plt.close()

    # Create a scatter plot of number of startups vs. average revenue
    plt.figure(figsize=(12, 8))

    num_startups = [data['num_startups'] for data in revenue_by_maker.values()]
    avg_revenues = [data['avg_revenue'] for data in revenue_by_maker.values()]
    usernames = list(revenue_by_maker.keys())

    plt.scatter(num_startups, avg_revenues, alpha=0.7)

    # Annotate points for makers with multiple startups
    for i, username in enumerate(usernames):
        if revenue_by_maker[username]['num_startups'] > 1:
            plt.annotate(
                username,
                (num_startups[i], avg_revenues[i]),
                xytext=(5, 5),
                textcoords='offset points'
            )

    plt.title('Number of Startups vs. Average Revenue by Maker')
    plt.xlabel('Number of Startups')
    plt.ylabel('Average Revenue ($)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'startups_vs_avg_revenue.png'))
    plt.close()

    print(f"\nVisualizations saved to {OUTPUT_DIR}")

def main():
    """Main function."""
    data = load_data()
    analyze_makers(data)

if __name__ == "__main__":
    main()
