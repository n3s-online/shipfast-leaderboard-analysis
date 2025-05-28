#!/usr/bin/env python3
"""
Print the top 25 headlines by revenue from startups.json as a simple bulleted list.
Save output to a file in the output directory.
"""

import json
import sys
import os

# Create output directory if it doesn't exist
OUTPUT_DIR = 'output'
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

    return data

def print_top_headlines_list(data, top_n=25):
    """Print the top N headlines as a simple list and save to file."""
    # Filter for English items with headlines and revenue
    english_items = [
        item for item in data 
        if 'headline' in item and item['headline'] and 'revenue' in item 
        and item.get('language') == 'English'
    ]
    
    if not english_items:
        print("No English items with both headlines and revenue found.")
        return
    
    # Sort by revenue (descending)
    sorted_items = sorted(english_items, key=lambda x: x['revenue'], reverse=True)
    
    # Take top N
    top_items = sorted_items[:top_n]
    
    # Prepare output content
    output_lines = [f"Top {top_n} Headlines by Revenue:\n"]
    
    for item in top_items:
        headline = item['headline']
        line = f"- \"{headline}\""
        output_lines.append(line)
        print(line)  # Also print to console
    
    # Save to file
    output_file = os.path.join(OUTPUT_DIR, 'top_headlines_by_revenue.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"\nOutput saved to: {output_file}")

def main():
    """Main function."""
    data = load_data()
    print_top_headlines_list(data, 25)

if __name__ == "__main__":
    main() 