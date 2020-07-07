import os
import platform
import sys
if __name__ == '__main__':
    sys.path.extend(['../', '.../', './'])
from typing import List, Dict, Union, Optional, Any
from Validation.validationSetup import handleGUIData

sys.path.extend(['../../', '../', './'])
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
    print(data)
    print(f"Type of data: {type(data)}")
    if data.get('destination', False) == 'ValidationSetUp':
        print('Matched destination')
        res = handleGUIData(data.get('data', {}), send_logs_to_frontend)
        return res


@eel.expose
def getLog():
    print("Got prompted for Log")
    eel.show_log('HI FROM PYTHON')



def start_eel(develop):
    """Start Eel with either production or development configuration."""

    if develop:
        directory = 'src'
        app = None
        page = {'port': 3000}
        print("Starting eel")
    else:
        directory = 'build'
        app = 'chrome-app'
        page = 'index.html'

    eel.init(directory, ['.tsx', '.ts', '.jsx', '.js', '.html'])


    eel_kwargs = dict(
        host='localhost',
        port=8080,
        size=(1280, 800),
    )
    try:
        eel.start(page, mode=app, **eel_kwargs)
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