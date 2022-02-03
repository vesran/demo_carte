import pandas as pd
import geopandas as gpd


PATH_TO_CLEAN_COMMUNES = 'data/clean/communes.geojson'
PATH_TO_CLEAN_BIRTHES = 'data/clean/naissances.geojson'
PATH_TO_CLEAN_SCHOOLS = 'data/clean/schools.csv'
OUTPUT_FILE = 'data/clean/stats.geojson'


def get_communes():
    return gpd.read_file(PATH_TO_CLEAN_COMMUNES)


def get_birthes():
    return gpd.read_file(PATH_TO_CLEAN_BIRTHES)


def get_schools():
    return pd.read_csv(PATH_TO_CLEAN_SCHOOLS)


def add_schools(communes):
    schools = get_schools()

    # Group agglomerations
    agglo_prefixes = ['751', '691', '130']
    agglo_codes = ['75056', '69123', '13055']
    schools['code_insee'] = schools.code_insee.apply(
        lambda x: agglo_codes[agglo_prefixes.index(x[:3])] if x[:3] in agglo_prefixes else x)

    schools_by_communes = schools.groupby('code_insee').agg({'code': 'count', 'academie': 'first'}).rename({'code': 'num_schools'}, axis=1).reset_index()
    communes = communes.merge(schools_by_communes, on='code_insee', how='left')
    communes['num_schools'] = communes.num_schools.fillna(0)
    return communes


def add_birthes(communes):
    birthes = get_birthes()
    birthes = birthes[['code_insee', 'NAIS']]
    communes = communes.merge(birthes, on='code_insee', how='left')
    communes['NAIS'] = communes.NAIS.fillna(0)
    return communes


def compute_stats(communes):
    stats = add_schools(communes)
    stats = add_birthes(stats)
    stats['ratio_birth_school'] = stats.apply(lambda x: x['NAIS'] / x['num_schools'] if x['num_schools'] > 0 else float('inf'), axis=1)
    stats['ratio_school_birth'] = stats.apply(lambda x: x['num_schools'] / x['NAIS'] if x['NAIS'] > 0 else float('inf'), axis=1)
    return stats


def main():
    communes = get_communes()
    communes = communes.query('code_insee != "75001"')
    stats = compute_stats(communes)
    stats.to_file(OUTPUT_FILE, driver='GeoJSON')
    return stats


if __name__ == '__main__':
    stats = main()
    stats.query('code_insee == "75056"')
