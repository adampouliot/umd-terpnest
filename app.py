import streamlit as st
import pandas as pd
from umd_schools import UMD_SCHOOLS
from distance import get_walking_time

st.title("UMD Apartment Aggregator")

# Load apartment data
df = pd.read_csv("apartments.csv")

# Filters
st.sidebar.header("Filter Your Search")
price_limit = st.sidebar.slider("Max Price ($)", 800, 2000, 1500)
min_beds = st.sidebar.selectbox("Minimum Bedrooms", [1, 2, 3, 4])
school = st.sidebar.selectbox("Your UMD School", list(UMD_SCHOOLS.keys()))

# Filter listings
filtered_df = df[(df["Price"] <= price_limit) & (df["Beds"] >= min_beds)]

# Add walking time column
destination = UMD_SCHOOLS[school]
filtered_df["Walk Time"] = filtered_df["Address"].apply(
    lambda addr: get_walking_time(addr, destination)
)

st.write(f"Apartments filtered by price, bedrooms, and walking distance to {school}:")
st.dataframe(filtered_df)
