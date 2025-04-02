# scraper_view.py
import pandas as pd
import re
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def extract_price(section):
    # Try to get the price from the special-rates element first.
    price_el = section.find("span", class_="special-rates")
    if price_el:
        text = price_el.get_text(strip=True)
    else:
        # Fallback: search any text in the section for a dollar value.
        possible_price_text = section.get_text(" ", strip=True)
        matches = re.findall(r"\$[\d,]+", possible_price_text)
        if not matches:
            return None
        text = matches[-1]  # take the last match
    try:
        return int(text.replace("$", "").replace(",", ""))
    except:
        return None

def scrape_university_view():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://live-theview.com/rates-floorplans/", wait_until="networkidle")
        
        # Wait for floorplan tabs to be rendered.
        page.wait_for_selector("div.floorplan")
        
        # Simulate clicking each tab to reveal all floorplan content.
        tabs = page.query_selector_all("button[role='tab']")
        for tab in tabs:
            tab.click()
            page.wait_for_timeout(1000)  # Wait 1 second after each click
        
        # Scroll down to trigger lazy loading.
        page.evaluate("window.scrollBy(0, window.innerHeight)")
        page.wait_for_timeout(3000)  # Wait 3 seconds
        
        # Simulate mouse movement to help trigger any lazy-loaded events.
        page.mouse.move(500, 500)
        page.wait_for_timeout(1000)
        
        # Get the fully rendered page HTML.
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    sections = soup.find_all("div", class_="floorplan margin-pad big-bottom")
    print("Found floorplan sections:", len(sections))

    data = []

    for section in sections:
        try:
            # Attempt to find the title from an h2 or h4 element.
            raw_title = section.find("h2") or section.find("h4")
            if not raw_title:
                continue

            title_text = raw_title.get_text(strip=True).replace("*", "")
            print("Raw title:", title_text)
            normalized_title = title_text.replace(" ", "")

            # Use regex to extract bed and bath information.
            layout_match = re.search(r"(\d+)Bedroom(\d+)Bath", normalized_title, re.IGNORECASE)
            if layout_match:
                beds = int(layout_match.group(1))
                baths = int(layout_match.group(2))
                layout = f"{beds}x{baths}"
                name = f"University View - {layout} ({title_text})"
            elif "studio" in title_text.lower():
                beds = 0
                baths = 1
                layout = "Studio"
                name = "University View - Studio (Studio)"
            else:
                print("❌ Could not parse bed/bath:", title_text)
                continue

            # Extract price using our helper.
            price = extract_price(section)
            if price is None:
                print("❌ Missing price for:", title_text, "- including listing with missing price")
            else:
                print(f"✅ Parsed: {name} — ${price} — {beds}x{baths}")

            data.append({
                "Name": name,
                "Price": price,
                "Beds": beds,
                "Baths": baths,
                "Sqft": None,
                "Address": "8400 Baltimore Ave, College Park, MD 20740"
            })

        except Exception as e:
            print("🔥 Skipping listing due to error:", e)
            continue

    df = pd.DataFrame(data)
    print(f"✅ Scraped {len(df)} floorplans (including variations)")
    print(df[["Name", "Price", "Beds", "Baths"]])
    df.to_csv("apartments.csv", index=False)
    return df

if __name__ == "__main__":
    scrape_university_view()
