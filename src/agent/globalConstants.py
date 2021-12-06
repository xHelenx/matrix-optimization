import logging
import sys
#--- time between checking availability of file
SLEEP_TIME = 0.005

#--- set print debug messages
DEBUG_FILECREATION = True
DEBUG_COMMAND = True
DEBUG_STATES = False
DEBUG_EPISDOE = False
DEBUG_VALID_ACTION = False 
DEBUG_WARNING = False
DEBUG_CURRENT_EXPERIMENT = True

#--- command types
COMMAND_RESET = "reset"
COMMAND_ACTION_MOVE = "move"
COMMAND_SETUP_DONE = "done"
COMMAND_TRAINING_DONE = "training done"

#--- File constants
PATH =r"A:\\"  #sys.argv[1] #e.g #"A:/" #r"E:\\Bachelorarbeit\\src\\simulation\\" 
EXPERIMENT_PATH = r"E:\\Bachelorarbeit\\src\\experiments\\" 
EXPERIMENT = "experiment"


EVENT_STATE = "state"
EVENT_COMMAND = "command"
EVENT_REWARD = "reward"
EVENT_CONFIG = "config"
LOGFILE = "logfile"
EXTENSION_XML = ".xml"
EXTENSION_TEMP = ".temp"
EXTENSION_LOG = ".log"
EXPERIMENT = "experiment"

#--- XML-related constant identifiers
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
ID_TOTALTIME = "totalTime"
NODE_IDENTIFIER = "id"

##- Experiment file
ID_AGENT = "agent"
ID_DISCOUNT_FACTOR  = "discount_factor"
ID_LEARNING_RATE    = "learning_rate"
ID_EPISODES = "episodes"
ID_EXPLORATION_RATE = "exploration_rate"
ID_BATCH_SIZE   = "batch_size"
ID_REWARD_TYPE  = "reward_type"
ID_ACTION_TYPE  = "action_type"
ID_AGENT_TYPE   = "agent_type"
ID_FOLDERNAME   = "foldername"


def debug_print(message, type):
    '''
    debug_print prints a message, if IF_DEBUG is set to True. Otherwise the debug prints will
    not be shown on the terminal
    '''
    if type:
        logging.debug(message)

        