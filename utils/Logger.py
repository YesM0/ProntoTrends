if __name__ == '__main__':
    import sys
    sys.path.extend(['./', '../', '.../'])

import logging
from typing import Callable
import eel
from utils.misc_utils import lcol


class Logger:
    def __init__(self, Debug_Log_Function: Callable = None, Dev_Error_Function: Callable = None,
                 User_Info_Function: Callable = None, User_Notification_Function: Callable = None,
                 User_Error_Function: Callable = None, Default_Function: Callable = None):
        if any([v is not None for k, v in locals().items()]):
            logging.basicConfig(
                format=f'{lcol.OKBLUE}%(threadName)s:%(levelname)s - %(module)s - %(funcName)s - {lcol.ENDC}%(message)s',
                level=logging.INFO)
        self.debug = Debug_Log_Function if Debug_Log_Function is not None else logging.debug
        self.dev_error = Dev_Error_Function if Dev_Error_Function is not None else logging.error
        self.user_info = User_Info_Function if User_Info_Function is not None else logging.info
        self.user_notification = User_Notification_Function if User_Notification_Function is not None else logging.info
        self.user_error = User_Error_Function if User_Error_Function is not None else logging.error
        self.default = Default_Function if Default_Function is not None else print