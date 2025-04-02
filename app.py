import streamlit as st

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
- Shows you the **best deals instantly**

**No more checking 10 websites**. No more guessing how far you'll be walking in the rain.

---

**Get started below and find your next place to live. It's totally free.**
""")

import pandas as pd
from umd_schools import UMD_SCHOOLS
from distance import get_walking_time
st.markdown("---")

st.title("Explore Available Apartments")

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

# Add Google Maps walking directions links
filtered_df["Walk Link"] = filtered_df["Address"].apply(
    lambda addr: f"https://www.google.com/maps/dir/?api=1&destination={addr.replace(' ', '+')}&travelmode=walking"
)

# Hardcoded apartment site links
apartment_links = {
    "University View": "https://live-theview.com",
    "Landmark": "https://landmarkcollegepark.com",
    "The Varsity": "https://www.varsitycollegepark.com",
    "Terrapin Row": "https://www.terrapinrow.com",
    "Union on Knox": "https://www.uniononknox.com",
    "The Standard": "https://www.thestandardcollegepark.com",
}

def find_link(name):
    for keyword, url in apartment_links.items():
        if keyword.lower() in name.lower():
            return url
    return ""

filtered_df["Website"] = filtered_df["Name"].apply(find_link)

# Build display version of the dataframe with markdown links
display_df = filtered_df.copy()
display_df["Name"] = display_df.apply(
    lambda row: f"[{row['Name']}]({row['Website']})", axis=1
)
display_df["Walk Time"] = display_df.apply(
    lambda row: f"[{row['Walk Time']}]({row['Walk Link']})", axis=1
)

# Final display
st.write(f"Apartments filtered by price, bedrooms, and walking distance to {school}:")
cols = ["Name", "Price", "Beds", "Baths", "Sqft", "Walk Time"]
import streamlit.components.v1 as components

html_table = "<table><thead><tr>"
for col in cols:
    html_table += f"<th>{col}</th>"
html_table += "</tr></thead><tbody>"

for _, row in display_df[cols].iterrows():
    html_table += "<tr>"
    for col in cols:
        value = row[col]
        if isinstance(value, str) and value.startswith("["):
            # It's a markdown link like [Name](URL), convert to HTML
            label = value.split("](")[0][1:]
            url = value.split("](")[1][:-1]
            value = f'<a href="{url}" target="_blank">{label}</a>'
        html_table += f"<td>{value}</td>"
    html_table += "</tr>"

html_table += "</tbody></table>"

st.write("### 📊 Sortable Apartment Table")
components.html(f"""
<div style="overflow-x: auto">
    <style>
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            border: 1px solid #444;
            padding: 0.5rem;
            text-align: left;
        }}
        th {{
            background-color: #111;
            color: #fff;
        }}
    </style>
    {html_table}
</div>
""", height=600, scrolling=True)
