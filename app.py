import streamlit as st
import pandas as pd
from umd_schools import UMD_SCHOOLS
from distance import get_walking_time
from scrapers.view_scraper import scrape_and_extract_view  # 🔌 GPT-powered scraper

st.set_page_config(
    page_title="TerpNest | UMD Apartment Finder",
    page_icon="favicon.png",
    layout="wide"
)

# --- Load apartment listings from University View scraper ---
st.markdown("# TerpNest\n### The Smarter Way to Find UMD Housing")

with st.status("🔄 Scraping University View listings in real-time...", expanded=True) as status:
    try:
        df = scrape_and_extract_view()
        st.success(f"✅ Scraped {len(df)} listings from University View.")
        status.update(label="✅ Listings loaded", state="complete")
    except Exception as e:
        st.error("🚨 Failed to scrape apartment data.")
        st.exception(e)
        st.stop()

# --- Info Header ---
st.markdown("""
---
TerpNest is a free tool built by students, for students.
**What it does:**
- Aggregates real apartment listings near UMD
- Calculates **walking distance** to your school (Engineering, Business, Journalism, etc.)
- Lets you filter by **price, bedrooms, bathrooms, and square footage**
- Allows you to download results as a CSV file

**No more checking 10+ websites**. No more guessing how far you'll be walking in the rain.
---
**Get started below and find your next place to live. It's totally free.**
""")
st.markdown("---")
st.title("Explore Available Apartments")

# --- Validation ---
if df.empty or "price" not in df.columns:
    st.error("No apartment listings were found at this time. Please try again later.")
    st.stop()

# Normalize column names if needed
df.columns = [col.strip().capitalize() for col in df.columns]

# --- Sidebar Filters ---
st.sidebar.header("Filter Your Search")
school = st.sidebar.selectbox("Your UMD School (for walk time)", list(UMD_SCHOOLS.keys()))
min_beds = st.sidebar.selectbox("Minimum Bedrooms", [1, 2, 3, 4])
min_baths = st.sidebar.selectbox("Minimum Bathrooms", [1, 2, 3, 4])
price_limit = st.sidebar.slider("Max Price ($ per person)", 800, 2000, 1500)

# --- Apply Filters ---
filtered_df = df[
    ((df["Price"].isna()) | (df["Price"] <= price_limit)) &
    (df["Beds"] >= min_beds) &
    (df["Baths"] >= min_baths)
]

# --- Walk Time Calculation ---
destination = UMD_SCHOOLS[school]
filtered_df["Walk Time"] = filtered_df["Address"].apply(
    lambda addr: get_walking_time(addr, destination)
)

# --- Display Results ---
cols = ["Name", "Price", "Beds", "Baths", "Address", "Walk Time"]
display_df = filtered_df[cols].reset_index(drop=True)
st.write(f"Apartments filtered by price, bedrooms, and walking distance to **{school}**:")
st.data_editor(display_df, use_container_width=True, hide_index=True, disabled=True)

# --- Download CSV ---
csv = display_df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download CSV", data=csv, file_name="filtered_apartments.csv", mime="text/csv")
