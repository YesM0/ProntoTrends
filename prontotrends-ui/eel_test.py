import platform
import sys
import random

sys.path.extend(['../', '.../', './'])
from typing import List, Dict, Union, Any, Callable
from Validation.validationSetup import handleGUIData
from utils.custom_types import *
from utils.Countries import Country
from api.api_resolvers import get_available_comparisons, get_available_tags, get_available_category_overviews, \
    get_keywords_from_db
from Datapipeline.finalCSVgenerator import api_start
from Input_Set_Up.prepareKeywordsFile import api_file_creation

import eel


@eel.expose
def process_input(x):
    print(x)
    if x == 'y':
        return "Good job!"
    elif x == 'n':
        return 'This is false'
    else:
        return 'Try again'


@eel.expose
def get_comparisons(country_short_code: Country_Shortcode):
    return get_available_comparisons(Country(short_name=country_short_code))


@eel.expose
def get_category_overviews(country_short_code: Country_Shortcode, campaign_code: str) -> List[
    Dict[str, Union[str, bool]]]:
    c = Country(short_name=country_short_code)
    l = get_available_comparisons(c)
    l.extend(get_available_category_overviews(c, campaign_code))
    to_dict = map(lambda x: {'folder_name': x, 'chosen': False}, l)
    return list(to_dict)


@eel.expose
def get_tags(country_short_code: Country_Shortcode) -> List[Dict[str, Union[int, str, bool]]]:
    return get_available_tags(Country(short_name=country_short_code))


@eel.expose
def start_final_csv_generation(settings: dict):
    send_logs_to_frontend(f"Received task to create: {settings.get('chosenActions')}")
    api_start(settings, send_logs_to_frontend)


def send_logs_to_frontend(string):
    eel.show_log(string)


@eel.expose
def receive_data(data: Dict[str, Union[Dict[str, Any], str]]):
    """
    Universal receiver for data. Takes a dict of {destination: 'function', data: {DATA}}
    Args:
        data:

    Returns:

    """
    print(f"Type of data: {type(data)}")
    if data.get('destination', False) == 'ValidationSetUp':
        print('Matched destination')
        res = handleGUIData(data.get('data', {}), send_logs_to_frontend)
        return res
    elif data.get('destination', False) == 'InputSetup':
        print("Matched destination: InputSetup")
        print(data)
        eel.show_log(f'Creating Input_Setup: {data.get("data", {}).get("input_type", "NO INPUT TYPE FOUND")}')
        api_file_creation(data.get('data', {}), eel.show_log)
    else:
        print(data)


@eel.expose
def getLog():
    print("Got prompted for Log")
    eel.show_log('HI FROM PYTHON')


@eel.expose
def get_keywords_for_tags(country_short_name: Country_Shortcode, search_items: List[str]) -> List[
    Dict[str, Union[str, List[str], int]]]:
    country = Country(short_name=country_short_name)
    search_items = list(map(lambda x: int(x) if x.isnumeric() else x, search_items))
    try:
        results: List[Dict[str, Union[str, int, List[str]]]] = get_keywords_from_db(country, search_items=search_items)
        if results is not None:
            out = []
            for item in results:
                out.append({
                    "category": '',
                    "option": item['tag_name'],
                    'keywords': item['keywords'],
                    'tag_id': item.get('tag_id', random.randint(1, 2000))
                })
            return out
        else:
            eel.show_log("Could not get data from Database. This can be a connection problem or due to mistakes or missing credentials. Please check!", {'type': 'error'})
    except Exception as e:
        addition = ""
        if 'timeout' in e.__repr__().lower():
            addition = "Please try to wait for a while and try again."
        eel.show_log(f"Could not get data from Database. Error: {e}\n{addition}", {'type': 'error'})
    return []


def start_eel(develop):
    """Start Eel with either production or development configuration."""

    if develop:
        directory = 'src'
        app = None
        page = {'port': 3000}

        def close_callback(page, sockets):
            pass

        print("Starting eel")
    else:
        directory = 'build'
        app = 'chrome-app'
        page = 'index.html'
        close_callback = None

    eel.init(directory, ['.tsx', '.ts', '.jsx', '.js', '.html'], manual_js_functions=['show_log'])

    eel_kwargs = dict(
        host='localhost',
        port=8080,
        size=(1280, 800),
    )
    try:
        eel.start(page, mode=app, close_callback=close_callback, **eel_kwargs)
        print("Started eel")
    except EnvironmentError as e:
        # If Chrome isn't found, fallback to Microsoft Edge on Win10 or greater
        print("Environment Error", e)
        if sys.platform in ['win32', 'win64'] and int(platform.release()) >= 10:
            eel.start(page, mode='edge', **eel_kwargs)
        else:
            raise e


if __name__ == '__main__':
    import sys

    # Pass any second argument to enable debugging
    start_eel(develop=len(sys.argv) == 2)
