import os
import sys
from time import sleep
import signal
import logging
from watchdog.observers import Observer
from watchdog.events import DirModifiedEvent, FileModifiedEvent, FileSystemEventHandler
from tensorforce import Agent, Environment

from SPSEnvironemnt import SPSEnvironmnet
from DataExchanger import DataExchanger
from globalConstants import  COMMAND_SETUP_DONE, COMMAND_TRAINING_DONE, DEBUG_EPISDOE, DEBUG_FILECREATION, DEBUG_STATES, EXPERIMENT_PATH, EXTENSION_LOG, LOGFILE, PATH, EVENT_CONFIG,EVENT_REWARD,EVENT_COMMAND, \
    EVENT_STATE,EXTENSION_XML,EXTENSION_TEMP, debug_print, SLEEP_TIME

class FileHandler(FileSystemEventHandler):
    
    def __init__(self,de):
        super().__init__()
        self.dataEx = de

    def on_created(self, event):
        '''
            When a file is created in the defined directory, the triggered event is handled
            @input event - file name 
            @output - %
            @precondition - observer is installed
            @postcondition - %
        '''
        debug_print(event.src_path, DEBUG_FILECREATION)
        if   event.src_path == (PATH + EVENT_STATE + EXTENSION_XML):
            self.dataEx.read_file(EVENT_STATE)
        elif event.src_path == (PATH + EVENT_REWARD + EXTENSION_XML):
            self.dataEx.read_file(EVENT_REWARD)
        elif not (event.src_path == PATH + EVENT_CONFIG + EXTENSION_TEMP or event.src_path == PATH + EVENT_STATE + EXTENSION_TEMP \
            or event.src_path == PATH + EVENT_COMMAND + EXTENSION_TEMP or event.src_path == PATH + EVENT_REWARD + EXTENSION_TEMP or \
                event.src_path == PATH + EVENT_COMMAND + EXTENSION_XML or event.src_path == PATH + EVENT_CONFIG + EXTENSION_XML):
            raise ValueError("Unknown file type created, no event exists to handle this file")

def signal_handler(signal, frame):
    '''
    Sends a termination information to the simulation, if the program was shut down with Ctrl+C
    '''

    print('Process killed with Ctrl+C, stopping simulation')
    de = DataExchanger()
    de.write_command(commandtype=COMMAND_TRAINING_DONE) 
    sys.exit(0)

if __name__ ==  "__main__":
    signal.signal(signal.SIGINT, signal_handler) #setup signal handler for Ctrl+C
    #clean up old files 
    all_events = [EVENT_COMMAND,EVENT_REWARD,EVENT_STATE]
    all_extensions = [EXTENSION_XML,EXTENSION_TEMP]
    for file in all_events:
        for extension in all_extensions:
            try:    
                os.remove(PATH + file + extension)
            except: 
                pass
    try:
        os.remove(PATH + LOGFILE + EXTENSION_LOG)
    except:
        pass

    #set up logging file
    logging.basicConfig(filename=PATH + LOGFILE + EXTENSION_LOG, encoding='utf-8', level=logging.DEBUG)
    debug_print(PATH,DEBUG_FILECREATION)
    
    print("Creating environment...")
    env = Environment.create(environment=SPSEnvironmnet())
    print("...done")

    #load current experiment configurations
    env.dataEx.load_experiment(int(sys.argv[1]))

    #setup file handler to trigger on creation of file
    event_handler = FileHandler(env.dataEx)
    observer = Observer()
    observer.schedule(event_handler,  path=PATH,  recursive=False)
    observer.start()
    env.dataEx.read_file(EVENT_CONFIG)
    env.dataEx.define_action_space() #create action space based on workplan from config
    
    print("Creating agent...")
    agent = Agent.create(agent=env.dataEx.agent_type, \
                        environment = env, \
                        batch_size = env.dataEx.batch_size,  exploration = env.dataEx.exploration_rate,
                        learning_rate = env.dataEx.learning_rate, discount = env.dataEx.discount_factor)
    print("...done")
    num_updates = 0

    print(env.dataEx.foldername)
    #training loop
    for episode in range(10): #env.dataEx.episodes):
        env.dataEx.write_command(commandtype=COMMAND_SETUP_DONE)
        states = env.reset() 
        while not env.dataEx.received_state: #wait to receive first state
            sleep(SLEEP_TIME)
        env.dataEx.received_state = False
        debug_print(env.dataEx.state, DEBUG_STATES)
        sum_rewards = 0.0
        terminal = False
        step = 0
        env.dataEx.validActionsCounter = 0
        while not terminal:
            actionID = agent.act(states=states)
            action = env.dataEx.actions[actionID[0]] 
            states, terminal, reward = env.execute(actions=action)
            step += 1
            #debug_print(env.dataEx.state, DEBUG_STATES)
            num_updates += agent.observe(terminal=terminal, reward=reward)
            sum_rewards += reward
        env.dataEx.returns.append(sum_rewards)
        env.dataEx.totalSteps.append(step)
        env.dataEx.validActions.append(env.dataEx.validActionsCounter)
        env.dataEx.totalTime.append(env.dataEx.totalTimeThisEpisode)
        debug_print("Episode "+ str(episode) + ": return="+ str(sum_rewards) + " updates="+ str(num_updates) +" steps="+ str(step) + ": " + str(terminal) + "\n ------------------------", DEBUG_EPISDOE)
        print('Episode {}: return={} updates={}, steps={}'.format(episode, sum_rewards, num_updates,step))
        print("-------------------------------")
    
    env.dataEx.write_command(commandtype=COMMAND_TRAINING_DONE) 
    env.dataEx.save_results()
    agent.save(EXPERIMENT_PATH + env.dataEx.foldername, filename="agent")
    #safe model

    #TODO: evaluation of agent, save model
    agent.close()
    env.close()

