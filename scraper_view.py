# scraper_view.py
import pandas as pd
import re
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def scrape_university_view():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://live-theview.com/rates-floorplans/", wait_until="networkidle")
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    sections = soup.find_all("div", class_="floorplan margin-pad big-bottom")
    print("Found floorplan sections:", len(sections))

    data = []

    for section in sections:
        try:
            # Extract title (e.g., "4 Bedroom2 Bath", "Studio")
            raw_title = section.find("h2") or section.find("h4")
            if not raw_title:
                continue

            title_text = raw_title.get_text(strip=True).replace("*", "")
            print("Raw title:", title_text)

            # Normalize for matching (remove all spaces)
            normalized_title = title_text.replace(" ", "")

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
                print("Could not parse bed/bath:", title_text)
                continue

            # Get price
            price_el = section.find("span", class_="special-rates")
            if not price_el:
                continue
            price = int(price_el.get_text(strip=True).replace("$", "").replace(",", ""))

            data.append({
                "Name": name,
                "Price": price,
                "Beds": beds,
                "Baths": baths,
                "Sqft": None,
                "Address": "8400 Baltimore Ave, College Park, MD 20740"
            })

        except Exception as e:
            print("Skipping listing due to error:", e)
            continue

    df = pd.DataFrame(data)
    print(f"✅ Scraped {len(df)} floorplans (including variations)")
    print(df[["Name", "Price", "Beds", "Baths"]])

    df.to_csv("apartments.csv", index=False)
    return df

if __name__ == "__main__":
    scrape_university_view()
