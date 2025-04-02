import streamlit as st
st.set_page_config(
    page_title="TerpNest | UMD Apartment Finder",
    page_icon="favicon.png",
    layout="wide"
)

import pandas as pd
from umd_schools import UMD_SCHOOLS
from scraper_view import scrape_university_view
from distance import get_walking_time

@st.cache_data(ttl=3600)
def get_apartment_data():
    try:
        df = scrape_university_view()
        st.write("✅ Scraper ran successfully. Sample data:")
        st.write(df.head())  # TEMP: Debug preview
        return df
    except Exception as e:
        st.error("🚨 Scraper failed to load data.")
        st.exception(e)
        return pd.DataFrame()

# --- Load apartment data ---
df = get_apartment_data()

# --- Header ---
st.markdown("# TerpNest\n### The Smarter Way to Find UMD Housing")

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

# --- Fallback if scraper returned nothing ---
if df.empty or "Price" not in df.columns:
    st.error("No apartment listings were found at this time. Please try again later.")
    st.stop()

# --- Sidebar filters ---
st.sidebar.header("Filter Your Search")

school = st.sidebar.selectbox(
    "Your UMD School (for walk time)",
    list(UMD_SCHOOLS.keys()),
    help="We'll estimate walking distance from each apartment to this location."
)

st.sidebar.subheader("Apartment Preferences")
min_beds = st.sidebar.selectbox("Minimum Bedrooms", [1, 2, 3, 4])
min_baths = st.sidebar.selectbox("Minimum Bathrooms", [1, 2, 3, 4])

st.sidebar.subheader("Price Limit")
price_limit = st.sidebar.slider("Max Price ($ per person)", 800, 2000, 1500)

# --- Apply filters ---
filtered_df = df[
    (df["Price"] <= price_limit) &
    (df["Beds"] >= min_beds) &
    (df["Baths"] >= min_baths)
]

# --- Add walk time column ---
destination = UMD_SCHOOLS[school]
filtered_df["Walk Time"] = filtered_df["Address"].apply(
    lambda addr: get_walking_time(addr, destination)
)

# --- Display results ---
cols = ["Name", "Price", "Beds", "Baths", "Sqft", "Walk Time"]
display_df = filtered_df[cols].reset_index(drop=True)

st.write(f"Apartments filtered by price, bedrooms, and walking distance to **{school}**:")
st.data_editor(display_df, use_container_width=True, hide_index=True, disabled=True)
