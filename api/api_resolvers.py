import os
import sys
from typing import List, Dict, Union
import pandas as pd
import random

sys.path.extend(["../", "./"])

from utils.Filesys import generic_FileServer as FS
from utils.Countries import Country, getCountry
from utils.custom_types import *
from utils.sql_utils import selectTagsFromDB
from Input_Set_Up.prepareKeywordsFile import apply_php_deserialization, generateKeywordsFile


def folder_contains_country(folder: Folderpath, country: Country):
    return any(map(lambda f: country.Shortcode in f or country.Full_name in f, os.listdir(folder)))


def get_available_comparisons(country: Country) -> List[str]:
    folders = [f for f in os.listdir(FS.Comparisons) if
               os.path.isdir(os.path.join(FS.Comparisons, f)) and not f.startswith('.')]
    return [folder for folder in folders if folder_contains_country(os.path.join(FS.Comparisons, folder), country)]


def get_available_category_overviews(country: Country, campaign_name: str) -> List[str]:
    if os.path.exists(os.path.join(FS.Final, country.Full_name, campaign_name)):
        return [f for f in os.listdir(os.path.join(FS.Final, country.Full_name, campaign_name)) if not f.startswith(
            '.') and 'Main_Section' not in f and 'Top5_Tags' not in f and 'Main_Section' not in f and 'Chart_Data' not in f and 'Table_Data' not in f and 'Map_Data' not in f]
    else:
        return []


def get_available_tags(country: Country) -> List[Dict[str, Union[int, str, bool]]]:
    all_files: List[str] = os.listdir(os.path.join(FS.Aggregated, country.Full_name))
    tags = {}
    for file in all_files:
        if 'Adjusted' in file or (not file.startswith('.') and not file.startswith(f"{country.Shortcode.upper()}-")):
            try:
                tag_name = file.split('_')[2]
                tags[tag_name] = tags.get(tag_name, 0) + 1
            except Exception as e:
                print(e)
    array_form = []
    for key, val in tags.items():
        array_form.append({
            'tag_name': key,
            'count': val,
            'chosen': False
        })
    return array_form


def get_keywords_from_db(country: Country, search_items: List[Union[str, int]]) -> Union[List[
                                                                                             Dict[str, Union[
                                                                                                 str, int, List[
                                                                                                     str]]]], None]:
    search_keywords = [item for item in search_items if isinstance(item, str)]
    search_tag_ids = [item for item in search_items if isinstance(item, int) or isinstance(item, float)]
    df = selectTagsFromDB(country.Shortcode, search_keywords, search_tag_ids, called_through_api=True)
    if df is None:
        return None
    print(df)
    parsed_df = apply_php_deserialization(
        df)  # df headers: tag_id, tag_name, service_name, bc_name, elite_keywords, top_keywords
    tag_kwd_df: pd.DataFrame = generateKeywordsFile(parsed_df, "", "", desired_return='tag_keyword_df')
    grouped = tag_kwd_df.groupby(['tag_id', 'tag'])
    out = []
    for (tag_id, tag_name), group in grouped:
        kwds = group['keyword'].unique().tolist()
        out.append({
            'tag_id': tag_id,
            'tag_name': tag_name,
            'keywords': kwds
        })
    return out


def get_scraping_input_file(country: Country, campaign_short_code: str, scraping_type: str) -> Union[str, Filepath]:
    if "Individual" in scraping_type:
        if len(campaign_short_code) > 0:
            campaign_short_code = f"{campaign_short_code}_"
        expected = os.path.join(FS.Inputs, f"{campaign_short_code}Keywords_{country.Shortcode.upper()}.csv")
        if os.path.exists(expected):
            return expected
        else:
            expected = os.path.join(FS.Inputs, f"Keywords_{country.Shortcode.upper()}.csv")
            if os.path.exists(expected):
                return expected
            else:
                return ""
    else:
        expected = os.path.join(FS.Inputs, f"ProntoPro Trends_Questions_{country.Shortcode.upper()}.json")
        if os.path.exists(expected):
            return expected
        else:
            expected = os.path.join(FS.Inputs, f"ProntoPro_Trends_Questions_{country.Shortcode.upper()}.json")
            if os.path.exists(expected):
                return expected
            else:
                return ""


def get_csv(filename: Union[Filepath, str]):
    if os.path.exists(filename):
        return filename
    else:
        for root, dirs, files in os.walk(FS.cwd):
            if filename in files:
                return os.path.join(root, filename)


def get_available_options(filepath: Filepath, columns: List[str] = ('Year', 'ticket_geo_region_name')) -> Dict[
    str, List[Union[str, int]]]:
    df: pd.DataFrame = pd.read_csv(filepath)
    vals: Dict[str, List[Union[str, int]]] = {}
    for col in columns:
        vals[col] = df[col].unique().tolist()
    return vals


def get_data_for_options(filepath: Filepath, year: int, region: str):
    available_colors = [
        "#f7f8f9", "#e9ecef", "#bec8d0", "#7d92a2", "#274964", "#f2fdf7", "#e5faef", "#b2f2d0", "#66e6a2", "#00d664",
        "#f6fcfc", "#ecf8f9", "#c8ebef", "#91d9e0", "#48bfcc", "#fef7f4", "#feeee9", "#fdcebe", "#fc9d7e", "#f95c28",
        "rgba(39,73,100,.6)", "#fdf5f2", "#fcebe6", "#f6c4b4", "#ed8b6a", "#e13d06", "hsla(0,0%,100%,0)", "#fff",
        "#fefcf4", "#fef8e9", "#fcebbf", "#fad880", "#f7be2c", "#48bfcc", "#91d9e0", "#f7f8f9", "#e9ecef", "#bec8d0",
        "#7d92a2", "#f2fdf7", "#e5faef", "#b2f2d0", "#66e6a2", "#f6fcfc", "#ecf8f9", "#c8ebef", "#fef7f4", "#feeee9",
        "#fdcebe", "#fc9d7e", "#fdf5f2", "#fcebe6", "#f6c4b4", "#ed8b6a", "#48bfcc", "#fefcf4", "#fef8e9", "#fcebbf",
        "#fad880"]
    df: pd.DataFrame = pd.read_csv(filepath)
    query = df.query('Year == @year & ticket_geo_region_name == @region').fillna(0)
    # print(query)
    labels = query[query.columns[2]].tolist()
    data = query['Distribution'].tolist()
    chosen_colors = random.choices(available_colors, k=len(data))
    final = {
        'labels': labels,
        'datasets': [{
            'data': data,
            'backgroundColor': chosen_colors,
            'hoverBackgroundColor': chosen_colors,
        }]
    }
    return final


if __name__ == '__main__':
    path = "/Users/chris/PycharmProjects/ProntoTrends/Output_Files/FINAL/Italy/Summer/Overview_Homecare.csv"
    get_data_for_options(path, 2020, 'Italia')
