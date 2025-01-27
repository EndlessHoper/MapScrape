# Google Maps Venue Scraper

A simple Python script that scrapes venue names from Google Maps search results. Built with Playwright for web automation.

## Features
- Search for any location/venue type on Google Maps
- Customizable number of results
- Human-like scrolling and mouse movements
- Automatic cookie handling
- Results saved to JSON file

# Note
 - This runs in headful mode, so you can see the browser open and close.
 - The approach is quite basic, just for me to use for personal projects
 - May break when Google changes their website structure

## Requirements
- Python 3.7+
- Playwright

## Installation

1. Clone the repository
2. Install dependencies: `pip install playwright`
3. Run the script: `python main.py`

## Usage

1. Enter your search terms when prompted.
2. Enter the maximum number of results you want to scrape.
3. The script will save the results to `venues.json`.


