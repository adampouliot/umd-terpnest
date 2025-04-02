import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_university_view():
    url = "https://live-theview.com/rates-floorplans/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    data = []

    cards = soup.find_all("div", class_="floor-plan-card")

    for card in cards:
        try:
            name = card.find("h3").text.strip()
            bedbath = card.find("span", class_="beds").text.strip()
            price = card.find("span", class_="rate").text.strip().replace("Starting at", "").strip().replace("$", "").replace(",", "")
            sqft = card.find("span", class_="sqft").text.strip().replace("Sq Ft", "").strip()

            beds, baths = bedbath.split("/")

            data.append({
                "Name": f"University View - {name}",
                "Price": int(price),
                "Beds": int(beds.strip().split()[0]),
                "Baths": int(baths.strip().split()[0]),
                "Sqft": int(sqft),
                "Address": "8400 Baltimore Ave, College Park, MD 20740"
            })
        except Exception as e:
            print("Skipping a listing due to error:", e)
            continue

    return pd.DataFrame(data)
if __name__ == "__main__":
    df = scrape_university_view()
    print(df)
