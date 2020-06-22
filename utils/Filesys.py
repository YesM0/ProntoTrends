if __name__ == '__main__':
    import sys
    sys.path.append('../')

import os
# import pandas as pd
from utils.custom_types import *

cwd = os.getcwd()
cwd = os.path.split(cwd)[0]


def makePath(*args) -> Filepath:
    return os.path.join(*args)


class Fileserver:
    """
    Represents the filesystem structure and implements utilities for opening and retrieving files
    """

    def __init__(self, settings_file: str = os.path.join(cwd, 'Input_Files', 'Static', '.settings.yaml')):
        """
        Sets up the main folders and file-locations
        Args:
            settings_file: str -- path to settings file
        """
        self.cwd: Filepath = cwd
        self.Outfiles_general: Filepath = makePath(cwd, 'Output_Files')
        self.Aggregated: Filepath = makePath(cwd, 'Output_Files', 'Aggregated')
        self.Final: Filepath = makePath(cwd, 'Output_Files', 'FINAL')
        self.Kwd_Level_Outs: Filepath = makePath(cwd, 'Output_Files', 'out')
        self.Comparisons: Filepath = makePath(cwd, 'Output_Files', 'comparisons')
        self.Inputs: Filepath = makePath(cwd, 'Input_Files')
        self.Statics: Filepath = makePath(cwd, 'Input_Files', 'Static')
        if settings_file and ".yaml" in settings_file:
            import yaml
            with open(settings_file, "r") as f:
                s = f.read()
            d: dict = yaml.safe_load(s)
            self.Outfiles_general: Filepath = d.get("Out_files_path", self.Outfiles_general)
            self.Aggregated: Filepath = d.get("Aggregated_path", self.Aggregated)
            self.Final: Filepath = d.get("Final_path", self.Final)
            self.Kwd_Level_Outs: Filepath = d.get("Tag_out_path", self.Kwd_Level_Outs)
            self.Comparisons: Filepath = d.get("Comparisons_path", self.Comparisons)
            self.Inputs: Filepath = d.get("Inputs_path", self.Inputs)
            self.Statics: Filepath = d.get("Statics_path", self.Statics)

        self.Settings_File = settings_file
        self.Ordered_Regions = makePath(self.Statics, "ordered_regions.json") if os.path.exists(
            makePath(self.Statics, "ordered_regions.json")) else FileNotFoundError(
            f"The file 'ordered_regions' does not exist. Ensure that it is located in: {self.Statics}")
        self.All_Google_Locales = makePath(self.Statics, "All_Google_Locales.json") if os.path.exists(
            makePath(self.Statics, "All_Google_Locales.json")) else FileNotFoundError(
            f"The file 'All_Google_Locales.json' does not exist. Ensure that it is located in: {self.Statics}")


generic_FileServer = Fileserver()

# TODO (p1): Add functions to find files / get subfolders
# TODO (p2): consider smaller classes: e.g. Aggregated_Folder class with custom utilities