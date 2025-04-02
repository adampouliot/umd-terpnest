import streamlit as st
import pandas as pd
from umd_schools import UMD_SCHOOLS
from distance import get_walking_time

st.set_page_config(
    page_title="TerpNest | UMD Apartment Finder",
    page_icon="favicon.png",
    layout="wide"
)

# --- Load CSV ---
try:
    df = pd.read_csv("apartments.csv")

    # Clean columns: remove $ and convert price and $/sqft to numeric
    df["price"] = df["price"].replace('[\$,]', '', regex=True).astype(float)
    df["$/sqft"] = df["$/sqft"].replace('[\$,]', '', regex=True).astype(float)

except Exception as e:
    st.error("🚨 Failed to load apartment data.")
    st.exception(e)
    st.stop()

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

# --- Fallback check ---
# Normalize column names
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

if df.empty or "price" not in df.columns:
    st.error("No apartment listings were found at this time. Please try again later.")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("Filter Your Search")
school = st.sidebar.selectbox("Your UMD School (for walk time)", list(UMD_SCHOOLS.keys()))
min_beds = st.sidebar.selectbox("Minimum Bedrooms", sorted(df["beds"].unique()))
min_baths = st.sidebar.selectbox("Minimum Bathrooms", sorted(df["baths"].unique()))
price_limit = st.sidebar.slider("Max Price ($ per person)", 800, 3000, 1600)

# --- Apply Filters ---
filtered_df = df[
    (df["price"] <= price_limit) &
    (df["beds"] >= min_beds) &
    (df["baths"] >= min_baths)
].copy()

# --- Walk Time Calculation ---
destination = UMD_SCHOOLS[school]
filtered_df["walk time"] = filtered_df["address"].apply(
    lambda addr: get_walking_time(addr, destination)
)

# --- Display Columns ---
cols = ["name", "beds", "baths", "price", "sqft", "$/sqft", "address", "walk time"]
display_df = filtered_df[cols].reset_index(drop=True)

st.write(f"Apartments filtered by price, bedrooms, and walking distance to **{school}**:")
st.data_editor(display_df, use_container_width=True, hide_index=True, disabled=True)

# --- Optional CSV Download ---
st.download_button(
    label="Download CSV",
    data=display_df.to_csv(index=False),
    file_name="filtered_apartments.csv",
    mime="text/csv"
)
