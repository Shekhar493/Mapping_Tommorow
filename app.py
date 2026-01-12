import streamlit as st
import folium
from streamlit_folium import st_folium
import pydeck as pdk
import geopandas as gpd
from utils import fetch_osm_data, create_risk_zones, perform_spatial_analysis

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Mapping Tomorrow - Pokhara",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for aesthetics
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1 {
        color: #2E86C1;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #2E86C1;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Openstreetmap_logo.svg/1024px-Openstreetmap_logo.svg.png", width=80)
    st.title("Mapping Tomorrow")
    st.subheader("Settings")
    
    layer_waste = st.checkbox("Show Waste/Recycling Points", value=True)
    layer_risk = st.checkbox("Show Disaster Risk Zones", value=True)
    
    st.divider()
    st.markdown("### About")
    st.info(
        "This dashboard visualizes disaster risks and circular economy resources "
        "in Pokhara using OpenStreetMap data."
    )

# --- MAIN DATA FETCHING ---
place_name = "Pokhara, Nepal"
waste_tags = {"amenity": ["waste_basket", "recycling", "waste_transfer_station"]}

with st.spinner(f"Fetching latest data for {place_name}..."):
    waste_gdf = fetch_osm_data(place_name, waste_tags)
    risk_gdf = create_risk_zones()

# Analysis
risk_waste = perform_spatial_analysis(waste_gdf, risk_gdf)

# --- HEADER ---
st.title("🌍 Mapping Tomorrow: Pokhara")
st.markdown("### Safer Communities, Greener Future")

# --- METRICS ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Waste/Recycling Points", value=len(waste_gdf))
with col2:
    st.metric(label="Identified Risk Zones", value=len(risk_gdf))
with col3:
    st.metric(label="Points in Risk Areas", value=len(risk_waste), delta=f"{len(risk_waste)/len(waste_gdf)*100:.1f}% of total" if len(waste_gdf)>0 else "0%")

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["🗺️ 2D Interactive Map", "🏙️ 3D Visualization", "📊 Risk Analysis", "📢 Report Issue"])

# --- TAB 1: 2D MAP ---
with tab1:
    st.subheader("City Overview")
    
    # Base map
    m = folium.Map(location=[28.2096, 83.9856], zoom_start=13, tiles="CartoDB positron")
    
    # Waste Layer
    if layer_waste and not waste_gdf.empty:
        waste_fg = folium.FeatureGroup(name="Waste & Recycling")
        for idx, row in waste_gdf.iterrows():
            # Get geometry coordinates
            lat = row.geometry.y
            lon = row.geometry.x
            
            # Popup content
            popup_html = f"<b>Type:</b> {row['amenity']}<br>"
            if 'name' in row and str(row['name']) != 'nan':
                 popup_html += f"<b>Name:</b> {row['name']}"
            
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=200),
                icon=folium.Icon(color="green", icon="recycle", prefix="fa"),
                tooltip="Waste/Recycling Point"
            ).add_to(waste_fg)
        waste_fg.add_to(m)

    # Risk Layer
    if layer_risk and not risk_gdf.empty:
        risk_fg = folium.FeatureGroup(name="Risk Zones")
        for idx, row in risk_gdf.iterrows():
            color = "red" if "Flood" in row["risk_type"] else "orange"
            folium.GeoJson(
                row.geometry,
                style_function=lambda x, color=color: {
                    "fillColor": color,
                    "color": color,
                    "weight": 2,
                    "fillOpacity": 0.3
                },
                tooltip=f"⚠ {row['risk_type']}"
            ).add_to(risk_fg)
        risk_fg.add_to(m)

    folium.LayerControl().add_to(m)
    st_folium(m, width="100%", height=500)

# --- TAB 2: 3D VISUALIZATION ---
with tab2:
    st.subheader("3D Terrain & Density View")
    
    if not waste_gdf.empty and not risk_gdf.empty:
        # Prepare data for PyDeck
        waste_3d = waste_gdf.copy()
        waste_3d["lat"] = waste_3d.geometry.y
        waste_3d["lon"] = waste_3d.geometry.x
        
        # Centroids for risk zones
        risk_3d = risk_gdf.copy()
        risk_3d["lat"] = risk_3d.geometry.centroid.y
        risk_3d["lon"] = risk_3d.geometry.centroid.x
        
        # Layers
        layers = []
        
        # Satellite Basemap Layer (Esri World Imagery)
        satellite_layer = pdk.Layer(
            "TileLayer",
            data=["https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"],
            min_zoom=0,
            max_zoom=19,
            tile_size=256,
        )
        layers.append(satellite_layer)
        
        if layer_waste:
            waste_layer = pdk.Layer(
                "ColumnLayer",
                data=waste_3d,
                get_position=["lon", "lat"],
                get_elevation=50,
                elevation_scale=10,
                radius=30,
                get_fill_color=[0, 255, 100, 200], # Neon Green for contrast
                pickable=True,
                auto_highlight=True,
            )
            layers.append(waste_layer)
            
        if layer_risk:
            # Using Scatterplot for zones in 3D (simplified representation)
            risk_layer = pdk.Layer(
                "ViolinplotLayer",
                data=risk_3d,
                get_position=["lon", "lat"],
                get_radius=1000,
                get_fill_color=[255, 50, 50, 100],
                stroked=True,
                get_line_color=[255, 0, 0, 200],
                get_line_width=20,
                pickable=True,
            )
            layers.append(risk_layer)

        # Deck
        view_state = pdk.ViewState(
            latitude=28.2096,
            longitude=83.9856,
            zoom=12,
            pitch=50,
        )
        
        r = pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            tooltip={"text": "Feature Location"},
            map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
        )
        
        st.pydeck_chart(r)
    else:
        st.warning("No data available for 3D view.")

# --- TAB 3: ANALYSIS ---
with tab3:
    st.subheader("Vulnerability Analysis")
    if not risk_waste.empty:
        st.markdown("The following waste management resources are located in **High Risk Zones**:")
        
        # Clean up table for display
        display_cols = ['amenity', 'risk_type', 'name']
        # Add name if missing
        if 'name' not in risk_waste.columns:
            risk_waste['name'] = "Unknown"
        else:
             risk_waste['name'] = risk_waste['name'].fillna("Unknown")
             
        cols_to_show = [c for c in display_cols if c in risk_waste.columns]
        
        st.dataframe(risk_waste[cols_to_show], use_container_width=True)
        
        st.warning(f"⚠ Critical Insight: {len(risk_waste)} recycling points are at risk of being compromised during a disaster.")
    else:
        st.success("Analysis complete: No waste resources found in the currently defined high-risk zones.")

# --- TAB 4: REPORT ISSUE ---
with tab4:
    st.subheader("Citizen Reporting Prototype")
    st.markdown("Report unmanaged waste or new hazard zones.")
    
    with st.form("report_form"):
        report_type = st.selectbox("Issue Type", ["Unmanaged Waste", "Landslide Risk", "Flood Prone Area", "Other"])
        description = st.text_area("Description", placeholder="Describe the issue...")
        coords = st.text_input("Location (Coordinates or Landmark)", placeholder="e.g., Near Lakeside Market")
        
        submitted = st.form_submit_button("Submit Report")
        
        if submitted:
            st.success("✅ Report submitted successfully! This data would be sent to the backend database in a production environment.")
            st.balloons()



