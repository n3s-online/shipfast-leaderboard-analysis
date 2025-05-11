#!/usr/bin/env python3
"""
Analyze revenue data from startups.json and print out key statistics.
"""

import json
import statistics
import sys

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

def analyze_revenue(data):
    """Analyze revenue data and print statistics."""
    # Extract revenue values
    revenues = [startup.get('revenue', 0) for startup in data]

    # Calculate statistics
    total_revenue = sum(revenues)
    average_revenue = total_revenue / len(revenues) if revenues else 0
    median_revenue = statistics.median(revenues) if revenues else 0

    # Calculate standard deviation
    std_dev = statistics.stdev(revenues) if len(revenues) > 1 else 0

    # Find min and max revenue
    min_revenue = min(revenues) if revenues else 0
    max_revenue = max(revenues) if revenues else 0

    # Find startups with min and max revenue
    min_startup = next((s['startup'] for s in data if s.get('revenue', 0) == min_revenue), "Unknown")
    max_startup = next((s['startup'] for s in data if s.get('revenue', 0) == max_revenue), "Unknown")

    # Calculate quartiles
    q1 = statistics.quantiles(revenues, n=4)[0] if len(revenues) >= 4 else 0
    q3 = statistics.quantiles(revenues, n=4)[2] if len(revenues) >= 4 else 0

    # Calculate revenue ranges
    revenue_ranges = {
        "0-1K": 0,
        "1K-5K": 0,
        "5K-10K": 0,
        "10K-50K": 0,
        "50K-100K": 0,
        "100K+": 0
    }

    for revenue in revenues:
        if revenue < 1000:
            revenue_ranges["0-1K"] += 1
        elif revenue < 5000:
            revenue_ranges["1K-5K"] += 1
        elif revenue < 10000:
            revenue_ranges["5K-10K"] += 1
        elif revenue < 50000:
            revenue_ranges["10K-50K"] += 1
        elif revenue < 100000:
            revenue_ranges["50K-100K"] += 1
        else:
            revenue_ranges["100K+"] += 1

    # Print statistics
    print("\n===== REVENUE STATISTICS =====")
    print(f"Total Revenue: ${total_revenue:,}")
    print(f"Average Revenue: ${average_revenue:,.2f}")
    print(f"Median Revenue: ${median_revenue:,}")
    print(f"Standard Deviation: ${std_dev:,.2f}")
    print(f"Minimum Revenue: ${min_revenue:,} ({min_startup})")
    print(f"Maximum Revenue: ${max_revenue:,} ({max_startup})")
    print(f"1st Quartile (Q1): ${q1:,}")
    print(f"3rd Quartile (Q3): ${q3:,}")
    print(f"Interquartile Range (IQR): ${q3 - q1:,}")

    print("\n===== REVENUE DISTRIBUTION =====")
    for range_name, count in revenue_ranges.items():
        percentage = (count / len(revenues)) * 100 if revenues else 0
        print(f"{range_name}: {count} startups ({percentage:.1f}%)")

def main():
    """Main function to analyze revenue data."""
    print("Loading data from startups.json...")
    data = load_data()

    print(f"Analyzing revenue data for {len(data)} startups...")
    analyze_revenue(data)

if __name__ == "__main__":
    main()
