import logging
# set print debug messages
DEBUG_FILECREATION = True
DEBUG_ACTIONS = True
DEBUG_STATES = True
DEBUG_EPISDOE = True
DEBUG_VALID_ACTION = True 
#---Message types
MSG_SETUP_DONE = "setupdone"


#--- File constants
MYPATH = r"E:\\Bachelorarbeit\\src\\simulation\\"
EVENT_STATE = "state"
EVENT_ACTION = "action"
EVENT_REWARD = "reward"
EVENT_CONFIG = "config"
EVENT_MESSAGE = "message"
LOGFILE = "logfile"
EXTENSION_XML = ".xml"
EXTENSION_TEMP = ".temp"
EXTENSION_LOG = ".log"
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
ID_THROUGHPUTPERHOUR = "throughputperhour"
ID_TERMINAL = "terminal"
ID_CURRENTID = "currentId"

NODE_IDENTIFIER = "id"

ACTIONTYPE_RESET = "reset"
ACTIONTYPE_MOVE = "move"


def debug_print(message, type):
    '''
    debug_print prints a message, if IF_DEBUG is set to True. Otherwise the debug prints will
    not be shown on the terminal
    '''
    if type:
        logging.debug(message)