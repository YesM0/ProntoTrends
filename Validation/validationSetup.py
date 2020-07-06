import os
import json
from typing import List, Dict
from utils.Filesys import generic_FileServer as FS


def handleGUIData(data, logging_func):
    print(f"Data passed In handle GUI {data}")
    country: str = data.get('country', False)
    fileName: str = data.get('title', False)
    columns: List[str] = data.get('colNames', False)
    labels: Dict[str, List[str]] = data.get('labels', False)
    label_counts = data.get('labelCounts', False)
    separators = data.get('separators', False)
    var_types = data.get('variableTypes', False)
    if not country or not fileName:
        return 'Error'
    else:
        dictionary = {'separators': separators}
        if isinstance(columns, list):
            dictionary['columns'] = columns
        if isinstance(labels, dict):
            dictionary['labels'] = labels
        if isinstance(label_counts, dict):
            dictionary['label_counts'] = label_counts
        if isinstance(var_types, dict):
            dictionary['var_types'] = var_types
        fname = fileName if fileName.endswith('.json') else f"{fileName}.json"
        folderpath = os.path.join(FS.Validation, country)
        if not os.path.exists(folderpath):
            os.makedirs(folderpath)
        with open(os.path.join(folderpath, fname), "w+") as f:
            f.write(json.dumps(dictionary))
        logging_func(f"Saved file: {os.path.join(folderpath, fname)}")
        return f"Saved file: {os.path.join(folderpath, fname)}"
