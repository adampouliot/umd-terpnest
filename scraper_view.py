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
    floorplans = soup.select("div.floorplan.margin-pad.big-bottom")

    print("Found floorplan sections:", len(floorplans))

    data = []
    seen_names = set()

    for section in floorplans:
        try:
            title_el = section.find("h4", class_="rate")
            price_el = section.find("span", class_="special-rates")

            if not title_el or not price_el:
                continue

            name = title_el.get_text(strip=True)
            if name in seen_names:
                continue  # skip duplicates
            seen_names.add(name)

            price = int(price_el.get_text(strip=True).replace("$", "").replace(",", "").split("*")[-1])

            # Extract bed/bath count heuristically from name
            name_lower = name.lower()
            if "studio" in name_lower:
                beds = 0
                baths = 1
            else:
                beds = next((int(x) for x in name_lower.split() if x.isdigit()), None)
                baths = beds if beds else 1

            data.append({
                "Name": f"University View - {name}",
                "Price": price,
                "Beds": beds,
                "Baths": baths,
                "Sqft": None,
                "Address": "8400 Baltimore Ave, College Park, MD 20740"
            })

        except Exception as e:
            print("Skipping a listing due to error:", e)
            continue

    df = pd.DataFrame(data)
    print(f"✅ Scraped {len(df)} unique floorplans")
    df.to_csv("apartments.csv", index=False)
    return df

if __name__ == "__main__":
    df = scrape_university_view()
    print(df)
