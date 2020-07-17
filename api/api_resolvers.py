import os
import sys
from typing import List, Dict, Union

sys.path.extend(["../", "./"])

from utils.Filesys import generic_FileServer as FS
from utils.Countries import Country, getCountry
from utils.custom_types import *


def folder_contains_country(folder: Folderpath, country: Country):
    return any(map(lambda f: country.Shortcode in f or country.Full_name in f, os.listdir(folder)))


def get_available_comparisons(country: Country) -> List[Folderpath]:
    folders = [f for f in os.listdir(FS.Comparisons) if
               os.path.isdir(os.path.join(FS.Comparisons, f)) and not f.startswith('.')]
    return [folder for folder in folders if folder_contains_country(os.path.join(FS.Comparisons, folder), country)]


def get_available_category_overviews(country: Country, campaign_name: str) -> List[str]:
    return [f for f in os.listdir(os.path.join(FS.Final, country.Full_name, campaign_name)) if not f.startswith(
        '.') and 'Main_Section' not in f and 'Top5_Tags' not in f and 'Main_Section' not in f and 'Chart_Data' not in f and 'Table_Data' not in f and 'Map_Data' not in f]


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


if __name__ == '__main__':
    country = Country(short_name='DE')
    print(get_available_category_overviews(country, 'Wed'))
    print(get_available_comparisons(country))
    print(get_available_tags(country))
