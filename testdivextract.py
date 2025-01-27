from playwright.sync_api import sync_playwright
import time
import random
import json
import argparse
from urllib.parse import quote

def get_cli_args():
    parser = argparse.ArgumentParser(description='Google Maps Venue Scraper')
    parser.add_argument('search_terms', type=str, help='Search terms to look for')
    parser.add_argument('--max_results', type=int, default=50, 
                       help='Maximum number of results to gather (default: 50)')
    args = parser.parse_args()
    
    formatted_terms = '+'.join(args.search_terms.split())
    url = f"https://www.google.com/maps/search/{quote(formatted_terms)}"
    return url, args.max_results

def simulate_human_movement(page):
    page.mouse.move(
        random.randint(100, 700),
        random.randint(100, 700)
    )

def handle_cookies(page):
    for _ in range(3):
        try:
            if page.locator('button:has-text("Reject All")').count() > 0:
                simulate_human_movement(page)
                page.click('button:has-text("Reject All")', timeout=5000)
                print("✓ Cookies handled")
                return
            time.sleep(random.uniform(0.8, 1.2))
        except:
            pass
    print("✓ No cookie dialog found")

def scroll_results_container(page, max_results):
    results_container = page.locator('div.m6QErb[aria-label^="Results for"]').first
    
    previous_results_count = 0
    same_count_iterations = 0
    MAX_SAME_COUNT = 3  # Number of times we'll allow the same count before stopping
    
    while True:
        # Get current results
        venue_cards = page.locator('div.Nv2PK').all()
        current_results_count = len(venue_cards)
        
        # Check if we've reached max results
        if current_results_count >= max_results:
            print(f"Reached target number of results ({max_results})")
            break
        
        # Check if we're getting new results
        if current_results_count == previous_results_count:
            same_count_iterations += 1
            if same_count_iterations >= MAX_SAME_COUNT:
                print("No new results found after multiple scrolls")
                break
        else:
            same_count_iterations = 0
            print(f"Found {current_results_count} venues...")
        
        # Store current count for next iteration
        previous_results_count = current_results_count
        
        # Scroll and add randomization
        scroll_percentage = random.uniform(0.85, 0.95)
        results_container.evaluate(
            f'(element) => element.scrollTo(0, element.scrollTop + element.clientHeight * {scroll_percentage})'
        )
        
        time.sleep(random.uniform(1.5, 2.5))
        simulate_human_movement(page)

def extract_venue_details(page):
    details = {}
    try:
        # Wait for the side panel to be visible first - short timeout
        side_panel_selector = '#QA0Szd > div > div > div.w6VYqd > div.bJzME.Hu9e2e.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde'
        page.wait_for_selector(side_panel_selector, timeout=2000)
        side_panel = page.locator(side_panel_selector).first
        
        # Name - quick check
        name_element = side_panel.locator('h1').first
        if name_element and name_element.is_visible(timeout=500):
            details['name'] = name_element.inner_text()

        # Rating - quick check
        rating_selector = 'div.TIHn2 div.F7nice > span:nth-child(1) > span:nth-child(1)'
        rating_element = side_panel.locator(rating_selector).first
        if rating_element and rating_element.is_visible(timeout=500):
            details['rating'] = rating_element.inner_text()
        
        # Address - quick check
        address_button = page.locator('button[data-item-id="address"]').first
        if address_button and address_button.is_visible(timeout=500):
            details['address'] = address_button.inner_text()

        # Website - quick check
        website_button = page.locator('a[data-item-id="authority"]').first
        if website_button and website_button.is_visible(timeout=500):
            details['website'] = website_button.get_attribute('href')

        # Phone - quick check
        phone_button = page.locator('button[data-item-id^="phone"]').first
        if phone_button and phone_button.is_visible(timeout=500):
            details['phone'] = phone_button.inner_text()

    except Exception as e:
        print(f"Error extracting details: {str(e)}")
    
    return details

def main():
    url, max_results = get_cli_args()
    venues_data = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            print(f"\nAccessing {url}")
            page.goto(url, timeout=60000)
            time.sleep(random.uniform(2, 4))
            
            handle_cookies(page)
            print("\nLooking for venue listings...")
            
            # Wait for results to load
            page.wait_for_selector('div.Nv2PK', timeout=20000)
            
            # Scroll to load desired number of results
            scroll_results_container(page, max_results)
            
            # Get all venue cards
            venue_cards = page.locator('div.Nv2PK').all()[:max_results]
            print(f"\nProcessing {len(venue_cards)} venues...")
            
            for i, card in enumerate(venue_cards, 1):
                try:
                    print(f"\nProcessing venue {i}/{len(venue_cards)}")
                    
                    # Click the card and wait for side panel
                    card.click()
                    time.sleep(1)  # Base wait for side panel animation
                    
                    # Extract details from side panel
                    details = extract_venue_details(page)
                    if details:
                        venues_data.append(details)
                        print(f"Extracted details for: {details.get('name', 'Unknown venue')}")
                        if 'rating' in details:
                            print(f"Rating: {details['rating']}")
                    
                    time.sleep(random.uniform(1, 1.5))
                    
                except Exception as e:
                    print(f"Error processing venue {i}: {str(e)}")
            
            # Save the results
            with open('venue_details.json', 'w', encoding='utf-8') as f:
                json.dump(venues_data, f, indent=2, ensure_ascii=False)
            print(f"\n✓ Saved {len(venues_data)} venue details to venue_details.json")
            
        except Exception as e:
            print(f"\nError: {str(e)}")
        finally:
            browser.close()

if __name__ == "__main__":
    main()
