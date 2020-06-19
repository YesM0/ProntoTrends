if __name__ == '__main__':
    import sys

    sys.path.append('../')

from typing import Union, Dict, List, Tuple
import os
import pandas as pd
from utils.misc_utils import reverseDict, translate_dict, deduplicateColumns, rescale_comparison
from utils.user_interaction_utils import choose_from_dict
from utils.custom_types import *
from utils.Countries import region_merges, regions_map_english_to_local, getCountry
from utils.Filesys import generic_FileServer as FS

eng_code = {
    "Alsace": "FR-A",
    "Aquitaine": "FR-B",
    "Auvergne": "FR-C",
    "Brittany": "FR-E",
    "Burgundy": "FR-D",
    "Centre-Val de Loire": "FR-F",
    "Champagne-Ardenne": "FR-G",
    "Corsica": "FR-H",
    "Franche-Comté": "FR-I",
    "Languedoc-Roussillon": "FR-K",
    "Limousin": "FR-L",
    "Lorraine": "FR-M",
    "Lower Normandy": "FR-P",
    "Midi-Pyrénées": "FR-N",
    "Nord-Pas-de-Calais": "FR-O",
    "Pays de la Loire": "FR-R",
    "Picardy": "FR-S",
    "Poitou-Charentes": "FR-T",
    "Provence-Alpes-Côte d'Azur": "FR-U",
    "Rhone-Alpes": "FR-V",
    "Upper Normandy": "FR-Q",
    "Île-de-France": "FR-J",
    "Grand-est": 'FR-GE',
    "Hauts-de-france": 'FR-HF',
    "Normandie": "FR-NO",
    "Bourgogne-Franche-Comté": "FR-BFC",
    "Nouvelle-Aquitaine": "FR-NA",
    "Occitanie": "FR-OC",
    "Auvergne-Rhône-Alpes": "FR-AR"
}

override_list = [
    {"name": "Brittany", "id": "FR-E"},
    {'name': "Centre-Val de Loire", 'id': "FR-F"},
    {'name': "Corsica", 'id': "FR-H"},
    {'name': "Pays de la Loire", 'id': "FR-R"},
    {'name': "Provence-Alpes-Côte d'Azur", 'id': "FR-U"},
    {'name': "Île-de-France", 'id': "FR-J"},
    {'name': "Grand-est", 'id': 'FR-GE'},
    {'name': "Hauts-de-france", 'id': 'FR-HF'},
    {'name': "Normandie", 'id': "FR-NO"},
    {'name': "Bourgogne-Franche-Comté", 'id': "FR-BFC"},
    {'name': "Nouvelle-Aquitaine", 'id': "FR-NA"},
    {'name': "Occitanie", 'id': "FR-OC"},
    {'name': "Auvergne-Rhône-Alpes", 'id': "FR-AR"}
]


def doMerges_Geo(df: pd.DataFrame, cc_merges: dict, index_col='means'):
    for col_name, items in cc_merges.items():
        if col_name in df.columns:
            non_index_cols = [col for col in df.columns if col not in [index_col, col_name]]
            exclude_subqueries = []
            for label, subitems in items.items():
                query = "|"
                subqueries = []
                for item in subitems:
                    query_col_name = col_name if not ' ' in col_name else f"`{col_name}`"
                    subqueries.append(f"{query_col_name} == '{item}'")
                    exclude_subqueries.append(f"{query_col_name} != '{item}'")
                query = query.join(subqueries)
                selection = df.query(query)
                if len(non_index_cols) > 0:
                    averaged = selection.groupby(non_index_cols).mean()
                else:
                    averaged = selection.mean()
                averaged[col_name] = label
                print(averaged)
                df = df.append(averaged, ignore_index=True)
            df = df.query(" & ".join(exclude_subqueries))
            print(df)
    maximum = df[index_col].max()
    if not maximum == 100:
        df[index_col] = df[index_col].apply(lambda x: (x / maximum) * 100)
    return df


def do_merges_Time(folder: Folderpath,
                   cc_merges: Dict[Column_Name, Dict[Region_Shortcode, List[Region_Shortcode]]]) -> Tuple[
    List[Filepath], List[Filepath]]:
    new_files = []
    unnecessary_files = []
    for column, combinations in cc_merges.items():
        for rg_short, combis in combinations.items():
            merge_region_df: Union[pd.DataFrame, None] = None
            for rg in combis:
                try:
                    files = os.listdir(folder)
                    file: Filepath = os.path.join(folder, list(filter(lambda x: rg in x.split("_"), files))[0])
                except Exception as e:
                    print(e)
                    file: bool = False
                if file:
                    unnecessary_files.append(file)
                    df = pd.read_csv(file)
                    df['date'] = pd.to_datetime(df.date)
                    df = df.set_index(df.date)
                    df = df.drop(columns=list(filter(lambda x: x if x in ['isPartial', 'date'] else None, df.columns)))
                    df = deduplicateColumns(df, extra='isPartial')
                    # if df.shape[1] <= 3:
                    #     df = df.iloc[:, 1:] # drop index if needed
                    if merge_region_df is None:
                        merge_region_df = df.copy()
                    else:
                        col_merge_on = 'date'
                        merge_region_df = merge_region_df.combine(df, func=avg, overwrite=False)
            merge_region_df = rescale_comparison(merge_region_df)
            new_name = file.replace(rg, rg_short)
            merge_region_df.to_csv(new_name, index=False)
    return new_files, unnecessary_files


def merge_for_scraper(directory: Filepath, country_shortcode: Country_Shortcode = 'FR'):
    """
    Conducts all merges for the scraper. Takes an directory and cycles through everything
    Args:
        directory:
        country_shortcode:

    Returns:

    """
    cc_merges = region_merges.get(country_shortcode, False)
    if cc_merges:
        print("Merging region-files")
        t = translate_dict(translate_dict(cc_merges, reverseDict(regions_map_english_to_local)),
                           eng_code)  # translates from French to English to Code
        new_files, unnecessary_files = do_merges_Time(directory, t)
        print(f"Created new files: {new_files}\nThese files are not necessary anymore: {unnecessary_files}")
        geoFiles: List[str] = list(
            filter(lambda x: country_shortcode in x and "geo" in x.lower(), os.listdir(directory)))
        for geoFile in geoFiles:
            try:
                path = os.path.join(directory, geoFile)
                df = pd.read_csv(path, usecols=[1, 2])
                t = translate_dict(cc_merges, reverseDict(regions_map_english_to_local))
                new = doMerges_Geo(df, t, 'means')
                new.to_csv(path)
                print(f"Updated file: {path}")
            except Exception as e:
                print(e)


def avg(s1: pd.Series, s2: pd.Series) -> pd.Series:
    val = (s1 + s2) / 2
    print(s1, s2)
    return val


if __name__ == '__main__':
    country = getCountry()
    choice = choose_from_dict({i: k for i, k in enumerate(['Comparisons', 'Aggregated'])}, label="Folders",
                              request_description="In which of the following Folders do you want to merge regions?")
    directories = FS.Comparisons
    if choice == 'Comparisons':
        directories = []
        for item in os.listdir(FS.Comparisons):
            if os.path.isdir(item) and not item.startswith("."):
                directories.append(item)
    elif 'Aggregated':
        directories = [os.path.join(FS.Aggregated, country.Full_name)]
    for directory in directories:
        print(f"Working on directory: {directory}")
        merge_for_scraper(directory, country.Shortcode)
