import pandas as pd
from pytrends.request import TrendReq
import utils.paramsGetter as paramsGetter
import time
import os
import random
import datetime
from utils.Filesys import generic_FileServer
from utils.misc_utils import getRandomDelay, getToday, saveData, sleep

FS = generic_FileServer


def readInKeywords():
    params = pd.read_csv(os.path.join(FS.Inputs, "Keywords_DE.csv"))
    # params = params['Keyword']
    return params


def scrapeCountry(keyword, countryName, pytrends, keyword_id=''):
    cwd = os.getcwd()
    ccInfo = paramsGetter.findLocale(countryName, includeChildren=True)
    regionIds = [f"{ccInfo[0]}-{x}" for x in ccInfo[1]]
    locales_list = [ccInfo[0]] + regionIds
    directory = os.path.join(FS.Kwd_Level_Outs, keyword)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # scrape multiline for each locale
    for id, locale in enumerate(locales_list):
        if id > 0:
            sleep(getRandomDelay())
        print(f"Scraping KW {keyword} for {locale}")
        while True:
            try:
                pytrends.build_payload([keyword], timeframe=f'2018-01-01 {getToday()}', geo=locale, gprop='')
                result = pytrends.interest_over_time()
                break
            except Exception as e:
                print(e)
        print(f"Got data. Shape: {result.shape}")
        print(result.head())
        if (result.size == 0 and id == 0):
            print("No Data")
            return keyword
        if result.size != 0:
            filepath = os.path.join(directory, f"Time_{countryName}_{locale}_{keyword}_{keyword_id}.csv")
            saveData(result, filepath)
            print("Saved Data")

    sleep(getRandomDelay())
    # scrape region
    print("Scraping Geo Data")
    while True:
        try:
            pytrends.build_payload([keyword], timeframe='today 3-m', geo=ccInfo[0], gprop='')
            result = pytrends.interest_by_region(resolution='REGION', inc_low_vol=True, inc_geo_code=True)
            break
        except Exception as e:
            print(e)
    saveData(result, os.path.join(directory, f"Geo_{countryName}_{keyword}_{keyword_id}.csv"))
    return False


def prepareTrendReqObj():
    pytrends = TrendReq(hl='en-US', tz=60)
    return pytrends


if __name__ == '__main__':
    tr = prepareTrendReqObj()
    keywords = readInKeywords()
    failedScrapes = []
    for row_index, row in keywords.iterrows():
        keyword = row['Keyword']
        kwd_id = row['kwd_id']
        print(f"Working on keyword {keyword}")
        bad_result = scrapeCountry(keyword, 'Germany', tr, keyword_id=kwd_id)
        sleep(getRandomDelay())
        if bad_result:
            failedScrapes.append(bad_result)
    print("_" * 10 + "FINISHED" + "_" * 10)
    print("Failed Scrapes")
    print(failedScrapes)
