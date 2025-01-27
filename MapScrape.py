import json
import time
import random
from urllib.parse import quote
from playwright.sync_api import sync_playwright

def get_user_input():
    print("\nGoogle Maps Venue Scraper")
    print("----------------------------")
    search_terms = input("Enter search terms (or press Enter for 'cute cafes amsterdam'): ").strip()
    
    try:
        max_results = input("Enter maximum number of results (or press Enter for 50) Note, higher numbers could take a while to scrape, and could be rate limited by Google: ").strip()
        max_results = 50 if not max_results else int(max_results)
    except ValueError:
        print("Invalid number, using 50 results")
        max_results = 50
    
    if not search_terms:
        return "https://www.google.com/maps/search/cute+cafes+amsterdam", max_results
    
    formatted_terms = '+'.join(search_terms.split())
    url = f"https://www.google.com/maps/search/{formatted_terms}"
    return url, max_results

def simulate_human_movement(page):
#Add random mouse movements
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
        current_results = extract_venues(page)
        current_results_count = len(current_results)
        
        # Check if we've reached max results
        if current_results_count >= max_results:
            print(f"Reached maximum results limit ({max_results})")
            break
        
        # Check if we're getting new results
        if current_results_count == previous_results_count:
            same_count_iterations += 1
            if same_count_iterations >= MAX_SAME_COUNT:
                print("No new results found after multiple scrolls, likely reached the end")
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

def extract_venues(page):
    #just from quick scan of HTML, but likely open to change
    venues = []
    selectors = [
        'div.Nv2PK.THOPZb',
        '[role="article"]',
        'div[jsaction*="mouseover:pane"]'
    ]
    
    for selector in selectors:
        if page.locator(selector).count() > 0:
            venue_cards = page.locator(selector).all()
            for card in venue_cards:
                name = card.locator('div.qBF1Pd').first.inner_text()
                if name: venues.append(name)
            break
    return list(set(venues))

def save_results(venues):
#Save results to JSON
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved {len(venues)} venues to venues.json")

def scrape_google_maps(url, max_results):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            print(f"\nAccessing {url}")
            page.goto(url, timeout=60000)
            time.sleep(random.uniform(2, 4))
            
            handle_cookies(page)
            print("Waiting for results to load...")
            page.wait_for_selector('div.Nv2PK', timeout=20000)
            
            scroll_results_container(page, max_results)
            venues = extract_venues(page)[:max_results]
            save_results(venues)
            
        except Exception as e:
            print(f"\nError: {str(e)}")
        finally:
            browser.close()

if __name__ == "__main__":
    url, max_results = get_user_input()
    scrape_google_maps(url, max_results)