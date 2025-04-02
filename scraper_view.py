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

    # Get each floorplan section
    sections = soup.find_all("div", class_="floorplan margin-pad big-bottom")
    print("Found floorplan sections:", len(sections))

    data = []

    for section in sections:
        try:
            title_tag = section.find("h2")
            price_tag = section.find("span", class_="special-rates")

            if not title_tag or not price_tag:
                continue

            title = title_tag.get_text(strip=True)

            # Infer bed/bath count
            if "Studio" in title:
                beds = 0
                baths = 1
            else:
                try:
                    beds = int(title.split(" Bedroom")[0].strip())
                    baths = int(title.split(" Bedroom")[1].split(" Bath")[0].strip())
                except:
                    beds, baths = None, None  # fallback if parsing fails

            price = int(price_tag.get_text(strip=True).replace("$", "").replace(",", ""))

            data.append({
                "Name": f"University View - {title}",
                "Price": price,
                "Beds": beds,
                "Baths": baths,
                "Sqft": None,
                "Address": "8400 Baltimore Ave, College Park, MD 20740"
            })

        except Exception as e:
            print("Skipping section due to error:", e)
            continue

    df = pd.DataFrame(data)
    df.drop_duplicates(subset=["Name", "Price"], inplace=True)
    print(f"✅ Scraped {len(df)} unique floorplans")
    df.to_csv("apartments.csv", index=False)
    return df

# Local debug
if __name__ == "__main__":
    df = scrape_university_view()
    print(df)
