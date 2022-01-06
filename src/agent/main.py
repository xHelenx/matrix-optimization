import os
import sys
from time import sleep
import signal
import logging
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from tensorforce import Agent, Environment

from SPSEnvironemnt import SPSEnvironmnet
from DataExchanger import DataExchanger
from globalConstants import  COMMAND_EXPERIMENT_DONE, COMMAND_SETUP_DONE, COMMAND_TRAINING_DONE, EVENT_INFO,  EXTENSION_LOG, LOGFILE,  EVENT_CONFIG,EVENT_REWARD,EVENT_COMMAND, \
    EVENT_STATE,EXTENSION_XML,EXTENSION_TEMP, debug_print, SLEEP_TIME
from dynamicConfigurations import DEBUG_EPISODE, DEBUG_FILECREATION, DEBUG_STATES, EXPERIMENT_PATH, FILE_PATH

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
        if   event.src_path == (FILE_PATH + EVENT_STATE + EXTENSION_XML):
            self.dataEx.read_file(EVENT_STATE)
        elif event.src_path == (FILE_PATH + EVENT_REWARD + EXTENSION_XML):
            self.dataEx.read_file(EVENT_REWARD)
        elif event.src_path == (FILE_PATH + EVENT_INFO + EXTENSION_XML):
            self.dataEx.read_file(EVENT_INFO)
        elif not (event.src_path == FILE_PATH + EVENT_INFO + EXTENSION_TEMP or event.src_path == FILE_PATH + EVENT_CONFIG + EXTENSION_TEMP or event.src_path == FILE_PATH + EVENT_STATE + EXTENSION_TEMP \
            or event.src_path == FILE_PATH + EVENT_COMMAND + EXTENSION_TEMP or event.src_path == FILE_PATH + EVENT_REWARD + EXTENSION_TEMP or \
                event.src_path == FILE_PATH + EVENT_COMMAND + EXTENSION_XML or event.src_path == FILE_PATH + EVENT_CONFIG + EXTENSION_XML):
            raise ValueError("Unknown file type created, no event exists to handle this file")
        

def signal_handler(signal, frame):
    '''
    Sends a termination information to the simulation, if the program was shut down with Ctrl+C
    '''

    print('Process killed with Ctrl+C, stopping simulation')
    de = DataExchanger()
    de.write_command(commandtype=COMMAND_TRAINING_DONE) 
    #TODO close agent, env and observer here too?
    sys.exit(0)

if __name__ ==  "__main__":
    start_time = time.time()
    signal.signal(signal.SIGINT, signal_handler) #setup signal handler for Ctrl+C
    #clean up old files 
    all_events = [EVENT_COMMAND,EVENT_REWARD,EVENT_STATE]
    all_extensions = [EXTENSION_XML,EXTENSION_TEMP]
    for file in all_events:
        for extension in all_extensions:
            try:    
                os.remove(FILE_PATH + file + extension)
            except: 
                pass
    try:
        os.remove(FILE_PATH + LOGFILE + EXTENSION_LOG)
    except:
        pass

    #set up logging file
    logging.basicConfig(filename=FILE_PATH + LOGFILE + EXTENSION_LOG, encoding='utf-8', level=logging.DEBUG)
    debug_print(FILE_PATH,DEBUG_FILECREATION)
    
    print("Creating environment...")
    env = Environment.create(environment=SPSEnvironmnet(), max_episode_timesteps=25000)
    print("...done")

    #load current experiment configurations
    env.dataEx.load_experiment(int(sys.argv[1]))

    #setup file handler to trigger on creation of file
    event_handler = FileHandler(env.dataEx)
    observer = Observer()
    observer.schedule(event_handler,  path=FILE_PATH,  recursive=False)
    observer.start()
    env.dataEx.read_file(EVENT_CONFIG)
    env.dataEx.define_action_space() #create action space based on workplan from config
    

    if env.dataEx.analysis_type == "training":
        print("Creating agent...")
        if env.dataEx.agent_type == "ppo":
            agent = Agent.create(agent=env.dataEx.agent_type, \
                                environment = env, \
                                exploration = env.dataEx.exploration_rate, \
                                learning_rate = env.dataEx.learning_rate, discount = env.dataEx.discount_factor, batch_size = env.dataEx.batch_size,
                                saver=dict(directory=EXPERIMENT_PATH + env.dataEx.foldername, frequency=25, max_checkpoints=2))
        if env.dataEx.agent_type == "ddqn":
            agent = Agent.create(agent=env.dataEx.agent_type, \
                                environment = env, \
                                exploration = env.dataEx.exploration_rate, \
                                learning_rate = env.dataEx.learning_rate, discount = env.dataEx.discount_factor, batch_size = env.dataEx.batch_size,
                                saver=dict(directory=EXPERIMENT_PATH + env.dataEx.foldername, frequency=25, max_checkpoints=2))

        elif env.dataEx.agent_type == "random":
            agent = Agent.create(agent=env.dataEx.agent_type, \
                                environment = env,
                                saver=dict(directory=EXPERIMENT_PATH + env.dataEx.foldername, frequency=25, max_checkpoints=2))
        else:
            raise ValueError("Invalid agent type selected")
    elif env.dataEx.analysis_type == "evaluation":
        print("Loading trained agent...")
        agent = Agent.load(directory=EXPERIMENT_PATH + env.dataEx.foldername, format="checkpoint", environment=env)
    
    print("...done")

    num_updates = 0

    print(env.dataEx.foldername)

    if env.dataEx.analysis_type == "training":
        #training loop
        for episode in range(env.dataEx.episodes): #env.dataEx.episodes):
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
                debug_print(env.dataEx.state, DEBUG_STATES)
                num_updates += agent.observe(terminal=terminal, reward=reward)
                sum_rewards += reward
                if step >= env.max_episode_timesteps(): #if the limit of steps is reached stop episode 
                    break 
            env.dataEx.returns.append(sum_rewards)
            env.dataEx.totalSteps.append(step)
            env.dataEx.validActions.append(env.dataEx.validActionsCounter)
            env.dataEx.totalTime.append(env.dataEx.totalTimeThisEpisode)
            env.dataEx.save_results()
            debug_print("Episode "+ str(episode) + ": return="+ str(sum_rewards) + " updates="+ str(num_updates) +" steps="+ str(step) + ": " + str(terminal) + "\n ------------------------", DEBUG_EPISODE)
            print('Training: Episode {}: return={} updates={}, steps={}'.format(episode, sum_rewards, num_updates,step))
            print("-------------------------------")
            if len(env.dataEx.returns) >= 3:
                print(env.dataEx.returns[-1], env.dataEx.returns[-2], env.dataEx.returns[-3] )
            if len(env.dataEx.returns) >= 3 and (env.dataEx.returns[-1] == env.dataEx.returns[-2]) and (env.dataEx.returns[-2] == env.dataEx.returns[-3]):
                print("Early stopping, proceed with new episode")
                break
        print("\n")
        

    elif env.dataEx.analysis_type == "evaluation":
        # Evaluate 
        num_updates = 0
        
        print("Starting evaluation")
        
        for episode in range(env.dataEx.episodes):
            env.dataEx.write_command(commandtype=COMMAND_SETUP_DONE)
            states = env.reset() 
            while not env.dataEx.received_state: #wait to receive first state
                sleep(SLEEP_TIME)
            env.dataEx.received_state = False
            debug_print(env.dataEx.state, DEBUG_STATES)
            
            sum_rewards = 0.0
            step = 0
            env.dataEx.validActionsCounter = 0
            terminal = False
            internals = agent.initial_internals()
            while not terminal:
                actionID, internals = agent.act(states=states, independent=True, deterministic=False, internals=internals) #deterministic allows exploration etc, otherwise always chooses 
                #"best" action (if that one is not possible, we get stuck here)
                action = env.dataEx.actions[actionID[0]] 
                states, terminal, reward = env.execute(actions=action)
                step += 1
                sum_rewards += reward
            env.dataEx.returnsEvaluation.append(sum_rewards)
            env.dataEx.totalStepsEvaluation.append(step)
            env.dataEx.validActionsEvaluation.append(env.dataEx.validActionsCounter)
            env.dataEx.totalTimeEvaluation.append(env.dataEx.totalTimeThisEpisode)
            env.dataEx.save_results()
            
            print('Evaluation: Episode {}: return={} updates={}, steps={}'.format(episode, sum_rewards, num_updates,step))
            print("-------------------------------")
            debug_print("Episode "+ str(episode) + ": return="+ str(sum_rewards) + " updates="+ str(num_updates) +" steps="+ str(step) + ": " + str(terminal) + "\n ------------------------", DEBUG_EPISODE)
            
            if len(env.dataEx.returnsEvaluation) >= 3 and (env.dataEx.returnsEvaluation[-1] == env.dataEx.returnsEvaluation[-2]) and (env.dataEx.returnsEvaluation[-2] == env.dataEx.returnsEvaluation[-3]):
                break
        

    
    print("--- %s seconds ---" % (round(time.time() - start_time,2)))
    env.dataEx.write_command(commandtype=COMMAND_EXPERIMENT_DONE) 

    observer.stop()
    observer.join()
    agent.close()
    env.close()

    #if training and eval is done merge all results in one final file   
    if env.dataEx.analysis_type == "evaluation":
        dataTrain = dataEval = ""
        with open(EXPERIMENT_PATH + env.dataEx.foldername + "//resultsTrain.txt") as fp:
            dataTrain = fp.read()
    
        with open(EXPERIMENT_PATH + env.dataEx.foldername + "//resultsEval.txt") as fp:
            dataEval = fp.read()
    
        # Merging the files 
        dataTrain += dataEval
        
        with open (EXPERIMENT_PATH + env.dataEx.foldername + "//results.txt", 'w') as fp:
            fp.write(dataTrain)
        os.remove(EXPERIMENT_PATH + env.dataEx.foldername + "//resultsTrain.txt")
        os.remove(EXPERIMENT_PATH + env.dataEx.foldername + "//resultsEval.txt")
