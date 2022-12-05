import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from shapely import wkt
import streamlit as st

st.set_page_config(layout="wide")

@st.cache
def load_data():
    access_df = pd.read_csv("/Users/feliphlvo/Documents/Minerva/Capstone/data/local/access_df.csv",index_col=0)
    access_df = gpd.GeoDataFrame(access_df, geometry = access_df["geometry"].apply(wkt.loads), crs = "EPSG:5641")
    access_df = access_df.to_crs(epsg=4326)
    return access_df

def plot_map(city_name, metric):
    subset_df = access_df[access_df["city_name"] == city_name]
    # Get latitude and longitude of the first observation
    center = {"lat": subset_df["geometry"].iloc[0].centroid.y, "lon": subset_df["geometry"].iloc[0].centroid.x}

    fig = px.choropleth_mapbox(subset_df, geojson=subset_df, locations=subset_df.index, color=metric,
                           mapbox_style="open-street-map", opacity=0.5, center=center, zoom=9.5,
                           hover_data=["city_name"], width=1000, height=800, labels={metric: "Supply of High School Teachers"})
    fig.update_layout(title_text="title", margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=800)
    st.plotly_chart(fig, use_container_width=True)

access_df = load_data()



# col1, col2 = st.columns(2)

city = st.selectbox("Select a city", access_df["city_name"].unique())

metric = st.selectbox("Select a metric", ["3sfca_n_classes", "3sfca_n_teachers"])




plot_map(city, metric)

