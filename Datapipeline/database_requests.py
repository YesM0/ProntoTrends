if __name__ == '__main__':
    import sys

    sys.path.append('../')

import os
from typing import List, Dict, Union, Tuple

from utils.custom_types import *
from utils.sql_utils import establish_SQL_cursor, get_sql_login_data, construct_query_tags_keywords, define_sql_date
from utils.user_interaction_utils import binaryResponse, chooseFolder, chooseFile, choose_from_dict, \
    choose_multiple_from_dict, defineList, user_input, int_input
from utils.Filesys import generic_FileServer as FS
from utils.Countries import getCountry, Country
from utils.misc_utils import lcol

import pandas as pd
import pymysql


# TODOs:
#  TODO: Function that retrieves ticket counts per tag - incl. merging tags
#  TODO: Function that retrieves total ticket counts to symmetric year and regions
#  TODO: Function that normalizes ticket counts per tag based on total ticket counts
#  TODO: Function that retrieves counts based on Fields answers
#  TODO: Function that handles user choices for merging or handles json/yaml input


#  TODO: Function to set up everything

class Inquiry:
    """
    Generic Inquiry Class. Inherited from by other types of requests
    """

    def __init__(self, country: Country = None, db_login_data: Dict[str, str] = None):
        self.country: Country = getCountry(
            prompt="What country do you want to make database requests for?") if country is None else country
        self.db: str = self.country.Database
        self.access_details: Dict[str, str] = get_sql_login_data() if not db_login_data or not (
                'host' in db_login_data and 'user' in db_login_data and 'password' in db_login_data) else db_login_data
        self.connection: Union[pymysql.Connection, bool] = False
        self.isConnected: bool = False
        self.data: Union[Dict[str, pd.DataFrame], None] = None

    def __repr__(self) -> str:
        s: str = f"Generic Inquiry [{self.country.Shortcode.upper()}]"
        if self.data is not None:
            s += f" Data gathered: {len(list(self.data.keys()))}"
        return s

    def connect(self) -> pymysql.Connection:
        try:
            self.connection: pymysql.Connection = establish_SQL_cursor(self.access_details)
            self.isConnected = True
        except Exception as e:
            print(f"There was a problem establishing a connection. Please check your VPN and try again")
            print(e)
        return self.connection

    def close(self):
        self.connection.close()
        self.isConnected = False

    def execute(self, statement: str, statement_title: str = None):
        while not self.isConnected:
            self.connect()
            if not binaryResponse('Do you want to try again?'):
                return
        try:
            result: pd.DataFrame = pd.read_sql(statement, self.connection)
            if statement_title:
                self.data[statement_title] = result
            return result
        except Exception as e:
            print(e)
        finally:
            self.close()


class Ticket_Detail_Inquiry(Inquiry):
    """
    Class for Inquiry's into what choices people make relating to their services.
    For example: what type of wedding do they hire Pro's for?

    Uses ticket.fields for determining categories using LIKE matches
    """

    def __init__(self, country: Country = None, db_login_data: Dict[str, str] = None):
        super().__init__(country, db_login_data)
        self.query = None
        self.tags_included = None
        self.min_date = None
        self.switch_dict = None

    def __repr__(self):
        s: str = f"Ticket_Detail-Inquiry [{self.country.Shortcode.upper()}]"
        if self.data is not None:
            s += f" Data gathered: {len(list(self.data.keys()))}"
        return s

    def define_query_settings(self, tags_included: Union[List[int, str], None] = None,
                     min_date: Union[None, str] = "'2018-01-01'",
                     switch_dict: Union[None, Dict[str, Union[List[str], str]]] = None):
        self.tags_included: Union[List[int, str], None] = tags_included
        self.min_date: Union[None, str] = min_date  # ensure formatting with extra quotation marks
        self.switch_dict: Union[None, Dict[str, Union[List[str], str]]] = switch_dict
        if binaryResponse("Do you have a file with the settings prefilled?"):
            # TODO: use a file to replace the data - add where the file is missing fields
            pass
        # define tags_included
        if self.tags_included is None and binaryResponse("Do you want to limit the list of tags included?"):
            way = choose_from_dict({0: 'Tag_Id', 1: 'Tag Name'}, label="way",
                                   request_description='Based on what do you want to limit the tags?')
            if way == 'Tag_Id':
                self.tags_included: List[int] = defineList(label='Tag Ids', wanted_type='int')
            else:
                self.tags_included: List[str] = defineList(label='Tag Names')
        if self.min_date is None or binaryResponse(
                f"Do you want to use a different minimum date than {self.min_date}?"):
            self.min_date = define_sql_date()
        if self.switch_dict is None:
            print(
                f"{lcol.OKGREEN}Please define the categories in which different field answers should be grouped{lcol.OKGREEN}")
            categories = defineList()
            for cat in categories:
                print(f"{lcol.OKGREEN}What cases should we match to the category {cat}{lcol.ENDC}")
                cat_likes = defineList(label='cases')
                if self.switch_dict is None:
                    self.switch_dict = {cat: cat_likes}
                else:
                    self.switch_dict[cat] = cat_likes

    def construct_query(self):
