import json
import os
from typing import Union

from utils.custom_types import Country_Fullname, Region_Fullname, Region_Shortcode
from utils.misc_utils import deepSearch
from utils.Filesys import generic_FileServer

FS = generic_FileServer


def readInCategories():
    with open(os.path.join(FS.Statics, "All_Categories_Google.txt"), "r", encoding='utf-8') as f:
        allCats = f.read()
    allCats = json.loads(allCats)
    return allCats


def readInLocales() -> dict:
    with open(FS.All_Google_Locales, "r") as f:
        allLocales = f.read()
    allLocales = json.loads(allLocales)
    return allLocales


def findCategory(name):
    result = deepSearch(name, readInCategories())
    return result


def findLocale(name: Union[Country_Fullname, Region_Fullname, str], isRegion: bool = False, includeChildren: bool = False):
    locales: dict = readInLocales()
    if isRegion:
        regionId, parentId = deepSearch(name, locales, return_parents=True)
        result: Region_Shortcode = Region_Shortcode(f"{parentId}-{regionId}")
    elif includeChildren:
        r = deepSearch(name, locales, return_children=True)
        return r
    else:
        result: Union[tuple, str, bool] = deepSearch(name, locales)
    return result


def getRegionIdToName(country_name: Country_Fullname):
    locales: dict = readInLocales()
    cc_id, region_ids_dict = deepSearch(country_name, locales, return_children=True, include_children_names=True)
    return region_ids_dict


if __name__ == '__main__':
    # readInCategories()
    # readInLocales()
    # print(f"Found for Bavaria: {findLocale('Bavaria', isRegion=True)}")
    # print(f"Found for Netherlands: {findLocale('Netherlands', includeChildren=True)}")
    # print(f"Found id: {findCategory('Book Retailers')}")
    getRegionIdToName(Country_Fullname('Germany'))
