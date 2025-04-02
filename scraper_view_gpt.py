import os
import openai
import instructor
import streamlit as st
import pandas as pd
from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from typing import Optional, List

# 🔑 API KEYS
openai.api_key = os.getenv("OPENAI_API_KEY")
firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")

# ✅ GPT setup with Instructor
client = instructor.from_openai(openai.OpenAI(api_key=openai.api_key))

# ✅ Pydantic model for apartment listings
class Apartment(BaseModel):
    name: str = Field(..., description="Name of the apartment or layout (e.g., 4x2, Studio)")
    beds: int = Field(..., description="Number of bedrooms")
    baths: int = Field(..., description="Number of bathrooms")
    price: Optional[int] = Field(None, description="Price per person in USD")
    address: str = Field(default="8400 Baltimore Ave, College Park, MD 20740")

# ✅ Firecrawl setup
app = FirecrawlApp(api_key=firecrawl_api_key)

def scrape_and_extract():
    url = "https://live-theview.com/rates-floorplans/"
    st.info(f"🔗 Scraping markdown from: {url}")
    firecrawl_data = app.scrape_url(url)
    markdown = firecrawl_data.get("markdown", "")

    if not markdown:
        st.error("❌ Firecrawl failed to retrieve markdown content.")
        return []

    st.info("🧠 Extracting structured apartment data with GPT...")
    apartments: List[Apartment] = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_model=List[Apartment],
        messages=[{"role": "user", "content": markdown}]
    )
    
    return apartments

# ✅ Streamlit UI
st.set_page_config(page_title="University View Scraper", layout="centered")
st.title("🏢 University View Apartment Listings")

if st.button("🔍 Scrape Listings"):
    try:
        listings = scrape_and_extract()
        df = pd.DataFrame([a.dict() for a in listings])
        st.success(f"✅ Extracted {len(df)} listings.")
        st.dataframe(df)
        df.to_csv("apartments.csv", index=False)
        st.download_button("⬇️ Download CSV", df.to_csv(index=False), "apartments.csv", "text/csv")
    except Exception as e:
        st.exception(e)
