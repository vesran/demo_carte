import geopandas as gpd
import pandas as pd


INPUT_FILE = 'data/COMMUNES.geojson'
OUTPUT_FILE = 'data/clean/communes.geojson'


def extract_communes():
    communes = gpd.read_file(INPUT_FILE)
    return communes


def extract_arrondissements():
    arrs = gpd.read_file('data/ARRS.geojson')
    return arrs


def transform_communes(communes):
    arrs = extract_arrondissements()
    communes = pd.concat([communes, arrs])
    communes = communes.drop_duplicates(subset=['code'], keep='first')
    communes = communes.rename({
        'code': 'code_insee',
        'nom': 'lib_commune',
    }, axis=1)
    communes = communes.query('(not code_insee.str.startswith("97")) & (not code_insee.str.startswith("98"))')
    return communes


def main():
    communes = extract_communes()
    communes = transform_communes(communes)
    communes.to_file(OUTPUT_FILE, driver='GeoJSON')
    return communes


if __name__ == '__main__':
    communes = main()
