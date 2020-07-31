import platform
import sys
import random
import time
import os
import eel

sys.path.extend(['../', '.../', './'])

from typing import List, Dict, Union, Any, Callable
from Validation.validationSetup import handleGUIData
from utils.custom_types import *
from utils.Countries import Country
from utils.sql_utils import get_sql_login_data, create_credentials_file_api
from utils.Filesys import generic_FileServer as FS
from api.api_resolvers import get_available_comparisons, get_available_tags, get_available_category_overviews, \
    get_keywords_from_db, get_scraping_input_file, get_data_for_options, get_csv, get_available_options
from Datapipeline.finalCSVgenerator import api_start
from Input_Set_Up.prepareKeywordsFile import api_file_creation
from Datapipeline.mainProxy import api_access as scraper_api_access


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
    eel.notification(string)


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
        eel.notification(f'Creating Input_Setup: {data.get("data", {}).get("input_type", "NO INPUT TYPE FOUND")}')
        api_file_creation(data.get('data', {}), eel.notification)
    else:
        print(data)


@eel.expose
def getLog():
    print("Got prompted for Log")
    eel.notification('HI FROM PYTHON')


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
            eel.notification(
                "Could not get data from Database. This can be a connection problem or due to mistakes or missing credentials. Please check!",
                {'type': 'error'})
    except Exception as e:
        addition = ""
        if 'timeout' in e.__repr__().lower():
            addition = "Please try to wait for a while and try again."
        eel.notification(f"Could not get data from Database. Error: {e}\n{addition}", {'type': 'error'})
    return []


@eel.expose
def get_db_access_data():
    d = get_sql_login_data(True)
    if d is not None:
        eel.notification("Found saved login data")
        return d
    else:
        eel.notification("Did not find saved Login data")
        return {}


@eel.expose
def save_db_access_data(details):
    success = create_credentials_file_api(details, eel.notification)
    print(f"Saving successful? {success}")


@eel.expose
def sendLogs():
    for i in range(1000):
        time.sleep(0.1)
        if i % 100 == 0:
            eel.receiveLog(f"Iteration {i}")


@eel.expose
def get_scraping_file(country_short_name: Country_Shortcode, campaign_short_code: str, scraping_type: str) -> Filepath:
    print("Inputs to get_scraping_file")
    print(f"{country_short_name} - {campaign_short_code} - {scraping_type}")
    res = get_scraping_input_file(Country(short_name=country_short_name), campaign_short_code, scraping_type)
    if res == "":
        return "No File was found. Please select manually"
    else:
        return res


@eel.expose
def scrape(settings_dict: Dict[str, Union[bool, str, Filepath]]):
    actions = {
        "Individual - All Regions": 'Individual Keywords ("Keywords_CC.csv) - All Regions',
        "Individual - CC only": 'Individual Keywords ("Keywords_CC.csv) - Only Country',
        'Comparison': 'Comparisons (ProntoPro_Trends_Questions_CC.csv) - All Regions'
    }
    chosen_action = actions.get(settings_dict.get("scraping_type", None), None)
    if chosen_action:
        file = settings_dict.get("sourceFile", "")
        if os.path.sep not in file:
            file = os.path.join(FS.Inputs, file)
        country = Country(short_name=settings_dict.get('country_short_name', ""))
        deduplicateKeywords = settings_dict.get('deduplicate_keywords', False)
        prefix = settings_dict.get('campaign_short_code', '')
        scraper_api_access(chosen_action, country, file, deduplicateKeywords, prefix)
    else:
        eel.notification("Invalid action chosen", {'type': 'error'})


@eel.expose
def get_final_category_overviews(country_short_name: Country_Shortcode, campaign_name: str):
    return get_available_category_overviews(country=Country(short_name=country_short_name), campaign_name=campaign_name)


@eel.expose
def get_available_campaigns(country_short_name: Country_Shortcode):
    country = Country(short_name=country_short_name)
    return [x for x in os.listdir(os.path.join(FS.Final, country.Full_name)) if os.path.isdir(os.path.join(FS.Final, country.Full_name, x)) and not x.startswith(".")]


@eel.expose
def get_available_options_from_file(filepath: Filepath):
    print("Called get_available_options")
    csv_path = get_csv(filepath)
    print(f'Got csv path: {csv_path}')
    options = get_available_options(csv_path)
    for col, opts in options.items():
        options[col] = [{'value': x, 'label': x} for x in opts]
    options['full_csv_path'] = csv_path
    print("Got options")
    return options


@eel.expose
def get_data_for_chosen_options(filepath, year, region):
    return get_data_for_options(filepath, year, region)


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

    eel.init(directory, ['.tsx', '.ts', '.jsx', '.js', '.html'], manual_js_functions=['notification', 'ScraperReceiveStatus', 'console_log'])

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
