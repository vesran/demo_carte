import geopandas as gpd
import pandas as pd


PATH_TO_CLEAN_COMMUNES = 'data/clean/communes.geojson'

INPUT_FILE = 'data/base_naissances_2020.csv'
OUTPUT_FILE = 'data/clean/naissances.geojson'


def extract_birthes():
    birthes = pd.read_csv(INPUT_FILE, sep=';',
                          usecols=['CODGEO', 'NAISD17', 'NAISD18', 'NAISD19', 'NAISD20'])
    return birthes


def get_communes():
    return gpd.read_file(PATH_TO_CLEAN_COMMUNES)


def transform_birthes(birthes):
    birthes = birthes.rename({
        'CODGEO': 'code_insee'
    }, axis=1)
    birthes = birthes.fillna(0)

    # Group agglomerations
    agglo_prefixes = ['751', '691', '130']
    agglo_codes = ['75056', '69123', '13055']
    birthes['COMM'] = birthes.code_insee.apply(lambda x: agglo_codes[agglo_prefixes.index(x[:3])] if x[:3] in agglo_prefixes else x)
    birthes = birthes.groupby('COMM').sum().reset_index()
    birthes = birthes.rename({"COMM": "code_insee"}, axis=1)

    # Get total
    birthes['NAIS'] = birthes['NAISD17'] + birthes['NAISD18'] + birthes['NAISD19'] + birthes['NAISD20']
    birthes = birthes.drop(['NAISD17', 'NAISD18', 'NAISD19', 'NAISD20'], axis=1)

    communes = get_communes()
    birthes = communes.merge(birthes, on='code_insee', how='inner')
    return birthes


def main():
    birthes = extract_birthes()
    birthes = transform_birthes(birthes)
    birthes.to_file(OUTPUT_FILE, driver='GeoJSON')


if __name__ == '__main__':
    main()
