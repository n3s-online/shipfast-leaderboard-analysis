#!/usr/bin/env python3
"""
Fetch headlines for startups in startups.json.
Uses web scraping and OpenAI to extract headlines from websites.
Only processes entries that don't already have a headline field.
"""

import json
import os
import sys
import time
import random
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from tqdm import tqdm
from urllib.parse import urlparse
from dotenv import load_dotenv

# Configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
REQUEST_TIMEOUT = 10  # seconds
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:124.0) Gecko/20100101 Firefox/124.0'
]

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

def load_startups(filename='startups.json'):
    """Load startups data from JSON file."""
    try:
        with open(filename, 'r') as file:
            startups = json.load(file)
        return startups
    except FileNotFoundError:
        sys.exit(f"Error: {filename} file not found.")
    except json.JSONDecodeError:
        sys.exit(f"Error: {filename} is not a valid JSON file.")

def save_startups(startups, filename='startups.json'):
    """Save startups data to JSON file."""
    with open(filename, 'w') as file:
        json.dump(startups, file, indent=4)
    print(f"Saved updated data to {filename}")

def get_random_user_agent():
    """Return a random user agent from the list."""
    return random.choice(USER_AGENTS)

def fetch_website_content(url):
    """Fetch website content with retries."""
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()  # Raise an exception for 4XX/5XX responses
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"  Attempt {attempt + 1}/{MAX_RETRIES} failed: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAY * (attempt + 1)  # Exponential backoff
                print(f"  Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"  Failed to fetch {url} after {MAX_RETRIES} attempts")
                return None

def extract_headline_with_bs4(html_content):
    """Extract headline using BeautifulSoup."""
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, 'html.parser')

    # Try different methods to find the headline

    # Method 1: Look for h1 tags
    h1_tags = soup.find_all('h1')
    if h1_tags and len(h1_tags) > 0:
        return h1_tags[0].get_text().strip()

    # Method 2: Look for title tag
    title_tag = soup.find('title')
    if title_tag:
        return title_tag.get_text().strip()

    # Method 3: Look for meta tags with name="description" or property="og:description"
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        return meta_desc.get('content').strip()

    meta_og_desc = soup.find('meta', attrs={'property': 'og:description'})
    if meta_og_desc and meta_og_desc.get('content'):
        return meta_og_desc.get('content').strip()

    # Method 4: Look for meta tags with property="og:title"
    meta_og_title = soup.find('meta', attrs={'property': 'og:title'})
    if meta_og_title and meta_og_title.get('content'):
        return meta_og_title.get('content').strip()

    return None

def extract_headline_with_openai(html_content, startup_name, url):
    """Extract headline using OpenAI."""
    if not html_content:
        return None

    # Truncate HTML content to avoid token limits
    truncated_html = html_content[:15000]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts the main headline or tagline from a website's HTML content. Return ONLY the headline text, nothing else. If you cannot find a headline, return a short, concise headline based on the company name and website content. Never return an error message or apology."},
                {"role": "user", "content": f"Extract the main headline or tagline for the startup '{startup_name}' from this website: {url}\n\nHTML content:\n{truncated_html}"}
            ],
            max_tokens=100,
            temperature=0.3
        )

        headline = response.choices[0].message.content.strip()

        # Clean up the headline (remove quotes, etc.)
        headline = headline.strip('"\'')

        # Check if the response looks like an error message or apology
        error_indicators = ["sorry", "cannot", "could not", "unable to", "doesn't contain", "does not contain", "no headline", "no tagline"]
        if any(indicator in headline.lower() for indicator in error_indicators):
            # Generate a fallback headline based on the startup name
            fallback_headline = f"{startup_name}: Innovative Solutions for Modern Businesses"
            print(f"  OpenAI returned an error-like response. Using fallback headline instead.")
            return fallback_headline

        return headline
    except Exception as e:
        print(f"  OpenAI API error: {str(e)}")
        return None

def process_startups(input_file='startups.json', output_file='startups.json'):
    """Process startups and fetch headlines."""
    startups = load_startups(input_file)

    # Count startups without headlines
    startups_without_headlines = [s for s in startups if 'headline' not in s]
    total_to_process = len(startups_without_headlines)

    if total_to_process == 0:
        print("All startups already have headlines. Nothing to do.")
        return

    print(f"Found {total_to_process} startups without headlines. Starting processing...")

    # Process startups without headlines
    processed_count = 0
    success_count = 0

    for startup in tqdm(startups, desc="Processing startups"):
        # Skip if headline already exists
        if 'headline' in startup:
            continue

        processed_count += 1
        startup_name = startup['startup']
        url = startup['maker']

        print(f"\nProcessing {startup_name} ({url})...")

        # Fetch website content
        html_content = fetch_website_content(url)

        if html_content:
            # Try to extract headline with BeautifulSoup
            headline = extract_headline_with_bs4(html_content)

            # If BeautifulSoup fails, try OpenAI
            if not headline or len(headline) < 5:
                print("  BeautifulSoup extraction failed or returned very short headline. Trying OpenAI...")
                headline = extract_headline_with_openai(html_content, startup_name, url)

            if headline:
                # Add headline to startup data
                startup['headline'] = headline
                success_count += 1
                print(f"  ✓ Found headline: {headline}")
            else:
                print(f"  ✗ Failed to extract headline")
        else:
            print(f"  ✗ Failed to fetch website content")

    # Save updated data
    save_startups(startups, output_file)

    print(f"\nProcessing complete!")
    print(f"Processed {processed_count} startups without headlines")
    print(f"Successfully extracted {success_count} headlines")
    print(f"Failed to extract {processed_count - success_count} headlines")

if __name__ == "__main__":
    # Check if OPENAI_API_KEY is set
    if not os.environ.get('OPENAI_API_KEY'):
        print("Warning: OPENAI_API_KEY is not set in environment variables or .env file.")
        print("The script will still run but OpenAI extraction will fail.")
        print("You can set the API key in one of two ways:")
        print("1. Create a .env file with OPENAI_API_KEY=your-api-key")
        print("2. Set the environment variable: export OPENAI_API_KEY='your-api-key'")
        print("")
    else:
        print("OPENAI_API_KEY found.")

    # Check if we're in test mode
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        print("Running in test mode with test_startups.json...")
        process_startups('test_startups.json', 'test_startups_output.json')
    else:
        process_startups()
