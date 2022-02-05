import pandas as pd
import geopandas as gpd
import folium
from branca.element import Figure
import cmasher as cmr

from shapely.geometry import MultiPolygon, Polygon
from scipy.spatial import cKDTree


def find_closest_communes(gdf_src, indexor, schooled):
    gdf = gdf_src.copy()

    # Find id of the closest commune
    gdf['closest_point_i'] = gdf.centroid.apply(lambda x: indexor.query((x.x, x.y))[1])
    gdf['closest_code_insee'] = gdf['closest_point_i'].apply(lambda x: schooled.iloc[x].code_insee)

    # Add centroids of closest commune
    gdf = gdf.merge(schooled[['code_insee', 'centroid']], left_on='closest_code_insee', right_on='code_insee', how='left', suffixes=('', '_y')).drop('code_insee_y', axis=1).rename({'centroid': 'closest_centroid'}, axis=1)
    gdf = gdf.drop('closest_point_i', axis=1)
    return gdf


def load_data():
    gdf = gpd.read_file('data/clean/stats.geojson')
    communes = gpd.read_file('data/clean/communes.geojson')
    communes = communes.drop_duplicates('lib_commune', keep='first').copy()

    # Find the closest commune
    schooled = gdf.query('num_schools > 0').copy()
    schooled['centroid'] = schooled.centroid
    indexor = cKDTree(schooled.centroid.apply(lambda x: (x.x, x.y)).values.tolist())
    gdf = find_closest_communes(gdf, indexor, schooled)
    return gdf, communes


def prepare_academies(gdf, communes):
    # Group communes into academies
    reds = cmr.take_cmap_colors('Reds', 100, return_fmt='hex')
    seismic = cmr.take_cmap_colors('seismic', 100, return_fmt='hex')

    def choose_color(value):
        r = value / 120
        r_color = reds[min(int(r * 100) - 1, 99)]
        return r_color


    # Give an academy to each row
    insee2academie = {row['code_insee']: row['academie'] for _, row in gdf.iterrows() if row['academie'] is not None}
    gdf['inferred_academie'] = gdf['closest_code_insee'].apply(lambda x: insee2academie[x])

    cols = ['inferred_academie', 'NAIS', 'num_schools', 'geometry']
    academies = gdf[cols].dissolve('inferred_academie', aggfunc=sum).reset_index()
    academies['ratio_birth_school'] =  academies['NAIS'] / academies['num_schools']
    academies['color'] = academies.ratio_birth_school.apply(lambda x: choose_color(x))


    # Fix academies' names to join communes using their names (no id available)
    d = {
        'Aix-Marseille': 'Marseille',
        'Corse': 'Ajaccio',
        'Nancy-Metz': 'Nancy',
        'Orléans-Tours': 'Tours',
    }
    academies['commune'] = academies.inferred_academie.apply(lambda x: d[x] if x in d else x)
    academies = academies.merge(communes[['lib_commune', 'geometry']], left_on='commune', right_on='lib_commune', how='left', suffixes=('', '_commune'))

    # Computes points to localize the cities
    academies['point_commune'] = academies.set_geometry('geometry_commune').centroid
    return academies


def prepare_stats(gdf):
    # Compute ratios
    def compute_stats(gdf):
        gdf_geo = gdf[['closest_code_insee', 'geometry']].dissolve('closest_code_insee')
        gdf = gdf.groupby('closest_code_insee').agg({'lib_commune': 'first', 'num_schools':'sum', 'NAIS':'sum'}).reset_index()
        gdf = gdf_geo.merge(gdf, on='closest_code_insee', how='inner')
        gdf['ratio_birth_school'] = gdf.apply(lambda x: x['NAIS'] / x['num_schools'] if x['num_schools'] > 0 else float('inf'), axis=1)
        return gdf

    stats = compute_stats(gdf)
    stats['centroid'] = stats.centroid
    return stats


def main():
    # Data
    gdf, communes = load_data()
    academies = prepare_academies(gdf.copy(), communes.copy())
    stats = prepare_stats(gdf.copy())

    academies.to_csv('data/clean/academies.csv', index=False)
    stats = stats.to_csv('data/clean/stats_2.csv', index=False)


if __name__ == '__main__':
    main()
