import os
import platform
import sys

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


@eel.expose
def receive_data(data):
    print(data)
    print(f"Type of data: {type(data)}")


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