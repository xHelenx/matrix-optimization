# set print debug messages
IS_DEBUG = True

#--- File constants
MYPATH = r"E:\\Bachelorarbeit\\PrototypeForRL\\"
EVENT_STATE = "state"
EVENT_ACTION = "action"
EVENT_REWARD = "reward"
EVENT_CONFIG = "config"
EXTENSION_XML = ".xml"
EXTENSION_TEMP = ".temp"
#---- XML-related constant identifiers
PARTA = "PartA"
PARTB = "PartB"
STRING = "string"
FLOAT = "float"
BOOLEAN = "boolean"
NONE = "None"

ID_OCCUPIED = "occupied"
ID_PARTTYPE = "parttype"
ID_REMAININGPROCTIME = "remainingproctime"
ID_PROCTIME = "procTime"


def debug_print(message):
    '''
    debug_print prints a message, if IF_DEBUG is set to True. Otherwise the debug prints will
    not be shown on the terminal
    '''
    if IS_DEBUG:
        print(message)