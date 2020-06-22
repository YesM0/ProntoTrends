from utils.sql_utils import selectTagsFromDB

if __name__ == '__main__':
    import sys
    sys.path.append('../')

import os
import pandas as pd
import phpserialize as ps  # pip install phpserialize
import json
from utils.user_interaction_utils import binaryResponse, choose_from_dict, choose_multiple_from_dict, \
    chooseFile, defineList
from utils.Filesys import generic_FileServer

FS = generic_FileServer


def deserializeItem(x):
    if x != x or x is None:
        return None
    x = x.encode()
    x = ps.loads(x)
    x = [x[y].decode() for y in x]
    return x


def serializeItem(col_val):
    arr = col_val.split("|")
    return ps.dumps(arr)


def generateKeywordsFile(df, prefix_out='', cc='IT'):
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
    prefix_out = f"{prefix_out}_" if len(prefix_out) > 0 else ''
    saveLocation = os.path.join('Input_Files', f"{prefix_out}Keywords_{cc}.csv")
    keywords_df.to_csv(saveLocation, index=False)
    tag_kwd_df.to_csv(os.path.join('Input_Files', f"{prefix_out}Tag_Keyword_{cc}.csv"), index=False)
    print(f"SAVED FILES: {saveLocation}")


def read_php_csv(filename):
    df = pd.read_csv(filename)
    print(df.head())
    df = apply_php_deserialization(df)
    print(df.head())
    return df


def apply_php_deserialization(df):
    df['elite_keywords'] = df['elite_keywords'].apply(deserializeItem)
    df['top_keywords'] = df['top_keywords'].apply(deserializeItem)
    return df


def generateComparisonsFile(df, country):
    cats = defineList()
    selections = {}
    tags = deduplicatedTagsByName(df)
    for cat in cats:
        selections[cat] = choose_multiple_from_dict(tags, 'tags', request_description=f'Please select the Tags you want to add to the category {cat}')
    # TODO (P0): Add resolution from TagName to unique Keyword list
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
    s = json.dumps(final)
    path = os.path.join(FS.Inputs, f'ProntoPro_Trends_Questions_{country.upper()}')
    with open(path, 'w+') as f:
        f.write(s)
        print(f"Saved file {path}")
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


def inputList(request_text="",item_type='str'):
    while True:
        inp = input(f"{request_text} (seperate by comma)\n").strip()
        try:
            if "," in inp:
                if item_type == 'str':
                    inp = map(lambda x: x.strip(), inp.split(","))
                elif item_type == 'int':
                    inp = map(lambda x: int(x), inp.split(","))
            else:
                if item_type == 'str':
                    inp = [inp]
                elif item_type == 'int':
                    inp = [int(inp)]
            return inp
        except Exception as e:
            print(e)

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
        kwds = False
        tag_ids = False
        if use_ids:
            tag_ids = inputList(request_text="Please input the tag ids to use", item_type='int')
        else:
            kwds = inputList(request_text="Please input the Contains-Match keywords to use", item_type='str')
        df = selectTagsFromDB(country.lower(), kwds=kwds, tag_ids=tag_ids)
        df = apply_php_deserialization(df)
    if binaryResponse("Do you want to create the CSV's to scrape keywords individually (y) or do you want to create the json files to scrape them in comparison (n)?"):
        prefix = ""
        if binaryResponse("Do you want to add a prefix to the filename?"):
            prefix = input("Please type the prefix:\n").strip()
        generateKeywordsFile(df, prefix_out=prefix, cc=country)
    else:
        generateComparisonsFile(df, country)

