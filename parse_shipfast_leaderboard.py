#!/usr/bin/env python3
"""
Script to parse ShipFast leaderboard HTML and extract top startups data in JSON format.
"""

import json
import re
from bs4 import BeautifulSoup

def parse_leaderboard(html_file_path, limit=100):
    """
    Parse the ShipFast leaderboard HTML file and extract startup data.

    Args:
        html_file_path (str): Path to the HTML file
        limit (int): Number of startups to extract (default: 100)

    Returns:
        list: List of dictionaries containing startup data
    """
    # Read the HTML file
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the table containing the leaderboard data
    table = soup.find('table', {'class': 'table'})

    if not table:
        print("Error: Could not find the leaderboard table in the HTML file.")
        return []

    # Find all rows in the table body
    rows = table.find('tbody').find_all('tr')

    startups_data = []

    # Process each row up to the limit
    for i, row in enumerate(rows):
        if i >= limit:
            break

        # Extract cells from the row
        cells = row.find_all('td')

        # Extract rank
        rank_cell = cells[0]
        if i < 3:  # Top 3 have medal emojis
            rank = i + 1
        else:
            rank_text = rank_cell.find('span', {'class': 'text-lg'}).text.strip()
            rank = int(rank_text)

        # Extract startup name and URL
        startup_cell = cells[1]
        startup_link = startup_cell.find('a', {'class': 'link'})
        startup_name = startup_link.text.strip()
        startup_url = startup_link.get('href')

        # Clean the URL by removing the tracking parameter
        if '?ref=shipfast_leaderboard' in startup_url:
            startup_url = startup_url.split('?ref=shipfast_leaderboard')[0]

        # Extract revenue
        revenue_cell = cells[2]
        revenue_text = revenue_cell.find('span').text.strip()
        # Remove the dollar sign and commas, then convert to integer
        revenue = int(revenue_text.replace('$', '').replace(',', ''))

        # Extract maker's X.com link
        maker_cell = cells[3]
        maker_link = maker_cell.find('a', {'class': 'link'})
        maker_url = maker_link.get('href') if maker_link else ""

        # Create a dictionary for this startup
        startup_data = {
            "rank": rank,
            "startup": startup_name,
            "url": startup_url,
            "revenue": revenue
        }

        # Only add maker if it exists and is not empty
        if maker_url and maker_url.strip():
            # Replace twitter.com with x.com
            if "twitter.com" in maker_url:
                maker_url = maker_url.replace("twitter.com", "x.com")
            startup_data["maker"] = maker_url

        startups_data.append(startup_data)

    return startups_data

def save_to_json(data, output_file):
    """
    Save the data to a JSON file.

    Args:
        data (list): List of dictionaries to save
        output_file (str): Path to the output JSON file
    """
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2)

    print(f"Data saved to {output_file}")

def main():
    # Parse the leaderboard HTML file
    startups_data = parse_leaderboard('shipfast_leaderboard.html', limit=100)

    if startups_data:
        # Save the data to a JSON file
        save_to_json(startups_data, 'top_startups.json')

        # Print the first few entries as a sample
        print("\nSample of extracted data:")
        print(json.dumps(startups_data[:3], indent=2))

        print(f"\nTotal startups extracted: {len(startups_data)}")

if __name__ == "__main__":
    main()
