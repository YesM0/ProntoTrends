
if __name__ == '__main__':
    import sys
    sys.path.append('../')

import os
from typing import Union, List, Dict, Callable, Optional
import pandas as pd
import phpserialize as ps  # pip install phpserialize
import json
from utils.sql_utils import selectTagsFromDB
from utils.user_interaction_utils import binaryResponse, choose_from_dict, choose_multiple_from_dict, \
    chooseFile, defineList
from utils.Filesys import generic_FileServer
from utils.misc_utils import save_csv
from utils.custom_types import *

FS = generic_FileServer


def deserializeItem(x: str) -> Optional[List[str]]:
    if x != x or x is None:
        return None
    x = x.encode()
    x = ps.loads(x)
    x = [x[y].decode() for y in x]
    return x


def serializeItem(col_val: str) -> str:
    arr: list = col_val.split("|")
    return ps.dumps(arr)


def generateKeywordsFile(df: pd.DataFrame, prefix_out: str = '', cc: Country_Shortcode = 'IT', desired_return: str = None):
    tag_kwd = []
    keywords = set()
    keyword_ids = []
    grouped = df.groupby(by=[df.columns[0], df.columns[1]])
    for name, group in grouped:
        kwd_ids = 1
        tag_id, tag_name = name
        for ind, row in group.iterrows():
            columns = group.columns[2:]
            for col in columns:
                val = row[col]
                if isinstance(val, str):
                    val = [val]
                elif isinstance(val, int) or isinstance(val, float) or val is None:
                    continue
                for x in val:
                    if x not in keywords and x.lower() not in keywords:
                        kwd_id = f"{tag_id}-{kwd_ids}"
                        kwd_ids += 1
                        keywords.add(x)
                        tag_kwd.append([tag_id, kwd_id, tag_name, x])
                        keyword_ids.append([kwd_id, x])
                    else:
                        continue
    keywords_df = pd.DataFrame(keyword_ids, columns=['kwd_id', 'Keyword'])
    tag_kwd_df = pd.DataFrame(tag_kwd, columns=["tag_id", "kwd_id", "tag", "keyword"])
    if desired_return is None:
        saveKeywordsFiles(keywords_df, tag_kwd_df, prefix_out, cc)
    elif desired_return == 'keywords_df':
        return keywords_df
    else:
        return tag_kwd_df


def saveKeywordsFiles(keywords_df: pd.DataFrame, tag_kwd_df: pd.DataFrame, prefix_out: str, cc: Country_Shortcode, logging_function: Callable = print):
    prefix_out = f"{prefix_out}_" if len(prefix_out) > 0 else ''
    saveLocation = os.path.join(FS.Inputs, f"{prefix_out}Keywords_{cc}.csv")
    save_csv(keywords_df, saveLocation, index=False)
    save_csv(tag_kwd_df, os.path.join(FS.Inputs, f"{prefix_out}Tag_Keyword_{cc}.csv"), index=False, logging_func=logging_function)


def read_php_csv(filename: Filepath):
    df = pd.read_csv(filename)
    print(df.head())
    df = apply_php_deserialization(df)
    print(df.head())
    return df


def apply_php_deserialization(df: pd.DataFrame):
    df['elite_keywords'] = df['elite_keywords'].apply(deserializeItem)
    df['top_keywords'] = df['top_keywords'].apply(deserializeItem)
    return df


def generateComparisonsFile(df: pd.DataFrame, country: Country_Shortcode):
    cats = defineList()
    selections = {}
    tags = deduplicatedTagsByName(df)
    for cat in cats:
        selections[cat] = choose_multiple_from_dict(tags, 'tags', request_description=f'Please select the Tags you want to add to the category {cat}')
    final = {}
    for cat, options in selections.items():
        cat_kwds = {}
        for option in options:
            option_kwds = []
            rows = df.query('tag_name == @option')
            dictionary = rows.to_dict(orient='list')
            for key, vals in dictionary.items():
                if key in ['tag_name', 'tag_id']:
                    continue
                else:
                    for val in vals:
                        if not isinstance(val, list):
                            if not val is None and not pd.isna(val) and val != 'None':
                                option_kwds.append(val)
                        else:
                            for item in val:
                                option_kwds.append(item)
            cat_kwds[option] = list(set(option_kwds))
        final[cat] = cat_kwds
    return save_comparison(country, final)


def save_comparison(country: Country_Shortcode, final: dict, logging_func: Callable = print):
    s = json.dumps(final)
    path = os.path.join(FS.Inputs, f'ProntoPro_Trends_Questions_{country.upper()}.json')
    with open(path, 'w+') as f:
        f.write(s)
        logging_func(f"Saved file {path}")
    return final


def deduplicatedTagsByName(df):
    tags = {}
    for ind, row in df.iterrows():
        tags[ind] = row['tag_name']
    present = []
    to_pop = []
    for k, v in tags.items():
        if v in present:
            to_pop.append(k)
        else:
            present.append(v)
    for i in to_pop:
        tags.pop(i)
    return tags


def api_file_creation(settings: dict, logging_function: Callable):
    logging_function('Creating files')
    flow_type = settings.get("input_type", 'Comparison')
    do_individual = flow_type == 'Both' or flow_type == 'Individual'
    do_comparison = flow_type == 'Both' or flow_type == 'Comparison'
    if do_individual:
        keywords = []
        tag_keyword = {}
        for item in settings.get('tag_settings', []):
            print(item)
            keywords.extend(item.get('keywords', []))
            tag_keyword[item['option']] = item.get('keywords', [])
        kwds = [[i, k] for i, k in enumerate(keywords)]
        kwd_to_id = {i: k for (k, i) in kwds}
        print(kwd_to_id)
        kwds_df = pd.DataFrame(kwds, columns=['kwd_id', 'Keyword'])
        tag_to_keywords = []
        print(f"Tag Keyword: {tag_keyword}")
        for i, (tag, l) in enumerate(tag_keyword.items()):
            tag_id = f"111{i:03}"
            for k in l:
                kwd_id = kwd_to_id.get(k, tag_id)
                tag_to_keywords.append([tag_id, kwd_id, tag, k])
        print(tag_to_keywords)
        tag_kwd_df = pd.DataFrame(tag_to_keywords, columns=["tag_id", "kwd_id", "tag", "keyword"])
        saveKeywordsFiles(kwds_df, tag_kwd_df, cc=settings.get('country_short_name', 'DE'), prefix_out=settings.get('campaign_shortcode'), logging_function=logging_function)
    if do_comparison:
        final = {}
        for item in settings.get('tag_settings', []):
            cat = item.get('category', 'Default') if len(item.get('category', 'Default')) > 0 else 'Default'
            option = item.get('option', None)
            ks = item.get('keywords', None)
            if option is not None and ks is not None:
                if hasattr(final, cat):
                    final[cat][option] = ks
                else:
                    final[cat] = {option: ks}
        save_comparison(settings.get('country_short_name', 'DE'), final, logging_function)


if __name__ == '__main__':
    country = choose_from_dict({1: 'IT', 2: 'DE', 3: 'ES', 4: 'FR', 5: 'AT', 6: 'CH'}, 'Countries')
    if binaryResponse("Do you have a sourcefile to get Tag information from?"):
        filename = chooseFile(filetype=".csv")
        df = read_php_csv(filename)
    else:
        if binaryResponse("Do you want to search using Tag_Ids (y) or using Contains-Match in all text fields (n)?"):
            use_ids = True
        else:
            use_ids = False
        kwds = None
        tag_ids = None
        if use_ids:
            tag_ids = defineList(request_text="Please input the tag ids to use", wanted_type='int')
        else:
            kwds = defineList(wanted_type='str', request_text="Please input the Contains-Match keywords to use")
        df = selectTagsFromDB(country.lower(), kwds=kwds, tag_ids=tag_ids)
        df = apply_php_deserialization(df)
    c = choose_from_dict(['CSV to scrape Keywords individually', 'JSON file for Comparison', 'Both'], request_description='What type of files do you want to create?', label='actions')

    if c == 'CSV to scrape Keywords individually' or c == 'Both':
        prefix = ""
        if binaryResponse("Do you want to add a prefix to the filename?"):
            prefix = input("Please type the prefix:\n").strip()
        generateKeywordsFile(df, prefix_out=prefix, cc=country)
    if c == 'JSON file for Comparison' or c == 'Both':
        generateComparisonsFile(df, country)

