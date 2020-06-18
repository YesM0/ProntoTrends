from typing import Union, Dict, List
import os
import pandas as pd
import numpy as np
from utils.misc_utils import regions_map_english_to_local, reverseDict, translate_dict, deduplicateColumns
from utils.user_interaction_utils import choose_from_dict
from utils.custom_types import *

merges = {
    'FR': {
        "ticket_geo_region_name": {
            "Grand-est": ["Alsace", "Champagne-Ardenne", "Lorraine"],
            "Hauts-de-france": ["Picardie", "Nord-Pas-de-Calais"],
            "Normandie": ['Basse Normandie', 'Haute Normandie'],
            "Bourgogne-Franche-Comté": ["Bourgogne", "Franche-Comté"],
            "Nouvelle-Aquitaine": ["Aquitaine", "Limousin", "Poitou-Charentes"],
            "Occitanie": ["Languedoc-Roussillon", "Midi-Pyrénées"],
            "Auvergne-Rhône-Alpes": ["Auvergne", "Rhône-Alpes"]
        },
        'geoName': {
            "Grand-est": ["Alsace", "Champagne-Ardenne", "Lorraine"],
            "Hauts-de-france": ["Picardie", "Nord-Pas-de-Calais"],
            "Normandie": ['Basse Normandie', 'Haute Normandie'],
            "Bourgogne-Franche-Comté": ["Bourgogne", "Franche-Comté"],
            "Nouvelle-Aquitaine": ["Aquitaine", "Limousin", "Poitou-Charentes"],
            "Occitanie": ["Languedoc-Roussillon", "Midi-Pyrénées"],
            "Auvergne-Rhône-Alpes": ["Auvergne", "Rhône-Alpes"]
        }
    }
}

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
                   cc_merges: Dict[Column_Name, Dict[Region_Shortcode, List[Region_Shortcode]]]) -> pd.DataFrame:
    for column, combinations in cc_merges.items():
        for rg_short, combis in combinations.items():
            merge_region_df: Union[pd.DataFrame, None] = None
            for rg in combis:
                try:
                    file: Filepath = os.path.join(folder, list(filter(lambda x: rg in x, os.listdir(folder)))[0])
                except Exception as e:
                    print(e)
                    file: bool = False
                if file:
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
                        # avg = lambda s1, s2: (s1 + s2)/2 if (isinstance(s1, int) or isinstance(s1, float)) and (isinstance(s2, int) or isinstance(s2, float)) else np.NaN
                        merge_region_df = merge_region_df.combine(df, func=avg, overwrite=False)
                        # to_avg = [col for col in merge_region_df.columns if "_left" in col or "_right" in col]
                        # grouped_to_avg: Dict[str, List[str]] = {}
                        # for col in to_avg:
                        #     n = col.split("_")[0]
                        #     if grouped_to_avg.get(n, False):
                        #         grouped_to_avg[n].append(col)
                        #     else:
                        #         grouped_to_avg[n] = [col]
                        # for group, cols in grouped_to_avg.items():
                        #     merge_region_df[group] = merge_region_df[]
            comp = merge_region_df.copy()
            merge_region_df = merge_region_df.apply(lambda s: s / merge_region_df.max(axis=0, numeric_only=True).max())
            print(merge_region_df)
        return merge_region_df


# TODO (p0): Implement in generateSummaries flow / after scraping for France
# TODO (p0): adjust read-in functions for final_csv generator to take final regions and disregard old ones


def avg(s1: pd.Series, s2: pd.Series) -> pd.Series:
    val = (s1 + s2) / 2
    print(s1, s2)
    return val


def test1():
    path = "/Google_Trends/Aggregated/France/FR_211_Fleuriste pour évènements_Geo.csv"
    df = pd.read_csv(path, usecols=[1, 2])
    t = translate_dict(merges['FR'], reverseDict(regions_map_english_to_local))
    doMerges_Geo(df, t, 'means')


def test2():
    folder = "/Users/chris/PycharmProjects/Google Trends/Google_Trends/Output_Files/out/apprendre a dessiner"
    t = translate_dict(translate_dict(merges['FR'], reverseDict(regions_map_english_to_local)), eng_code)
    result = do_merges_Time(folder, t)
    print(result)


def test3():
    folder = "/Users/chris/PycharmProjects/Google Trends/Google_Trends/Output_Files/comparisons/Reception Location"
    t = translate_dict(translate_dict(merges['FR'], reverseDict(regions_map_english_to_local)), eng_code)
    result = do_merges_Time(folder, t)
    print(result)


if __name__ == '__main__':
    functions = [x for x, y in locals().items() if callable(y)]
    options = {i: item for i, item in enumerate(functions)}
    choice = choose_from_dict(options, 'Functions')
    fn = locals().get(choice, False)
    if fn is not False:
        fn()
