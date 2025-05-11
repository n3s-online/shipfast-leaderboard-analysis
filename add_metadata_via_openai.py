#!/usr/bin/env python3
"""
Add metadata to startups.json using OpenAI API.

This script analyzes headlines and adds the following attributes:
- benefitKeywords: string[] - Keywords that emphasize results or advantages
- actionVerbs: string[] - Verbs focusing on what the user can do
- phraseType: "question" | "statement" - Whether the headline poses a question or makes a statement
- focus: "features" | "benefit" - Whether the headline highlights features or benefits
- usesStats: boolean - Whether the headline includes numerical data
"""

import json
import os
import sys
import time
import re
from dotenv import load_dotenv
import openai

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    sys.exit("Error: OPENAI_API_KEY not found in environment variables or .env file.")

# Set up OpenAI client
openai.api_key = OPENAI_API_KEY

def analyze_headline_with_openai(headline):
    """
    Analyze a headline using OpenAI API to extract metadata.

    Args:
        headline (str): The headline to analyze

    Returns:
        dict: A dictionary containing the extracted metadata
    """
    try:
        prompt = """
        Analyze the following headline: "{0}"

        Extract the following information:

        1. Benefit Keywords: List any words or phrases that emphasize results or advantages (e.g., "faster," "better," "more efficient," "save time," "increase revenue"). Return as a JSON array of strings. If none, return an empty array.

        2. Action Verbs: List any verbs focusing on what the user can do (e.g., "Simplify," "Automate," "Scale," "Connect"). Return as a JSON array of strings. If none, return an empty array.

        3. Phrase Type: Is this a question or a statement? Return either "question" or "statement".

        4. Focus: Does the headline highlight what the product does (features) or what the user gets (benefits)? Return either "features" or "benefit".

        5. Uses Stats: Does the headline include numerical data to back up claims? Return true or false.

        Format your response as a JSON object with the following structure:
        {{
            "benefitKeywords": ["keyword1", "keyword2", ...],
            "actionVerbs": ["verb1", "verb2", ...],
            "phraseType": "question" or "statement",
            "focus": "features" or "benefit",
            "usesStats": true or false
        }}

        Return ONLY the JSON object, nothing else.
        """.format(headline)

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes headlines and extracts specific metadata in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )

        # Extract the JSON response
        json_str = response.choices[0].message.content.strip()

        # If the response is wrapped in ```json and ```, remove them
        json_str = re.sub(r'^```json\s*', '', json_str)
        json_str = re.sub(r'\s*```$', '', json_str)

        # Parse the JSON response
        metadata = json.loads(json_str)

        return metadata

    except Exception as e:
        print(f"Error analyzing headline: {headline}")
        print(f"Error details: {str(e)}")
        # Return default values in case of error
        return {
            "benefitKeywords": [],
            "actionVerbs": [],
            "phraseType": "statement",
            "focus": "features",
            "usesStats": False
        }

def main():
    """Main function to add metadata to startups.json."""
    json_file_path = 'startups.json'

    # Read the existing data from startups.json
    try:
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
        print(f"Loaded {len(data)} startups from {json_file_path}")
    except FileNotFoundError:
        print(f"Error: {json_file_path} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: {json_file_path} is not a valid JSON file.")
        return

    # Process each item in the data
    processed_count = 0
    skipped_count = 0
    already_processed_count = 0

    for i, item in enumerate(data):
        # Check if this item already has all the metadata fields
        if all(field in item for field in ['benefitKeywords', 'actionVerbs', 'phraseType', 'focus', 'usesStats']):
            print(f"Item {i+1} ({item.get('startup', 'Unknown')}) already has metadata. Skipping...")
            already_processed_count += 1
            continue

        headline = item.get('headline', '')
        if not headline:
            print(f"Warning: Item {i+1} ({item.get('startup', 'Unknown')}) has no headline. Skipping...")
            skipped_count += 1
            continue

        print(f"Processing item {i+1} ({item.get('startup', 'Unknown')}): {headline}")

        # Analyze headline with OpenAI
        metadata = analyze_headline_with_openai(headline)

        # Add metadata to the item
        item['benefitKeywords'] = metadata['benefitKeywords']
        item['actionVerbs'] = metadata['actionVerbs']
        item['phraseType'] = metadata['phraseType']
        item['focus'] = metadata['focus']
        item['usesStats'] = metadata['usesStats']

        print(f"Added metadata: {metadata}")
        print("-" * 50)

        processed_count += 1

        # Save after each item to allow for resuming if interrupted
        with open(json_file_path, 'w') as json_file:
            json.dump(data, json_file, indent=2)
        print(f"Saved progress ({i+1}/{len(data)} items)")

        # Add a small delay to avoid rate limiting
        if i < len(data) - 1:  # Don't sleep after the last item
            time.sleep(1)  # Increased delay to be safer with API rate limits

    print(f"\nSummary:")
    print(f"- Processed {processed_count} headlines with metadata")
    print(f"- Skipped {skipped_count} items without headlines")
    print(f"- Already had metadata: {already_processed_count} items")
    print(f"- Total items: {len(data)}")
    print(f"\nResults saved to {json_file_path}")

if __name__ == "__main__":
    main()
