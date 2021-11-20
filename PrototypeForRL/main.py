import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import DirModifiedEvent, FileModifiedEvent, FileSystemEventHandler
from tensorforce import Agent, Environment

from SPSEnvironemnt import SPSEnvironmnet
from DataExchanger import DataExchanger
from globalConstants import  COMMAND_RESET, COMMAND_SETUP_DONE, DEBUG_EPISDOE, DEBUG_FILECREATION, DEBUG_STATES, EVENT_MESSAGE, EXTENSION_LOG, LOGFILE, MYPATH, EVENT_CONFIG,EVENT_REWARD,EVENT_COMMAND, \
    EVENT_STATE,EXTENSION_XML,EXTENSION_TEMP, debug_print
class FileHandler(FileSystemEventHandler):
    
    def __init__(self,de):
        super().__init__()
        self.dataEx = de

    def on_created(self, event):
        debug_print(event.src_path, DEBUG_FILECREATION)
        if   event.src_path == (MYPATH + EVENT_STATE + EXTENSION_XML):
            self.dataEx.read_file(EVENT_STATE)
        elif event.src_path == (MYPATH + EVENT_REWARD + EXTENSION_XML):
            self.dataEx.read_file(EVENT_REWARD)
        #elif event.src_path == (MYPATH + EVENT_CONFIG + EXTENSION_XML):
        #    self.dataEx.read_file(EVENT_CONFIG)
        #    os.remove(MYPATH + EVENT_CONFIG + EXTENSION_XML)
        elif not (event.src_path == MYPATH + EVENT_CONFIG + EXTENSION_TEMP or event.src_path == MYPATH + EVENT_STATE + EXTENSION_TEMP \
            or event.src_path == MYPATH + EVENT_COMMAND + EXTENSION_TEMP or event.src_path == MYPATH + EVENT_REWARD + EXTENSION_TEMP or \
                event.src_path == MYPATH + EVENT_COMMAND + EXTENSION_XML or event.src_path == MYPATH + EVENT_CONFIG + EXTENSION_XML or \
                event.src_path == MYPATH + EVENT_MESSAGE + EXTENSION_XML or event.src_path == MYPATH + EVENT_MESSAGE + EXTENSION_TEMP):
            raise ValueError("Unknown file type created, no event exists to handle this file")

if __name__ ==  "__main__":
    #clean up old files 
    all_events = [EVENT_COMMAND,EVENT_REWARD,EVENT_STATE, EVENT_MESSAGE]
    all_extensions = [EXTENSION_XML,EXTENSION_TEMP]
    for file in all_events:
        for extension in all_extensions:
            try:    
                os.remove(MYPATH + file + extension)
            except: 
                pass
    try:
        os.remove(MYPATH + LOGFILE + EXTENSION_LOG)
    except:
        pass
    logging.basicConfig(filename=MYPATH + LOGFILE + EXTENSION_LOG, encoding='utf-8', level=logging.DEBUG)

    
    print("Creating environment...")
    env = Environment.create(environment=SPSEnvironmnet())
    print("...done")

    #setup file handler to trigger on creation of file
    event_handler = FileHandler(env.dataEx)
    observer = Observer()
    observer.schedule(event_handler,  path=MYPATH,  recursive=False)
    observer.start()

    env.dataEx.read_file(EVENT_CONFIG)
    env.dataEx.define_action_space() #create action space based on workplan from config
    
    print("Creating agent...")
    #agent = Agent.create(agent=Agent.TensorforceAgent(), environment=env)
    #agent = Agent.create(agent="ppo", environment=env, batch_size = 10 )
    agent = Agent.create(agent="ppo", environment=env, batch_size = 1)
    print("...done")

    env.dataEx.write_command(commandtype=COMMAND_SETUP_DONE)
    

    num_updates = 0

    for episode in range(2):
        states = env.reset() 
        while not env.dataEx.received_state: #wait to receive first state
            pass
        env.dataEx.received_state = False
    
        debug_print(env.dataEx.state, DEBUG_STATES)
        sum_rewards = 0.0
        terminal = False
        step = 0
        while not terminal:
            actionID = agent.act(states=states)
            action = env.dataEx.actions[actionID[0]] 
            states, terminal, reward = env.execute(actions=action)
            step += 1
            #debug_print(env.dataEx.state, DEBUG_STATES)
            num_updates += agent.observe(terminal=terminal, reward=reward)
            sum_rewards += reward
        debug_print("Episode "+ str(episode) + ": return="+ str(sum_rewards) + " updates="+ str(num_updates) +" steps="+ str(step) + ": " + str(terminal) + "\n ------------------------", DEBUG_EPISDOE)
        print('Episode {}: return={} updates={}, steps={}'.format(episode, sum_rewards, num_updates,step))
        print("-------------------------------")
        env.dataEx.write_command(commandtype=COMMAND_RESET) #reset SPS
        
    #print('Mean evaluation return:', sum_rewards / amzahlEpisoden)

    # Close agent and env
    agent.close()
    env.close()

