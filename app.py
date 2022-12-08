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
    key = "1B5lf4kxcBmtVUZppMgpcEh5RrJHrO9OG"
    access_df = pd.read_csv(
        f'gs://capstone_access_data/access_df.csv', index_col=0)
    access_df = gpd.GeoDataFrame(
        access_df, geometry=access_df["geometry"].apply(wkt.loads), crs="EPSG:5641")
    access_df = access_df.to_crs(epsg=4326)
    return access_df


def plot_map(city_name, metric):
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
                               labels={
                                   "3sfca_n_teachers": "Accessibility",
                                   "3sfca_n_classes": "Accessibility",
                                   "neighborhood_name": "Neighborhood",
                                   "avg_monthly_earnings": "Average Monthly Earnings"},
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


access_df = load_data()


# col1, col2 = st.columns(2)

# App components
st.title("Access to Public High Schools in Brazil")
st.markdown("This is a dashboard measuring the access to public high schools in each neighborhood in Brazil. The data was collected from the Brazilian Institute of Geography and Statistics (IBGE). See more details in the [GitHub repository](https://github.com/felipehlvo/access_to_education_map)")
st.markdown("Interesting cities to try: Campinas, Rio de Janeiro, São Paulo")


city = st.selectbox("Select a city", access_df["city_name"].unique())

metric_dict = {"Accessibility to Public High Schools": "3sfca_n_classes", "Average Montly Earnings (R$)": "avg_monthly_earnings",
               "Number of people aged 15 to 17": "n_people_15to17_alternative"}

metric = st.selectbox("Select a metric", metric_dict.keys())

plot_map(city, metric_dict[metric])
