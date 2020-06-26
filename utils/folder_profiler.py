import os
from typing import Dict, List, Union
from utils.custom_types import *
from utils.Filesys import generic_FileServer as FS
from utils.user_interaction_utils import chooseFolder
import json


def explore_directory(directory_path: Folderpath) -> List[Dict[str, List[Union[dict, str]]]]:
    print(f"Exploring folder: {directory_path}")
    cont = []
    contents = os.listdir(directory_path)
    files = [item for item in contents if
             os.path.isfile(os.path.join(directory_path, item)) and not item.startswith(".")]
    folders = [item for item in contents if os.path.isdir(os.path.join(directory_path, item)) and item not in ['venv',
                                                                                                               "__pycache__"] and not item.startswith(
        ".")]
    cont.extend(files)
    folders = {folder: explore_directory(os.path.join(directory_path, folder)) for folder in folders}
    if len(list(folders.keys())) > 0:
        cont.append(folders)
    return cont


if __name__ == '__main__':
    start_folder = chooseFolder(base_folder=FS.cwd, request_str="Where do you want to start exploring the files?")
    result = explore_directory(start_folder)
    filepath = os.path.join(FS.cwd, "folder_profiler_result.json")
    with open(filepath, "w+") as f:
        f.write(json.dumps(result, indent=4))
        print(f"Saved output in file://{filepath}")
