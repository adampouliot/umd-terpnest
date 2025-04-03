import streamlit as st
import pandas as pd
import pydeck as pdk
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
    df["price"] = df["price"].replace('[\$,]', '', regex=True).astype(float)
    df["$/sqft"] = df["$/sqft"].replace('[\$,]', '', regex=True).astype(float)
except Exception as e:
    st.error("🚨 Failed to load apartment data.")
    st.exception(e)
    st.stop()

# --- Header ---
st.markdown("# TerpNest\n### The Smarter Way to Find UMD Apartments")

st.markdown("""
---
TerpNest is a free tool built by students, for students.

**What it does:**
- Aggregates real apartment listings near UMD
- Calculates **walking distance** to your school (Engineering, Business, Journalism, etc.)
- Lets you filter by **price, bedrooms, bathrooms, and square footage**
- Allows you to download results as a CSV file

**No more checking 10+ websites**. No more guessing how far you'll be walking in the rain.

**Get started below and find your next place to live. It's totally free.**
""")

st.markdown("---")
st.title("Explore Available Apartments")

# --- Fallback check ---
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

if df.empty or "price" not in df.columns:
    st.error("No apartment listings were found at this time. Please try again later.")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("Filter Your Search")
school = st.sidebar.selectbox("Your UMD School (for walk time)", list(UMD_SCHOOLS.keys()))
bedroom_options = sorted(df["beds"].dropna().unique())
selected_beds = st.sidebar.multiselect("Select Bedrooms", bedroom_options, default=bedroom_options)
bathroom_options = sorted(df["baths"].dropna().unique())
selected_baths = st.sidebar.multiselect("Select Bathrooms", bathroom_options, default=bathroom_options)
price_limit = st.sidebar.slider("Max Price ($ per person)", 800, 3000, 1600)
min_sqft = int(df["sqft"].min())
max_sqft = int(df["sqft"].max())
sqft_range = st.sidebar.slider("Square Footage Range", min_sqft, max_sqft, (min_sqft, max_sqft))

# --- Apply Filters ---
filtered_df = df[
    (df["price"] <= price_limit) &
    (df["beds"].isin(selected_beds)) &
    (df["baths"].isin(selected_baths)) &
    (df["sqft"] >= sqft_range[0]) &
    (df["sqft"] <= sqft_range[1])
].copy()

# --- Walk Time ---
destination = UMD_SCHOOLS[school]
filtered_df["walk time"] = filtered_df["address"].apply(lambda addr: get_walking_time(addr, destination))

# --- Display Table ---
cols = ["name", "beds", "baths", "price", "sqft", "$/sqft", "address", "walk time"]
display_df = filtered_df[cols].reset_index(drop=True)

# Format Display
clean_df = display_df.copy()
clean_df["beds"] = clean_df["beds"].apply(lambda x: f"{x:.1f}".rstrip('0').rstrip('.') if x % 1 else str(int(x)))
clean_df["baths"] = clean_df["baths"].apply(lambda x: f"{x:.1f}".rstrip('0').rstrip('.') if x % 1 else str(int(x)))
clean_df["price"] = clean_df["price"].apply(lambda x: f"${int(round(x)):,}")
clean_df["sqft"] = clean_df["sqft"].apply(lambda x: f"{int(round(x)):,}")
clean_df["$/sqft"] = clean_df["$/sqft"].apply(lambda x: f"{x:.2f}")

def style_walk_time(val):
    try:
        minutes = int(str(val).split()[0])
    except:
        return "color: black"
    if minutes < 15:
        return "color: green"
    elif minutes <= 20:
        return "color: orange"
    else:
        return "color: red"

styled_df = clean_df.style.applymap(style_walk_time, subset=["walk time"])
st.write(f"Apartments filtered by price, bedrooms, and walking distance to **{school}**:")
st.dataframe(styled_df, use_container_width=True, hide_index=True)

# --- CSV Download ---
st.download_button(
    label="Download CSV",
    data=display_df.to_csv(index=False),
    file_name="filtered_apartments.csv",
    mime="text/csv"
)

# --- Apartment Coordinates and URLs ---
apartment_locations = pd.DataFrame([
    {"name": "University View", "lat": 38.99246, "lon": -76.93402, "url": "https://live-theview.com"},
    {"name": "The Varsity", "lat": 38.99144, "lon": -76.93427, "url": "https://www.varsitycollegepark.com"},
    {"name": "Tempo", "lat": 38.99504, "lon": -76.93273, "url": "https://tempocollegepark.com"},
    {"name": "Terrapin Row", "lat": 38.98059, "lon": -76.94191, "url": "https://www.terrapinrow.com"},
    {"name": "Union on Knox", "lat": 38.98132, "lon": -76.93899, "url": "https://www.uniononknox.com"},
    {"name": "The Standard", "lat": 38.97958, "lon": -76.94001, "url": "https://www.thestandardcollegepark.com"},
    {"name": "Aspen Heights", "lat": 38.98145, "lon": -76.94365, "url": "https://www.aspencollegepark.com"},
    {"name": "Landmark", "lat": 38.98237, "lon": -76.93684, "url": "https://www.landmarkcollegepark.com"},
    {"name": "Hub College Park", "lat": 38.98138, "lon": -76.94333, "url": "https://huboncampus.com/college-park"},
])

# --- Pydeck Interactive Map with clickable markers ---
st.markdown("## Apartment Map View")

layer = pdk.Layer(
    "ScatterplotLayer",
    apartment_locations,
    pickable=True,
    get_position='[lon, lat]',
    get_fill_color='[200, 30, 0, 160]',
    get_radius=60,
)

tooltip = {
    "html": "<b>{name}</b><br><a href='{url}' target='_blank'>Visit Website</a>",
    "style": {"backgroundColor": "steelblue", "color": "white"}
}

view_state = pdk.ViewState(latitude=38.9869, longitude=-76.9444, zoom=14)

st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/dark-v11",
    initial_view_state=view_state,
    layers=[layer],
    tooltip=tooltip
))

# --- Notes ---
st.markdown("""
---
### Notes on the Data

- Prices reflected **may not** include monthly utilities charges and additional fees  
- **Beds = 0** → Studio apartment (no separate bedroom)  
- **Beds = 0.5** → Shared bedroom (typically 2 people sharing a room)  
- **$/sqft** → Rent cost per square foot  
- **Walk Time** → Estimated walk from apartment to your selected UMD school  

This data is pulled directly from apartment websites near UMD and refreshed regularly.
""")

# --- Apartment Website Links ---
st.markdown("""
---
### Apartment Websites

- [University View](https://live-theview.com)  
- [The Varsity](https://www.varsitycollegepark.com)  
- [Tempo](https://tempocollegepark.com/)  
- [Terrapin Row](https://www.terrapinrow.com)  
- [Union on Knox](https://www.uniononknox.com)  
- [The Standard](https://www.thestandardcollegepark.com/)  
- [Aspen Heights](https://www.aspencollegepark.com/)  
- [Landmark](https://www.landmarkcollegepark.com)  
- [Hub College Park](https://huboncampus.com/college-park/)
""")
