# 🌍 Mapping Tomorrow: Pokhara Risk & Resource Dashboard

**Mapping Tomorrow** is a Streamlit-based geospatial application designed to visualize circular economy resources (waste/recycling points) and analyze their vulnerability to natural disasters (floods, landslides) in Pokhara, Nepal.

This tool demonstrates how OpenStreetMap (OSM) data can be leveraged for urban resilience planning.

## 🚀 Features

### 1. 2D Interactive Map
*   **Visualizes Key Data**: Displays waste/recycling points and hypothetical disaster risk zones on an interactive Folium map.
*   **Layer Controls**: Toggle visibility for "Waste & Recycling" points and "Risk Zones".
*   **Popups**: Click on any marker to see details (e.g., Amenity type, Name).

### 2. 3D Terrain & Density Visualization
*   **Immersive View**: Uses **PyDeck** to render a 3D visualization of the city.
*   **Satellite Imagery**: Overlays data on high-resolution satellite tiles (`Esri World Imagery`).
*   **Vertical Extrusion**:
    *   **Green Columns**: Represent waste/recycling points (height indicates a standard metric for visibility).
    *   **Red Cylinders**: Represent high-severity risk zones.

### 3. Vulnerability Analysis
*   **Spatial Join Logic**: Automatically performs a spatial intersection between waste resources and risk zones.
*   **Actionable Insights**: Identifies and lists specific recycling points that are at risk of being compromised (e.g., washed away in a flood), which is critical for disaster preparedness.

### 4. Citizen Reporting (Prototype)
*   **Feedback Loop**: A mock interface for citizens to report new hazards or unmanaged waste, demonstrating how crowdsourced data could feed back into the system.

---

## 🛠️ How It Works

The application creates a cohesive pipeline from data fetching to visualization:

### 1. Data Fetching (`utils.py`)
*   **OpenStreetMap Integration**: Uses the `osmnx` library to fetch real-time data from OSM.
    *   It queries for nodes with tags like `amenity=waste_basket`, `amenity=recycling`, etc.
    *   Data is cached using `@st.cache_data` to ensure fast load times on subsequent runs.
*   **Risk Zone Generation**: Since real-time risk data might not be available, the `create_risk_zones()` function generates **hypothetical** risk polygons (buffered points) around known hazard areas in Pokhara (e.g., Seti River Gorge) to demonstrate the analytics verification capability.

### 2. Spatial Analysis (`utils.py`)
*   The `perform_spatial_analysis()` function uses `geopandas.sjoin`.
*   It mathematically calculates if any "Waste Point" (Point geometry) lies within a "Risk Zone" (Polygon geometry).
*   The result is a filtered DataFrame of vulnerable resources displayed in the **Risk Analysis** tab.

### 3. Visualization (`app.py`)
*   **2D**: `folium` generates a Leaflet.js map.
*   **3D**: `pydeck` uses WebGL for high-performance 3D rendering. It maps the GeoDataFrame columns (lat/lon) to visual properties like color and elevation.

---

## 💻 Tech Stack

*   **Frontend**: [Streamlit](https://streamlit.io/) (Python web framework)
*   **Geospatial Data**: [OSMnx](https://osmnx.readthedocs.io/), [GeoPandas](https://geopandas.org/)
*   **Visualization**: [Folium](https://python-visualization.github.io/folium/) (2D), [PyDeck](https://deckgl.readthedocs.io/en/latest/) (3D)
*   **Data Source**: OpenStreetMap (OSM)

---

## 🏁 Getting Started

### Prerequisites
Ensure you have Python installed. It is recommended to use a virtual environment.

### 1. Install Dependencies
Run the following command to install the required Python packages:

```bash
pip install -r requirements.txt
```

*Note: You may also need `libspatialindex-dev` for Rtree dependencies depending on your OS.*

### 2. Run the Application
Navigate to the project directory and execute:

```bash
streamlit run app.py
```

The application will launch in your default web browser at `http://localhost:8501`.

---

## 📂 File Structure

*   `app.py`: The main entry point. Coordinates the UI layout, calls data functions, and renders maps.
*   `utils.py`: Helper functions for data fetching (`fetch_osm_data`), risk zone generation (`create_risk_zones`), and spatial analysis.
*   `requirements.txt`: List of Python dependencies.
