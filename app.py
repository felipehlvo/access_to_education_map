import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from shapely import wkt
import streamlit as st

st.set_page_config(layout="wide")


@st.cache_data
def load_data():
    '''
    Load data from Google Cloud Storage
    '''
    #key = "1B5lf4kxcBmtVUZppMgpcEh5RrJHrO9OG"
    access_df = pd.read_csv(
        f'gs://capstone_access_data/access_df.csv', index_col=0)
    access_df = gpd.GeoDataFrame(
        access_df, geometry=access_df["geometry"].apply(wkt.loads), crs="EPSG:5641")
    access_df = access_df.to_crs(epsg=4326)
    return access_df


def plot_map(city_name, metric):
    '''
    Plots the map of a city with the metric of interest
    '''
    # Get subset of data
    subset_df = access_df[access_df["microregion_name"] ==
                          access_df[access_df["city_name"] == city_name]["microregion_name"].values[0]]
    # Get latitude and longitude of the first observation
    center = {"lat": subset_df["geometry"].iloc[0].centroid.y,
              "lon": subset_df["geometry"].iloc[0].centroid.x}

    range_color = [access_df[metric].quantile(0.05), access_df[metric].quantile(0.95)]

    fig = px.choropleth_mapbox(subset_df, geojson=subset_df, locations=subset_df.index, color=metric,
                               mapbox_style="open-street-map", opacity=0.5, center=center, zoom=10,
                               hover_data=["neighborhood_name"],
                               width=1000, height=800,
                               labels=print_name,
                               color_continuous_scale="RdYlGn", range_color=range_color)
    fig.update_layout(
        # Figure style
        title_text="title",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=800,
        geo_scope="south america", 
        
        # Colorbar style
        coloraxis_colorbar=dict(
        yanchor="bottom",
        y=0.01,
        xanchor="left",
        x=0.01,
        len = .3,
        tickvals=range_color,
        ticktext=["Low", "High"],
        ))

    
    fig.update_traces(marker_line_width=0)
    st.plotly_chart(fig, use_container_width=True)


# Mapping of variable names to print-friendly names
print_name = {
"n_teachers":"Number of teachers",
"n_students":"Number of students",
"n_classes":"Number of classes",
"A": "Accessibility",
"Q": "Quality",
"H": "Quality-adjusted Accessibility",
"avg_monthly_earnings": "Monthly Income (R$)",
"density": "Density (people/km^2)",
"pct_white": "% White",}

inv_print_name = {v: k for k, v in print_name.items()}


# Loading the data
access_df = load_data()

# App components
st.title("Access to Public High Schools in Brazil")
st.markdown("This is a dashboard measuring the access to public high schools in each neighborhood in Brazil. The data was collected from the Brazilian Institute of Geography and Statistics (IBGE). See more details in the [GitHub repository](https://github.com/felipehlvo/access_to_education_map)")
st.markdown("Interesting cities to try: Campinas, Rio de Janeiro, São Paulo")

# Selection of the city using a dropdown
city = st.selectbox("Select a city", access_df["city_name"].unique())


metric_list = [print_name["A"], print_name["Q"], print_name["H"]]

# Selection of metric
metric = st.selectbox("Select a metric", metric_list)

# Plot map
plot_map(city, inv_print_name[metric])
