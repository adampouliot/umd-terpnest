# scraper_view.py
import pandas as pd
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

    # Grab all floorplan cards
    all_cards = soup.find_all("div", class_="floorplan margin-pad big-bottom")
    print("Found floorplan sections:", len(all_cards))

    data = []
    for card in all_cards:
        try:
            container = card.find_parent("div", class_="floorplan") or card
            title_el = container.find("h4", class_="rate")
            price_el = container.find("span", class_="special-rates")

            if not title_el or not price_el:
                continue

            title = title_el.get_text(strip=True).replace("*", "")
            price = int(price_el.get_text(strip=True).replace("$", "").replace(",", ""))

            # Default parsing fallback
            beds, baths = 0, 1
            if "studio" not in title.lower():
                # e.g. "4 Bedroom 4 Bath"
                parts = title.lower().split("bedroom")
                if len(parts) >= 2:
                    beds = int(parts[0].strip())
                    baths = int(parts[1].split("bath")[0].strip())

            name_cleaned = "University View - " + title.replace("Download Floorplan PDF", "").strip()

            data.append({
                "Name": name_cleaned,
                "Price": price,
                "Beds": beds,
                "Baths": baths,
                "Sqft": None,
                "Address": "8400 Baltimore Ave, College Park, MD 20740"
            })

        except Exception as e:
            print("Skipping due to error:", e)
            continue

    df = pd.DataFrame(data).drop_duplicates()
    print(f"✅ Scraped {len(df)} unique floorplans")
    print(df[["Name", "Price", "Beds", "Baths"]])

    df.to_csv("apartments.csv", index=False)
    return df

if __name__ == "__main__":
    scrape_university_view()
