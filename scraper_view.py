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

            raw_title = title_el.get_text(strip=True).replace("*", "")
            raw_price = price_el.get_text(strip=True).replace("*", "")

            # Extract latest price (e.g., "$1,269 $1,199" => 1199)
            price_match = re.findall(r"\$([\d,]+)", raw_price)
            if not price_match:
                continue
            price = int(price_match[-1].replace(",", ""))

            # Extract bed/bath from the title
            beds, baths = 0, 1
            bed_match = re.search(r"(\d+)\s*bed", raw_title, re.IGNORECASE)
            bath_match = re.search(r"(\d+)\s*bath", raw_title, re.IGNORECASE)
            if bed_match:
                beds = int(bed_match.group(1))
            if bath_match:
                baths = int(bath_match.group(1))

            name = "University View - " + raw_title.split("$")[0].strip()

            data.append({
                "Name": name,
                "Price": price,
                "Beds": beds,
                "Baths": baths,
                "Sqft": None,
                "Address": "8400 Baltimore Ave, College Park, MD 20740"
            })

        except Exception as e:
            print("Skipping a listing due to error:", e)
            continue

    df = pd.DataFrame(data).drop_duplicates()
    print(f"✅ Scraped {len(df)} unique floorplans")
    print(df[["Name", "Price", "Beds", "Baths"]])

    df.to_csv("apartments.csv", index=False)
    return df

if __name__ == "__main__":
    scrape_university_view()
