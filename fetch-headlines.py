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
import re
from bs4 import BeautifulSoup
from openai import OpenAI
from tqdm import tqdm
from urllib.parse import urlparse
from dotenv import load_dotenv

# Configuration
MAX_RETRIES = 1
RETRY_DELAY = 2  # seconds
REQUEST_TIMEOUT = 8  # seconds
SAVE_INTERVAL = 10  # Save progress every N startups
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

def sanitize_headline(headline):
    """Sanitize headline text by removing unwanted characters and formatting."""
    if not headline:
        return None

    # Fix Unicode escape sequences
    try:
        # First try to decode any Unicode escape sequences
        if '\\u' in headline:
            headline = headline.encode().decode('unicode_escape')

        # For JSON-loaded strings that already have Unicode characters
        # but might still have some escape sequences
        headline = json.loads(f'"{headline}"') if '\\u' in json.dumps(headline) else headline

        # Replace common problematic Unicode characters with their ASCII equivalents
        replacements = {
            '\u2018': "'",  # Left single quotation mark
            '\u2019': "'",  # Right single quotation mark
            '\u201c': '"',  # Left double quotation mark
            '\u201d': '"',  # Right double quotation mark
            '\u2013': '-',  # En dash
            '\u2014': '--', # Em dash
            '\u00a0': ' ',  # Non-breaking space
            '\u00e2\u0080\u009c': '"',  # Left double quotation mark (encoded)
            '\u00e2\u0080\u009d': '"',  # Right double quotation mark (encoded)
            '\u00e2\u0080\u0099': "'",  # Right single quotation mark (encoded)
            '\u00e2\u0080\u0098': "'",  # Left single quotation mark (encoded)
        }

        for old, new in replacements.items():
            headline = headline.replace(old, new)

        # Keep accented characters and other common non-ASCII characters
        # We don't need to replace these as they're valid and readable

        # Keep emojis as they are

    except Exception as e:
        # If any error occurs during Unicode handling, just continue with the original
        print(f"  Warning: Unicode handling error: {str(e)}")

    # Fix spacing issues
    # Replace multiple spaces with a single space
    sanitized = re.sub(r'\s+', ' ', headline)

    # Fix spacing around punctuation
    sanitized = re.sub(r'\s+([,.!?:;])', r'\1', sanitized)

    # Add space after punctuation if it's followed by a letter
    sanitized = re.sub(r'([,.!?:;])([a-zA-Z])', r'\1 \2', sanitized)

    # Remove common unwanted prefixes
    prefixes_to_remove = [
        "Welcome to ", "Home - ", "Home | ", "Homepage - ",
        "Official Website | ", "Official Website - ", "Official Website: "
    ]
    for prefix in prefixes_to_remove:
        if sanitized.startswith(prefix):
            sanitized = sanitized[len(prefix):]

    # Remove common unwanted suffixes
    suffixes_to_remove = [
        " | Home", " - Home", " | Official Website", " - Official Website"
    ]
    for suffix in suffixes_to_remove:
        if sanitized.endswith(suffix):
            sanitized = sanitized[:-len(suffix)]

    # Truncate if too long (over 100 characters)
    if len(sanitized) > 100:
        sanitized = sanitized[:97] + "..."

    return sanitized.strip()

def process_startups(input_file='startups.json', output_file='startups.json'):
    """Process startups and fetch headlines."""
    try:
        startups = load_startups(input_file)

        # Count startups without headlines
        startups_without_headlines = [s for s in startups if 'headline' not in s]
        total_to_process = len(startups_without_headlines)

        # Count startups with headlines (for sanitizing)
        startups_with_headlines = [s for s in startups if 'headline' in s]
        total_to_sanitize = len(startups_with_headlines)

        print(f"Found {total_to_process} startups without headlines and {total_to_sanitize} with headlines.")

        if total_to_process == 0 and total_to_sanitize == 0:
            print("No startups to process. Nothing to do.")
            return

        # Process startups
        processed_count = 0
        success_count = 0
        sanitized_count = 0

        for startup in tqdm(startups, desc="Processing startups"):
            try:
                startup_name = startup['startup']

                # Check if headline already exists
                if 'headline' in startup:
                    # Sanitize existing headline
                    original_headline = startup['headline']
                    sanitized_headline = sanitize_headline(original_headline)

                    if sanitized_headline != original_headline:
                        startup['headline'] = sanitized_headline
                        sanitized_count += 1
                        print(f"\nSanitized headline for {startup_name}:")
                        print(f"  Original: {original_headline}")
                        print(f"  Sanitized: {sanitized_headline}")

                        # Save after each sanitization
                        save_startups(startups, output_file)
                        print(f"  ✓ Saved progress to {output_file}")

                    continue

                processed_count += 1
                url = startup['url']  # Use the 'url' field instead of 'maker'

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
                        # Sanitize and add headline to startup data
                        sanitized_headline = sanitize_headline(headline)
                        startup['headline'] = sanitized_headline
                        success_count += 1
                        print(f"  ✓ Found headline: {sanitized_headline}")

                        # Save after each successful headline extraction
                        save_startups(startups, output_file)
                        print(f"  ✓ Saved progress to {output_file}")
                    else:
                        print(f"  ✗ Failed to extract headline")
                else:
                    print(f"  ✗ Failed to fetch website content")

            except Exception as e:
                print(f"  ✗ Error processing {startup.get('startup', 'unknown startup')}: {str(e)}")
                # Continue with the next startup
                continue

        # Final save
        save_startups(startups, output_file)

        print(f"\nProcessing complete!")
        print(f"Processed {processed_count} startups without headlines")
        print(f"Successfully extracted {success_count} headlines")
        print(f"Failed to extract {processed_count - success_count} headlines")
        print(f"Sanitized {sanitized_count} existing headlines")

    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user. Saving current progress...")
        save_startups(startups, output_file)
        print(f"Saved progress to {output_file}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nAn unexpected error occurred: {str(e)}")
        print("Attempting to save current progress...")
        try:
            save_startups(startups, output_file)
            print(f"Saved progress to {output_file}")
        except Exception as save_error:
            print(f"Failed to save progress: {str(save_error)}")
        sys.exit(1)

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
