if __name__ == '__main__':
    import sys

    sys.path.append('../')

import os
from typing import List, Dict, Union, Tuple, Optional

from utils.custom_types import *
from utils.sql_utils import establish_SQL_cursor, get_sql_login_data, construct_query_tags_keywords, define_sql_date, \
    construct_switch, resolve_where_dict, assemble_where
from utils.user_interaction_utils import binaryResponse, chooseFolder, chooseFile, choose_from_dict, \
    choose_multiple_from_dict, defineList, user_input, int_input
from utils.Filesys import generic_FileServer as FS
from utils.Countries import getCountry, Country
from utils.misc_utils import lcol, save_csv, rescale_comparison
from Datapipeline.create_custom_file import formatDate, convert_region_names_to_google

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
        self.data: Union[Dict[str, pd.DataFrame], None] = {}

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

    def execute(self, statement: str, statement_title: str = None) -> Optional[pd.DataFrame]:
        while not self.isConnected:
            print("Trying to establish connection")
            self.connect()
            if not self.isConnected and not binaryResponse('Do you want to try again?'):
                return
            else:
                break
        try:
            result: pd.DataFrame = pd.read_sql(statement, self.connection)
            if statement_title:
                self.data[statement_title] = result
            return result
        except Exception as e:
            print(e)
        finally:
            self.close()

    def save_data(self):
        """
        Saves the data in self.data
        Returns:

        """
        path = os.path.join(FS.Outfiles_general, '.temp', repr(self))
        for k, data in self.data.items():
            save_csv(data, os.path.join(path, f"{k}.csv"), index=False)

    def load_data(self):
        """
        Loads data from a csv chosen by the user
        Returns:

        """
        base = os.path.join(FS.Outfiles_general, '.temp', repr(self))
        filepath = chooseFile(filetype='csv', base_path=base, request_prompt="Which file do you want to load?")
        fname = os.path.split(filepath)[1]
        key = "".join(fname.split('.')[:-1])
        data = pd.read_csv(filepath)
        self.data[key] = data


# noinspection SqlResolve
class Ticket_Detail_Inquiry(Inquiry):
    """
    Class for Inquiry's into what choices people make relating to their services.
    For example: what type of wedding do they hire Pro's for?

    Uses ticket.fields for determining categories using LIKE matches
    """

    def __init__(self, country: Country = None, db_login_data: Dict[str, str] = None, category_name: str = None):
        super().__init__(country, db_login_data)
        self.name = category_name
        self.query = None
        self.tags_included = None
        self.min_date = None
        self.switch_dict = None
        self.group_by_tag_name = False

    def __repr__(self):
        s: str = f"Ticket_Detail-Inquiry [{self.country.Shortcode.upper()}]"
        if self.data is not None:
            s += f" Data gathered: {len(list(self.data.keys()))}"
        return s

    def define_query_settings(self, tags_included: Union[List[Union[int, str]], None] = None,
                              min_date: Union[None, str] = "'2018-01-01'",
                              switch_dict: Union[None, Dict[str, Union[List[str], str]]] = None):
        """
        Handles the user interaction to set up the query settings
        Args:
            tags_included:
            min_date:
            switch_dict:

        Returns:

        """
        self.tags_included: Union[List[int, str], None] = tags_included
        self.min_date: Union[None, str] = min_date  # ensure formatting with extra quotation marks
        self.switch_dict: Union[None, Dict[str, Union[List[str], str]]] = switch_dict
        if self.name is None:
            self.name = user_input("What is the name of the category this inquiry is for? (e.g. wedding location)",
                                   blocked_contents=["/"]).strip()
        if binaryResponse("Do you have a file with the settings prefilled?"):
            # TODO (p1): use a file to replace the data - add where the file is missing fields
            pass
        # define tags_included
        if self.tags_included is None and binaryResponse("Do you want to limit the list of tags included?"):
            way = choose_from_dict({0: 'Tag_Id', 1: 'Tag Name'}, label="way",
                                   request_description='Based on what do you want to limit the tags?')
            if way == 'Tag_Id':
                self.tags_included: List[int] = defineList(label='Tag Ids', wanted_type='int')
            else:
                self.tags_included: List[str] = defineList(label='Tag Names')
        if self.group_by_tag_name is not True:
            self.group_by_tag_name = binaryResponse(
                "Do you want to group the output by tag_name? Often this is not desired")
        if self.min_date is None or binaryResponse(
                f"Do you want to use a different minimum date than {self.min_date}?"):
            self.min_date = define_sql_date()
        if self.switch_dict is None:
            if not binaryResponse("Do you already know what options there are in the fields of the database?"):
                # get examples of fields from db
                where = assemble_where(settings={'IN': {
                    't2.id': self.tags_included
                }})
                query = f"SELECT t2.name, t.fields \nFROM {self.db}.ticket t\n LEFT JOIN {self.db}.tag t2 on t.tag_id = t2.id\n{where}\nLIMIT 10"
                l = self.execute(statement=query, do_retain_data=False)
                for ind, row in l.iterrows():
                    print(row['name'], row['fields'])
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
        """
        Takes instance properties switch_dict and tags_included and generates the query. Set to self.query
        Returns: void -

        """
        columns = "SELECT\nYEAR(t.status_new_at) as 'year',\nMONTH(t.status_new_at) as 'month',\nr.name as 'ticket_geo_region_name',\n"
        if self.group_by_tag_name:
            columns += "t2.name as 'ticket_taxonomy_tag_name',\n"
        columns += construct_switch(self.switch_dict, "t.fields", 'LIKE') + " as 'Options',\ncount(t.id)"
        tables = f"FROM {self.db}.ticket t\nLEFT JOIN {self.db}.tag t2 on t.tag_id = t2.id\nLEFT JOIN {self.db}.locality l on t.locality_id = l.id\nLEFT JOIN {self.db}.province p on l.province_id = p.id\nLEFT JOIN {self.db}.region r on p.region_id = r.id"
        tag_selector = ("t2.id", 'IN') if any(list(map(lambda x: isinstance(x, int), self.tags_included))) else (
            "t2.name", 'LIKE')
        where_settings = {
            "AND": {
                tag_selector[1]: {
                    tag_selector[0]: self.tags_included
                }
            }
        }
        where = assemble_where(where_settings)
        groupby = "GROUP BY 1,2,3,4,5" if self.group_by_tag_name else "GROUP BY 1,2,3,4"
        self.query = "\n".join([columns, tables, where, groupby])
        print(self.query)

    def execute(self, statement: str = None, statement_name: str = None, do_retain_data: bool = True):
        title = self.name if do_retain_data else None
        statement = statement if statement else self.query
        result = super().execute(statement, statement_title=title)
        if do_retain_data:
            self.data[self.name] = result
        return result

    def treat_data(self):
        for k, df in self.data.items():
            saving_folder = os.path.join(FS.Comparisons, self.country.Full_name, self.name)
            pivot_col = 'Options'
            grouping: list = ['year', 'month']
            # do pivot stuff
            selections = {}
            options = df[pivot_col].unique().tolist()
            to_drop = []
            dimension = 'Time'
            df, has_date = formatDate(df)
            index = ['date']
            index = index + ['ticket_geo_region_name']
            to_drop = ['year', 'month', 'day']
            df = df.drop(columns=to_drop)
            pivot = df.pivot_table(index=index, columns=pivot_col, aggfunc=sum, fill_value=0)
            pivot.reset_index()
            grouped = pivot.groupby(index[-1])
            for name, group in grouped:
                print(group)
                # group = group.rename(columns=lambda x: x.split("/")[1] if isinstance(x, str) else x[1])
                group = rescale_comparison(group, scale=100)
                group = group.reset_index()
                group = convert_region_names_to_google(group)
                region_id = group[index[-1]].unique().tolist()[0]
                filename = f"{dimension}_Italy_{region_id}_{self.name}.csv"
                group = group.drop(columns=[index[-1]])
                cols = list(map(lambda col: col[0] if len(col[1]) == 0 else col[1], group.columns))
                group.columns = cols
                save_csv(group, os.path.join(saving_folder, filename), index=False)
            # create Italy
            italy = pivot.groupby(index[0]).sum()
            italy = rescale_comparison(italy, scale=100)
            italy = italy.reset_index()
            cols = list(map(lambda col: col[0] if len(col[1]) == 0 else col[1], italy.columns))
            italy.columns = cols
            region_id = 'IT'
            filename = f"{dimension}_Italy_{region_id}_{self.name}.csv"
            save_csv(italy, os.path.join(saving_folder, filename), index=False)


def process_tag_time_data(group):
    """
    Used by Ticket_Count_Inquiry

    Args:
        group:

    Returns:

    """
    # get max
    maximum: float = group['Index'].max()
    # rescale values
    group['means'] = group['Index'].apply(lambda x: (x / maximum) * 100)
    # convert to dates
    group, _ = formatDate(group)
    # fill missing months
    group = group.resample('M', on='date').mean()
    # remove cols: final: ['date', 'means']
    cleaned = group.drop(columns=[col for col in
                                  ['year', 'month', 'tag_id', 'ticket_taxonomy_tag_name', 'ticket_geo_region_name',
                                   'Index'] if col in group.columns])
    return cleaned


class Ticket_Count_Inquiry(Inquiry):
    """
    Class for Inquiry's into what tags are requested how frequently
    For example: How does the demand for painters debelop over the year?

    --> ONLY Handles Time Information (no geo - as needs comparison with all tags in region in timeframe)
    """

    def __init__(self, country: Country = None, db_login_data: Dict[str, str] = None, name: str = None):
        super().__init__(country, db_login_data)
        self.name = None
        self.query = None
        self.tags_included = None
        self.min_date = None
        self.tag_merges = None  # to be a dict of New Name and previous name
        self.id_merges = None
        self.geo_query = None
        self.region_scaling_factors = {}

    def __repr__(self):
        s: str = f"Ticket_Count-Inquiry [{self.country.Shortcode.upper()}]: {self.name}"
        if self.data is not None:
            s += f" Data gathered: {len(list(self.data.keys()))}"
        return s

    def define_query_settings(self, tags_included: Union[List[Union[int, str]], None] = None,
                              min_date: Union[None, str] = "'2018-01-01'",
                              switch_dict: Union[None, Dict[str, Union[List[str], str]]] = None):
        """
        Handles the user interaction to set up the query settings
        Args:
            tags_included:
            min_date:
            switch_dict:

        Returns:

        """
        self.tags_included: Union[List[int, str], None] = tags_included
        self.min_date: Union[None, str] = min_date  # ensure formatting with extra quotation marks
        self.switch_dict: Union[None, Dict[str, Union[List[str], str]]] = switch_dict
        if binaryResponse("Do you have a file with the settings prefilled?"):
            # TODO (p1): use a file to replace the data - add where the file is missing fields
            pass
        if self.name is None:
            self.name = user_input("What is the subject of this inquiry? (e.g. Wedding)")
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
            self.min_date: str = define_sql_date()
        if self.tag_merges is None and binaryResponse("Do you want to merge individual tags together?"):
            merge_dict: Dict[str, List[str]] = {}
            base_merges: List[str] = defineList(label='new tag_names')
            tags_involved_in_merges: List[str] = []
            for merge_name in base_merges:
                selection: List[str] = defineList(label=f'tagnames to merge to {merge_name}')
                merge_dict[merge_name] = selection
                tags_involved_in_merges.extend(selection)
            # get the associated tag ids and select one per new tags
            where = assemble_where(settings={'IN': {
                't.id': tags_involved_in_merges
            }})
            q = f"SELECT t.id as 'id', t.name as 'name' FROM {self.db}.tag {where}"
            lst: pd.DataFrame = self.execute(q, do_retain_data=False)
            lookup: Dict[str, int] = {row[1]: row[0] for i, row in lst.iterrows()}  # converts df to Dict[name: id]
            id_merges: Dict[int, List[int]] = {}
            counter = 0
            for merge_name, merge_items in merge_dict.items():
                new_id = 9900 + counter
                id_merge_items = [id_merges.get(item, None) for item in merge_items if
                                  id_merges.get(item, None) is not None]
                id_merges[new_id] = id_merge_items
            self.tag_merges = merge_dict
            self.id_merges = id_merges

    def construct_query(self):
        """
        Takes instance properties switch_dict and tags_included and generates the query. Set to self.query
        Returns: void -

        """
        columns = "SELECT\nYEAR(t.status_new_at) as 'year',\nMONTH(t.status_new_at) as 'month',\nr.name as 'ticket_geo_region_name',\n"
        # \nt2.id as 'tag_id'\nt2.name as 'ticket_taxonomy_tag_name',\n"
        columns += construct_switch(self.id_merges, "t2.id", '=') + " as 'tag_id',\n"
        columns += construct_switch(self.tag_merges, 't2.name',
                                    '=') + " as 'ticket_taxonomy_tag_name',\ncount(t.id) as 'Index'"
        tables = f"FROM {self.db}.ticket t\nLEFT JOIN {self.db}.tag t2 on t.tag_id = t2.id\nLEFT JOIN {self.db}.locality l on t.locality_id = l.id\nLEFT JOIN {self.db}.province p on l.province_id = p.id\nLEFT JOIN {self.db}.region r on p.region_id = r.id"
        tag_selector = ("t2.id", 'IN') if any(list(map(lambda x: isinstance(x, int), self.tags_included))) else (
            "t2.name", 'LIKE')
        where_settings = {
            "AND": {
                tag_selector[1]: {
                    tag_selector[0]: self.tags_included
                },
                '>=': {
                    't.status_new_at': self.min_date
                }
            }
        }
        where = assemble_where(where_settings)
        groupby = "GROUP BY 1,2,3,4,5"
        self.query = "\n".join([columns, tables, where, groupby])
        print(self.query)

    def construct_geo_query(self, tag_level: bool = True):
        columns = "SELECT\nr.name as 'ticket_geo_region_name',\n"
        # \nt2.id as 'tag_id'\nt2.name as 'ticket_taxonomy_tag_name',\n"
        where_settings = {
            "AND": {
                '>=': self.min_date
            }
        }
        if tag_level:
            columns += construct_switch(self.id_merges, "t2.id", '=') + " as 'tag_id',\n"
            columns += construct_switch(self.tag_merges, 't2.name',
                                        '=') + " as 'ticket_taxonomy_tag_name',\ncount(t.id) as 'Index'"
            tables = f"FROM {self.db}.ticket t\nLEFT JOIN {self.db}.tag t2 on t.tag_id = t2.id\nLEFT JOIN {self.db}.locality l on t.locality_id = l.id\nLEFT JOIN {self.db}.province p on l.province_id = p.id\nLEFT JOIN {self.db}.region r on p.region_id = r.id"
            tag_selector = ("t2.id", 'IN') if any(list(map(lambda x: isinstance(x, int), self.tags_included))) else (
                "t2.name", 'LIKE')
            where_settings['AND'][tag_selector[1]] = {
                tag_selector[0]: self.tags_included
            }
            groupby = "GROUP BY 1,2,3"
        else:
            columns += "count(t.id) as 'Index'"
            tables = f"FROM {self.db}.ticket t\nLEFT JOIN {self.db}.locality l on t.locality_id = l.id\nLEFT JOIN {self.db}.province p on l.province_id = p.id\nLEFT JOIN {self.db}.region r on p.region_id = r.id"
            groupby = "GROUP BY 1"
        where = assemble_where(where_settings)
        q = "\n".join([columns, tables, where, groupby])
        if tag_level:
            self.geo_query = q
        return q

    def execute(self, statement: str = None, statement_name: str = None, do_retain_data: bool = True) -> pd.DataFrame:
        title = self.name if do_retain_data else None
        statement = statement if statement else self.query
        result = super().execute(statement, statement_title=title)
        if do_retain_data:
            self.data[self.name] = result
        return result

    def get_geo_data(self):
        restricted_query: str = self.construct_geo_query()
        unrestricted_query: str = self.construct_geo_query(tag_level=False)
        df_restricted: pd.DataFrame = self.execute(restricted_query, statement_name=f"Geo-Data")
        region_totals: pd.DataFrame = self.execute(unrestricted_query, statement_name=f"Geo-Data All_Tags").set_index(
            'ticket_geo_region_name')
        split_groups: pd.DataFrameGroupBy = df_restricted.groupby(['ticket_taxonomy_tag_name', 'tag_id'])

        def scale_region_level(row, region_level_df):
            region_name = row['ticket_geo_region_name']
            luv = region_level_df.loc[region_name, 'Index']
            row['Index'] = row['Index'] / luv
            return row

        for (tag_name, tag_id), group in split_groups:
            group_percentages_of_all_tickets_in_region: pd.DataFrame = group.apply(scale_region_level,
                                                                                   args=(region_totals,), axis=1)
            index_max: float = group_percentages_of_all_tickets_in_region['Index'].max()
            final_scaled: pd.DataFrame = group_percentages_of_all_tickets_in_region['Index'].apply(
                lambda x: (x / index_max) * 100)
            save_csv(final_scaled, os.path.join(FS.Aggregated, self.country.Full_name, f"{self.country.Shortcode.upper()}_{tag_id}_{tag_name}_Geo.csv"))
            self.region_scaling_factors[tag_name] = {row['ticket_geo_region_name']: row['Index'] for _, row in
                                                     final_scaled.iterrows()}

    def treat_data(self):
        self.get_geo_data()
        for k, df in self.data.items():
            saving_folder: Folderpath = os.path.join(FS.Aggregated, self.country.Full_name)
            grouping_cols: List[str] = ['ticket_geo_region_name', 'tag_id', 'ticket_taxonomy_tag_name']
            df = convert_region_names_to_google(df)
            groups = df.groupby(grouping_cols)
            for (region_id, tag_id, tag_name), group in groups:
                cleaned: pd.DataFrame = process_tag_time_data(group)
                # save
                save_csv(cleaned, os.path.join(saving_folder, f"{region_id}_{tag_id}_{tag_name}_Time.csv"), index=False)
                cleaned['means'] = cleaned['means'].apply(lambda x: x * (self.region_scaling_factors.get(tag_name, {}).get(region_id, 1)))
                save_csv(cleaned, os.path.join(saving_folder, f"{region_id}_{tag_id}_{tag_name}_Time_Adjusted.csv"), index=False)
            italy_grouped = df.groupby(grouping_cols[1:]).sum()
            for (tag_id, tag_name), group in italy_grouped:
                cleaned = process_tag_time_data(group)
                # save
                save_csv(cleaned, os.path.join(saving_folder, f"{self.country.Shortcode.upper()}_{tag_id}_{tag_name}_Time.csv"), index=False)


if __name__ == '__main__':
    t = Ticket_Detail_Inquiry(country=Country(short_name='it'), db_login_data=None)
    try:
        t.define_query_settings()
        t.construct_query()
        t.execute()
        t.treat_data()
        print(t)
    except Exception as e:
        print(e)
    finally:
        try:
            t.close()
        except Exception as e:
            print(e)
