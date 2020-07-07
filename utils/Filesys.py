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
    typically settings should be found here: os.path.join(cwd, 'Input_Files', 'Static', '.settings.yaml')
    """

    def __init__(self, settings_file: str = None):
        """
        Sets up the main folders and file-locations
        Args:
            settings_file: str -- path to settings file
        """
        self.cwd: Folderpath = cwd
        self.Outfiles_general: Folderpath = makePath(cwd, 'Output_Files')
        self.Aggregated: Folderpath = makePath(cwd, 'Output_Files', 'Aggregated')
        self.Final: Folderpath = makePath(cwd, 'Output_Files', 'FINAL')
        self.Kwd_Level_Outs: Filepath = makePath(cwd, 'Output_Files', 'out')
        self.Comparisons: Folderpath = makePath(cwd, 'Output_Files', 'comparisons')
        self.Inputs: Folderpath = makePath(cwd, 'Input_Files')
        self.Statics: Folderpath = makePath(cwd, 'Input_Files', 'Static')
        self.Validation: Folderpath = makePath(cwd, 'Validation')
        if settings_file and ".yaml" in settings_file:
            import yaml
            with open(settings_file, "r") as f:
                s = f.read()
            d: dict = yaml.safe_load(s)
            self.Outfiles_general: Folderpath = d.get("Out_files_path", self.Outfiles_general)
            self.Aggregated: Folderpath = d.get("Aggregated_path", self.Aggregated)
            self.Final: Folderpath = d.get("Final_path", self.Final)
            self.Kwd_Level_Outs: Folderpath = d.get("Tag_out_path", self.Kwd_Level_Outs)
            self.Comparisons: Folderpath = d.get("Comparisons_path", self.Comparisons)
            self.Inputs: Folderpath = d.get("Inputs_path", self.Inputs)
            self.Statics: Folderpath = d.get("Statics_path", self.Statics)
            self.Validation: Folderpath = d.get('Validation_path', self.Validation)

        self.Settings_File: Filepath = makePath(self.Statics, '.settings.yaml') if os.path.exists(
            makePath(self.Statics, '.settings.yaml')) else None
        self.Ordered_Regions: Filepath = makePath(self.Statics, "ordered_regions.json") if os.path.exists(
            makePath(self.Statics, "ordered_regions.json")) else FileNotFoundError(
            f"The file 'ordered_regions' does not exist. Ensure that it is located in: {self.Statics}")
        self.All_Google_Locales: Filepath = makePath(self.Statics, "All_Google_Locales.json") if os.path.exists(
            makePath(self.Statics, "All_Google_Locales.json")) else FileNotFoundError(
            f"The file 'All_Google_Locales.json' does not exist. Ensure that it is located in: {self.Statics}")


generic_FileServer = Fileserver()

GDrive_FileServer = Fileserver(os.path.join(cwd, 'Input_Files', 'Static', '.settings.yaml'))

# TODO (p1): Add functions to find files / get subfolders
# TODO (p2): consider smaller classes: e.g. Aggregated_Folder class with custom utilities