#!/usr/bin/env python3
"""
Add language field to startups in startups.json.
Uses OpenAI to determine the language of the headline.
"""

import json
import os
import sys
import time
import re
from openai import OpenAI
from tqdm import tqdm
from dotenv import load_dotenv

# Configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
SAVE_INTERVAL = 5  # Save progress every N startups

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

def detect_language_with_openai(text):
    """Detect language of text using OpenAI."""
    if not text:
        return "unknown"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a language detection assistant. Respond with only the ISO 639-1 language code (e.g., 'en' for English, 'fr' for French, 'es' for Spanish, etc.). If you cannot determine the language, respond with 'unknown'."},
                {"role": "user", "content": f"Detect the language of this text: \"{text}\""}
            ],
            max_tokens=10,
            temperature=0.3
        )

        language_code = response.choices[0].message.content.strip().lower()

        # Clean up the response to ensure it's just a language code
        language_code = re.sub(r'[^a-z-]', '', language_code)

        # Map common language codes to their full names
        language_map = {
            'en': 'English',
            'fr': 'French',
            'es': 'Spanish',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'nl': 'Dutch',
            'ru': 'Russian',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'vi': 'Vietnamese',
            'th': 'Thai',
            'tr': 'Turkish',
            'pl': 'Polish',
            'sv': 'Swedish',
            'no': 'Norwegian',
            'fi': 'Finnish',
            'da': 'Danish',
            'cs': 'Czech',
            'hu': 'Hungarian',
            'el': 'Greek',
            'he': 'Hebrew',
            'id': 'Indonesian',
            'ms': 'Malay',
            'ro': 'Romanian',
            'sk': 'Slovak',
            'uk': 'Ukrainian',
            'bg': 'Bulgarian',
            'hr': 'Croatian',
            'lt': 'Lithuanian',
            'lv': 'Latvian',
            'et': 'Estonian',
            'sl': 'Slovenian',
            'sr': 'Serbian',
            'mk': 'Macedonian',
            'sq': 'Albanian',
            'bs': 'Bosnian',
            'mt': 'Maltese',
            'ga': 'Irish',
            'cy': 'Welsh',
            'gl': 'Galician',
            'eu': 'Basque',
            'ca': 'Catalan',
            'unknown': 'Unknown'
        }

        return language_map.get(language_code, language_code)

    except Exception as e:
        print(f"  OpenAI API error: {str(e)}")
        return "unknown"

def process_startups(input_file='startups.json', output_file='startups.json'):
    """Process startups and add language field."""
    try:
        startups = load_startups(input_file)

        # Count startups without language
        startups_without_language = [s for s in startups if 'language' not in s]
        total_to_process = len(startups_without_language)

        print(f"Found {total_to_process} startups without language field.")

        if total_to_process == 0:
            print("All startups already have language field. Nothing to do.")
            return

        # Process startups
        processed_count = 0
        success_count = 0

        for startup in tqdm(startups, desc="Processing startups"):
            try:
                # Skip if language already exists
                if 'language' in startup:
                    continue

                startup_name = startup['startup']

                # Check if headline exists
                if 'headline' not in startup:
                    # If no headline, set language to "unknown"
                    startup['language'] = "Unknown"
                    processed_count += 1
                    success_count += 1
                    print(f"\nNo headline for {startup_name}, setting language to 'Unknown'")
                else:
                    headline = startup['headline']
                    print(f"\nProcessing {startup_name} with headline: {headline}")

                    # Detect language
                    language = detect_language_with_openai(headline)

                    # Add language to startup data
                    startup['language'] = language
                    processed_count += 1
                    success_count += 1
                    print(f"  ✓ Detected language: {language}")

                # Save progress periodically
                if processed_count % SAVE_INTERVAL == 0:
                    save_startups(startups, output_file)
                    print(f"  ✓ Saved progress to {output_file}")

            except Exception as e:
                print(f"  ✗ Error processing {startup.get('startup', 'unknown startup')}: {str(e)}")
                # Continue with the next startup
                continue

        # Final save
        save_startups(startups, output_file)

        print(f"\nProcessing complete!")
        print(f"Processed {processed_count} startups")
        print(f"Successfully added language to {success_count} startups")

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
        print("The script will not be able to detect languages.")
        print("You can set the API key in one of two ways:")
        print("1. Create a .env file with OPENAI_API_KEY=your-api-key")
        print("2. Set the environment variable: export OPENAI_API_KEY='your-api-key'")
        print("")
        sys.exit(1)
    else:
        print("OPENAI_API_KEY found.")

    # Check if we're in test mode
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        print("Running in test mode with test_language.json...")
        process_startups('test_language.json', 'test_language_output.json')
    else:
        process_startups()
