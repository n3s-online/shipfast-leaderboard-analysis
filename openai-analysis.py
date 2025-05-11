#!/usr/bin/env python3
"""
Analyze the top 50 English startup headlines using OpenAI.
This script extracts headlines, sends them to OpenAI for analysis, and saves the results as markdown.
"""

import json
import os
import sys
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    sys.exit("Error: OPENAI_API_KEY not found in environment variables or .env file.")

openai.api_key = openai_api_key

# Create output directory if it doesn't exist
OUTPUT_DIR = 'analysis'
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

def extract_english_headlines(data, limit=50):
    """
    Extract the top English headlines from the data.
    
    Args:
        data (list): List of startup dictionaries
        limit (int): Maximum number of headlines to extract
    
    Returns:
        list: List of dictionaries with startup name and headline
    """
    # Filter for items with English headlines
    english_items = [
        {
            'rank': item.get('rank', 'Unknown'),
            'startup': item.get('startup', 'Unknown'),
            'headline': item.get('headline', ''),
            'revenue': item.get('revenue', 0)
        }
        for item in data
        if 'headline' in item and 'language' in item and item['language'] == 'English'
    ]
    
    # Sort by rank (or revenue if rank is not available)
    english_items.sort(key=lambda x: x['rank'] if isinstance(x['rank'], int) else float('inf'))
    
    # Take the top 'limit' items
    top_items = english_items[:limit]
    
    print(f"Extracted top {len(top_items)} English headlines")
    return top_items

def create_openai_prompt(headlines):
    """
    Create a prompt for OpenAI to analyze the headlines.
    
    Args:
        headlines (list): List of dictionaries with startup name and headline
    
    Returns:
        str: The prompt for OpenAI
    """
    prompt = "Analyze the following top 50 startup headlines and provide insights on:\n"
    prompt += "1. Common themes and patterns\n"
    prompt += "2. Effective copywriting techniques used\n"
    prompt += "3. Types of value propositions presented\n"
    prompt += "4. Use of action words, benefits, and features\n"
    prompt += "5. Overall tone and emotional appeal\n\n"
    prompt += "Please provide a concise, insightful analysis with specific examples from the headlines.\n\n"
    prompt += "Headlines:\n"
    
    for i, item in enumerate(headlines, 1):
        prompt += f"{i}. {item['startup']}: \"{item['headline']}\"\n"
    
    return prompt

def get_openai_analysis(prompt):
    """
    Send the prompt to OpenAI and get the analysis.
    
    Args:
        prompt (str): The prompt for OpenAI
    
    Returns:
        str: The analysis from OpenAI
    """
    try:
        print("Sending request to OpenAI...")
        response = openai.chat.completions.create(
            model="gpt-4",  # Using GPT-4 for better analysis
            messages=[
                {"role": "system", "content": "You are an expert copywriter and marketing analyst specializing in startup headlines and value propositions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Extract the content from the response
        analysis = response.choices[0].message.content
        print("Received analysis from OpenAI")
        return analysis
    
    except Exception as e:
        print(f"Error getting analysis from OpenAI: {e}")
        return f"Error: {str(e)}"

def save_analysis_as_markdown(headlines, analysis):
    """
    Save the headlines and analysis as a markdown file.
    
    Args:
        headlines (list): List of dictionaries with startup name and headline
        analysis (str): The analysis from OpenAI
    """
    markdown = "# Analysis of Top 50 Startup Headlines\n\n"
    
    # Add the list of headlines
    markdown += "## Headlines Analyzed\n\n"
    for i, item in enumerate(headlines, 1):
        markdown += f"{i}. **{item['startup']}**: \"{item['headline']}\"\n"
    
    # Add the OpenAI analysis
    markdown += "\n## OpenAI Analysis\n\n"
    markdown += analysis
    
    # Save to file
    output_path = os.path.join(OUTPUT_DIR, 'headline_analysis.md')
    with open(output_path, 'w') as file:
        file.write(markdown)
    
    print(f"Analysis saved to {output_path}")

def main():
    """Main function to run the analysis."""
    print("Loading data...")
    data = load_data()
    
    print("Extracting English headlines...")
    headlines = extract_english_headlines(data)
    
    if not headlines:
        print("No English headlines found.")
        return
    
    print("Creating prompt for OpenAI...")
    prompt = create_openai_prompt(headlines)
    
    print("Getting analysis from OpenAI...")
    analysis = get_openai_analysis(prompt)
    
    print("Saving analysis as markdown...")
    save_analysis_as_markdown(headlines, analysis)
    
    print("Analysis complete!")

if __name__ == "__main__":
    main()
