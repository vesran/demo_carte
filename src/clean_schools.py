import geopandas as gpd
import pandas as pd

INPUT_FILE = 'data/fr-en-adresse-et-geolocalisation-etablissements-premier-et-second-degre.csv'
OUTPUT_FILE = 'data/clean/schools.csv'

PATH_TO_CLEAN_COMMUNES = 'data/clean/communes.geojson'


def extract_schools():
    schools = pd.read_csv(INPUT_FILE,
                    sep=';',
                    usecols=['Code établissement', 'Appellation officielle', 'Code commune', 'Département', 'Région', 'Académie', 'Position']
                   )
    return schools


def transform_schools(etabs):
    etabs = etabs.rename({
        'Code établissement': 'code',
        'Appellation officielle': 'nom',
        'Code commune': 'code_insee',
        'Département': 'lib_dep',
        'Région': 'lib_region',
        'Académie': 'academie',
        'Position': 'geoloc'
    }, axis=1)
    etabs = etabs[etabs.geoloc.notnull() & etabs['nom'].notnull()]

    # Handle geoloc
    etabs['latitude'] = etabs['geoloc'].apply(lambda x: x.split(',')[0])
    etabs['longitude'] = etabs['geoloc'].apply(lambda x: x.split(',')[1])
    etabs = etabs.drop('geoloc', axis=1)

    return etabs


def main():
    schools = extract_schools()
    schools = transform_schools(schools)
    schools.to_csv(OUTPUT_FILE, index=False)


if __name__ == '__main__':
    main()
