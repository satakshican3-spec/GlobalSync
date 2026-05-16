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
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlon = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return c * 6371

@st.cache_data
def fetch_global_data():
    try:
        response = requests.get("https://restcountries.com", timeout=10)
        return response.json()
    except:
        try:
            backup_url = "https://githubusercontent.com"
            response = requests.get(backup_url, timeout=10)
            data = response.json()
            for country in data:
                country['name'] = {'common': country['name']['common']}
                country['flags'] = {'png': country.get('flags', {}).get('png')}
            return data
        except:
            return None

countries_data = fetch_global_data()

if not countries_data:
    st.error("Connection Error: The global databases are currently unresponsive. Retrying...")
    if st.button("Refresh System Connection"):
        st.rerun()
    st.stop()

country_list = sorted([c['name']['common'] for c in countries_data])

st.sidebar.title("GlobalSync Explorer")
user_lat = st.sidebar.number_input("Your Latitude", value=51.0447, format="%.4f")
user_lon = st.sidebar.number_input("Your Longitude", value=-114.0719, format="%.4f")
search_selection = st.sidebar.selectbox("Select a Nation", country_list)

st.title("GlobalSync: Geographic Intelligence Portal")

if st.button("Spin the Globe", use_container_width=True):
    with st.spinner("Calculating trajectory..."):
        time.sleep(1)
        search_selection = random.choice(country_list)
        st.session_state.active_selection = search_selection

if 'active_selection' in st.session_state:
    search_selection = st.session_state.active_selection

selected_data = next(c for c in countries_data if c['name']['common'] == search_selection)
dest_coords = selected_data.get('latlng', [0, 0])
total_distance = calculate_distance(user_lat, user_lon, dest_coords[0], dest_coords[1])

st.write(f"### Current Intelligence Profile: {search_selection}")

m_col1, m_col2, m_col3, m_col4 = st.columns(4)
m_col1.metric("Capital", selected_data.get('capital', ['N/A'])[0])
m_col2.metric("Proximity (KM)", f"{total_distance:,.0f}")
m_col3.metric("Population", f"{selected_data.get('population', 0):,}")
m_col4.metric("Region", selected_data.get('region', 'N/A'))

st.divider()

tab_geo, tab_econ = st.tabs(["Geography", "Economics"])

with tab_geo:
    st.write("### Geographical Distribution")
    if selected_data['flags']['png']:
        st.image(selected_data['flags']['png'], width=300)
    map_data = pd.DataFrame({'lat': [dest_coords[0]], 'lon': [dest_coords[1]]})
    st.map(map_data, zoom=3)

with tab_econ:
    st.write("### Economic Indicators")
    st.write(f"United Nations Member: {'YES' if selected_data.get('unMember') else 'NO'}")
    st.write(f"Status: {selected_data.get('status', 'N/A').upper()}")

st.write("---")
st.caption("GlobalSync v1.1 | Professional Developer Suite")
