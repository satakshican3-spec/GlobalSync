import streamlit as st
import pandas as pd
import requests
import random
import time
from math import radians, cos, sin, asin, sqrt

st.set_page_config(page_title="GlobalSync", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
    }
    .stMetric {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculates the great-circle distance between two points in kilometers."""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlon = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r

@st.cache_data
def fetch_global_data():
    try:
        response = requests.get("https://restcountries.com")
        return response.json()
    except:
        return None

countries_data = fetch_global_data()

if countries_data:
    country_list = sorted([c['name']['common'] for c in countries_data])
else:
    st.error("Unable to connect to the global database. Please check your connection.")
    st.stop()

st.sidebar.title("GlobalSync Explorer")
st.sidebar.write("User Coordinates")
user_lat = st.sidebar.number_input("Your Latitude", value=51.0447, format="%.4f")
user_lon = st.sidebar.number_input("Your Longitude", value=-114.0719, format="%.4f")

search_selection = st.sidebar.selectbox("Select a Nation", country_list)

st.title("GlobalSync: Geographic Intelligence Portal")

if st.button("Spin the Globe", use_container_width=True):
    with st.spinner("Calculating trajectory to random coordinates..."):
        time.sleep(1.2)
        search_selection = random.choice(country_list)
        st.session_state.active_selection = search_selection

if 'active_selection' in st.session_state:
    search_selection = st.session_state.active_selection

selected_data = next(c for c in countries_data if c['name']['common'] == search_selection)
dest_lat, dest_lon = selected_data.get('latlng', [0, 0])

total_distance = calculate_distance(user_lat, user_lon, dest_lat, dest_lon)

st.write(f"### Current Intelligence Profile: {search_selection}")

col_meta1, col_meta2 = st.columns([1, 2])
with col_meta1:
    st.image(selected_data['flags']['png'], width=350)
with col_meta2:
    m_col1, m_col2 = st.columns(2)
    m_col1.metric("Capital City", selected_data.get('capital', ['N/A'])[0])
    m_col2.metric("Proximity (KM)", f"{total_distance:,.0f} km")

    m_col3, m_col4 = st.columns(2)
    m_col3.metric("Total Population", f"{selected_data.get('population', 0):,}")
    m_col4.metric("Region", selected_data.get('region', 'N/A'))

st.divider()

tab_geo, tab_econ, tab_hist = st.tabs(["Geography", "Economics", "History"])

with tab_geo:
    st.write("### Geographical Distribution")
    st.write(f"Official Designation: {selected_data['name'].get('official', 'N/A')}")
    st.write(f"Land Mass: {selected_data.get('area', 0):,} square kilometers")

    map_data = pd.DataFrame({'lat': [dest_lat], 'lon': [dest_lon]})
    st.map(map_data, zoom=3)

with tab_econ:
    st.write("### Economic Indicators")
    currencies = selected_data.get('currencies', {})
    if currencies:
        curr_code = list(currencies.keys())[0]
        st.write(f"Primary Currency: {currencies[curr_code].get('name')} ({curr_code})")

    st.write(f"Driving Orientation: {selected_data.get('car', {}).get('side', 'N/A').upper()}")
    st.write(f"United Nations Member: {'YES' if selected_data.get('unMember') else 'NO'}")

with tab_hist:
    st.write("### Historical Documentation")
    st.write(f"Accessing external research databases for {search_selection}...")
    wiki_link = f"https://wikipedia.org{search_selection.replace(' ', '_')}"
    st.link_button("Access Full Historical Records", wiki_link, use_container_width=True)

st.write("---")
st.caption("GlobalSync v1.0 | Calgary Portfolio Project Asset")
