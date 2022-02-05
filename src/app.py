import pandas as pd
import geopandas as gpd
import folium
from branca.element import Figure
import cmasher as cmr

from shapely.geometry import MultiPolygon, Polygon
from scipy.spatial import cKDTree
import shapely

import streamlit as st
from streamlit_folium import folium_static

st.set_page_config(layout='wide')

red_square = 'https://cdn4.iconfinder.com/data/icons/pretty-office-part-5-shadow-style/256/Stop-red.png'
blue_square = 'https://icon-library.com/images/blue-icon-png/blue-icon-png-23.jpg'


def create_map():
    m = folium.Map(location = [46.856578, 2.351828], zoom_start = 5)
    return m


def df_to_gdf(df_src, geocols):
    df = df_src.copy()
    for col in geocols:
        df[col] = df[col].apply(shapely.wkt.loads)
    df = gpd.GeoDataFrame(df, crs=4326)
    return df


@st.cache(allow_output_mutation=True)
def load_data():
    academies = pd.read_csv('data/clean/academies.csv')
    stats = pd.read_csv('data/clean/stats_2.csv')

    academies = df_to_gdf(academies, ['geometry', 'point_commune'])
    stats = df_to_gdf(stats, ['geometry', 'centroid'])
    return academies, stats


def style(row):
    return {
        'color': row['properties']['color'],
        'fillColor': row['properties']['color']
    }


def main():
    st.header("Carte des écoles")
    m = create_map()

    # Data
    with st.spinner(text='Load data'):
        academies, stats = load_data()

    # Select segments
    high = st.sidebar.slider('Lower bound of high ratio :', 0, 150, 100)
    low = st.sidebar.slider('Upper bound of low ratio :', 0, 50, 5)
    high_ratio = stats.query(f'ratio_birth_school >= {high}')
    low_ratio = stats.query(f'ratio_birth_school < {low}')

    # Building map
    reds = cmr.take_cmap_colors('Reds', len(academies), return_fmt='hex')

    aca_group = folium.FeatureGroup(name='Academies').add_to(m)
    zones = folium.GeoJson(data=academies[['inferred_academie', 'NAIS', 'num_schools', 'geometry', 'color']],
                   style_function=style,
                   tooltip=folium.GeoJsonTooltip(fields=('inferred_academie', 'NAIS', 'num_schools',),
                                                 aliases=('Académie', '#Naissances', '#Ecoles'))
                  )
    aca_group.add_child(zones)

    # Add marker
    communes_group = folium.FeatureGroup(name="Communes").add_to(m)
    for _, row in academies.iterrows():
        lon = row['point_commune'].x
        lat = row['point_commune'].y
        icon = folium.Marker(location=[lat, lon],
                              popup=f'Commune: {row["lib_commune"]}')
        communes_group.add_child(icon)


    # Add zones with not enough schools
    high_group = folium.FeatureGroup(name="Ecoles denses").add_to(m)
    for _, row in high_ratio.iterrows():
        lon = row['centroid'].x
        lat = row['centroid'].y
        ic = folium.features.CustomIcon(red_square,
                                        icon_size=(14, 14))
        icon = folium.Marker(location=[lat, lon],
                             icon=ic,
                              popup=f'Commune: {row["lib_commune"]}, #Naissances: {row["NAIS"]}')
        high_group.add_child(icon)


    # Add zones with too much schools
    low_group = folium.FeatureGroup(name="Ecoles peu denses").add_to(m)
    for _, row in low_ratio.iterrows():
        lon = row['centroid'].x
        lat = row['centroid'].y
        ic = folium.features.CustomIcon(blue_square,
                                        icon_size=(14, 14))
        icon = folium.Marker(location=[lat, lon],
                             icon=ic,
                              popup=f'Commune: {row["lib_commune"]}, #Naissances: {row["NAIS"]}')
        low_group.add_child(icon)


    folium.LayerControl().add_to(m)

    fig = Figure(width=1500, height=400)
    fig.add_child(m)

    folium_static(m)


if __name__ == '__main__':
    main()
