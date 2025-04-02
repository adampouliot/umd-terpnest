import streamlit as st
import pandas as pd
from umd_schools import UMD_SCHOOLS
from distance import get_walking_time

st.set_page_config(
    page_title="TerpNest | UMD Apartment Finder",
    layout="wide"
)

st.title("Welcome to TerpNest")
st.subheader("Find the Perfect Apartment Near UMD — All in One Place")

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

# Load data
df = pd.read_csv("apartments.csv")

# Sidebar filters
st.sidebar.header("Filter Your Search")
price_limit = st.sidebar.slider("Max Price ($)", 800, 2000, 1500)
min_beds = st.sidebar.selectbox("Minimum Bedrooms", [1, 2, 3, 4])
school = st.sidebar.selectbox("Your UMD School", list(UMD_SCHOOLS.keys()))

# Filter
filtered_df = df[(df["Price"] <= price_limit) & (df["Beds"] >= min_beds)]

# Add walk time column
destination = UMD_SCHOOLS[school]
filtered_df["Walk Time"] = filtered_df["Address"].apply(
    lambda addr: get_walking_time(addr, destination)
)

# Define columns to show
cols = ["Name", "Price", "Beds", "Baths", "Sqft", "Walk Time"]
display_df = filtered_df[cols].reset_index(drop=True)

# Final table
st.write(f"Apartments filtered by price, bedrooms, and walking distance to **{school}**:")
st.data_editor(display_df, use_container_width=True, hide_index=True, disabled=True)
