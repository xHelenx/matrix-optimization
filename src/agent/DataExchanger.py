from logging import DEBUG
from typing import Text
import xml.etree.ElementTree as ET
from xml.dom import minidom
import json
import os
from datetime import datetime
from time import sleep
import re


from globalConstants import COMMAND_ACTION_MOVE, COMMAND_EXPERIMENT_DONE, COMMAND_RESET, COMMAND_SETUP_DONE, COMMAND_TRAINING_DONE, EVENT_INFO, EXPERIMENT, ID_ACTION_TYPE, ID_AGENT, ID_AGENT_TYPE, ID_BATCH_SIZE, ID_CURRENTID, ID_DISCOUNT_FACTOR, ID_EPISODES, ID_EXPLORATION_RATE, ID_FOLDERNAME, ID_LEARNING_RATE, ID_PROCTIME, ID_REWARD_TYPE, ID_TERMINAL, ID_THROUGHPUTPERHOUR, ID_TOTALTIME, EVENT_CONFIG,EVENT_REWARD, \
EVENT_COMMAND,EVENT_STATE, EXTENSION_XML,EXTENSION_TEMP, ID_OCCUPIED, \
ID_PARTTYPE, ID_REMAININGPROCTIME, NODE_IDENTIFIER, NONE, PARTA, PARTB, debug_print, SLEEP_TIME, ID_ANALYSIS_TYPE
from dynamicConfigurations import  DEBUG_COMMAND, DEBUG_CURRENT_EXPERIMENT, DEBUG_FILECREATION, DEBUG_VALID_ACTION, DEBUG_WARNING, EXPERIMENT_PATH, FILE_PATH

class DataExchanger:
    def __init__(self):
        '''
        workplan            -  includes the processing steps per item type in the following format: {Parttype:{ProcessingStep:{{machine_src: {{machine_dest:totalproctime}}}}} 
        state               -  holds the last transmited state of the simulation
        action              -  dict of all possible actions in this simulation setup, format: {{Parttype:{src:dest}}..}
                                - possible action = theoretically senseful information due to the workplan, 
                                - valid action = applicable action in the current state
        rewardProperties    - dict of statistic values to calculate the reward
        received_*          - boolean indicating whether the specified file was received
        machines            - list of all machines (drains excluded)
        totalMachine        - number indicating the amount of machines
        terminal            - boolean indicating the end of an episode 
        
        ##--- 
        discount_factor     - 
        learning_rate       -
        episode             -
        max_timesteps       -
        exploration_rate    -
        batch_size          -   
        reward_type         - 
        action_type         -
        agent_type          -
        agent_type          -
        '''
        self.workplan = dict() #{Parttype:{ProcessingStep:{{machine_src: {{machine_dest:totalproctime}}}}} 
        self.state = dict() #{Machine}:{Occupation:true|false, RemainingProcTime:float,PartType:string}}
        self.actions = dict() #{{Parttype:{src:dest}}..}
        self.rewardProperties = dict() #e.g.  {"througput":10, ... } 
        self.received_state = False
        self.received_reward = False
        self.received_info = False
        self.machines = list()
        self.totalMachine = 0
        self.terminal = False
        self.totalTimeThisEpisode = -1 

        self.validActionsCounter = 0
        
        ##---- experiment configurations
        self.discount_factor   = -1
        self.learning_rate = -1
        self.episodes   = -1
        self.max_timesteps = -1
        self.exploration_rate  = -1
        self.batch_size    = -1
        self.reward_type    = -1
        self.action_type    = -1
        self.agent_type = -1
        self.agent_type = ""
        self.foldername = ""
        self.analysis_type = ""
        

        ##---- result values to log
        self.returns = [] 
        self.totalSteps = [] 
        self.validActions = [] 
        self.totalTime = []

        self.returnsEvaluation = [] 
        self.totalStepsEvaluation = [] 
        self.validActionsEvaluation = [] 
        self.totalTimeEvaluation = []

        self.allResultsToLog = [self.returns, self.totalSteps, self.validActions, self.totalTime, self.returnsEvaluation, self.totalStepsEvaluation, self.validActionsEvaluation, self.totalTimeEvaluation]
        self.namesofResults  = ["returns", "totalSteps", "validActions", "totalTime", "returnsEvaluation", "totalStepsEvaluation", "validActionsEvaluation", "totalTimeEvaluation"]
        


        
    def map_state_to_key(self):
        '''
        The state space of the RL comprises of all possible combinations of the occupation of each machine. 
        For example:
        state0: key: 0: M1 - False, M2 - False
        state1: key: 1: M1 - False, M2 - True 

        The key represents the current combination of occupation and is used for the agent as id for mapping the occupations to a single integer.
        @input: %
        @output: the key for the current state
        
        @preconditions: state exists
        '''
        if self.state == {}:
            raise RuntimeError("Cannot define action space, state has not been initialized yet")
        key = 0 #if machines would get really big -> maybe test for overflow?, for this use case ok
        for machine in self.machines:
            bitset = 0
            if  self.state[machine][ID_OCCUPIED]:
                bitset = 1
            key = (key << 1) + (bitset)
        return key

    def read_file(self, event):
        '''
        Wraps the individual file reading methods. This method encapsulate how to react to each incoming file

        @input: event - is the file name 
        @output: - 

        @preconditions: file with event name exists
        @postconditions: information of the file are stored in the data exchanger and are ready for use
        '''

        #make sure file is not in use
        is_readable = False
        while not is_readable:
                try:
                    tree = ET.parse( FILE_PATH + event + EXTENSION_XML)
                    root = tree.getroot()
                    is_readable = True
                except:
                    debug_print("WARNING:File is in use, cannot open file", DEBUG_WARNING)
                    sleep(SLEEP_TIME)

        #EVENT_CONFIG
        if event == EVENT_CONFIG:
            self.read_config(root)
            self.delete_file(event)
            while os.path.exists(FILE_PATH + event + EXTENSION_XML):
                pass

        #EVENT_STATE
        elif event == EVENT_STATE:
            self.read_state(root)
            self.delete_file(event)
            while os.path.exists(FILE_PATH + event + EXTENSION_XML):
                pass
            self.received_state = True

        #EVENT_REWARD
        elif event == EVENT_REWARD:
            self.read_reward(root)
            self.delete_file(event)
            while os.path.exists(FILE_PATH + event + EXTENSION_XML):
                pass
            self.received_reward = True
        
        #EVENT_INFO
        elif event == EVENT_INFO:
            self.delete_file(event)
            while os.path.exists(FILE_PATH + event + EXTENSION_XML):
                pass
            self.received_info = True
        
        
    def delete_file(self, event):
        '''
        helper function to delete a file when it is not in use anymore

        @input event - file name
        @output %
        @precondition - file exists
        @postcondition - file does not exist
        '''
        is_deletable = False
        while not is_deletable:
            try:
                os.remove(FILE_PATH + event + EXTENSION_XML)
                is_deletable = True
            except:
                debug_print("File is in use, cannot delete file", DEBUG_FILECREATION)
                sleep(SLEEP_TIME)

    def read_state(self, root):
        '''
        reads the state and stores it for later use
        @input - root the root of the xml file to read
        @output - %
        @preconditions - %
        @postconditions - %
        '''
        self.state = {}
        for state in root:
            for component in state:
                if component.tag == NODE_IDENTIFIER:
                    self.current_state_id = int(component.text)
                else:
                    machine_properties = {}
                    for property in component:
                        if property.tag == ID_OCCUPIED:
                            if property.text == "true":
                                machine_properties.update({ID_OCCUPIED:True})
                            elif property.text == "false":
                                machine_properties.update({ID_OCCUPIED:False})
                            else:
                                raise ValueError("Unknown value for ID_OCCUPIED")
                        elif property.tag == ID_PARTTYPE:
                            if property.text == NONE:
                                machine_properties.update({ID_PARTTYPE:None})
                            elif property.text == PARTA or property.text == PARTB:
                                machine_properties.update({ID_PARTTYPE:property.text})
                            else:
                                raise ValueError("Unknown value for ID_PARTTYPE")
                        elif property.tag == ID_REMAININGPROCTIME:
                            if property.text == "-1": 
                                property.text = "0"
                            machine_properties.update({ID_REMAININGPROCTIME:int(float(property.text))})
                        else:
                            raise ValueError("Unknown property type")
                        self.state.update({component.tag:machine_properties})
                        #print(json.dumps(self.state, sort_keys=False, indent=4))
            

    def read_reward(self,root):
        '''
        reads the reward file and stores the reward properties for later use

        @input - root the root of the xml file to read
        @output - %
        @preconditions - %
        @postconditions - %
        '''
        for metric in root: 
            if metric.tag == ID_THROUGHPUTPERHOUR:
                self.rewardProperties.update({ID_THROUGHPUTPERHOUR:float(metric.text)})
            if metric.tag == ID_TOTALTIME:   
                self.totalTimeThisEpisode = int(float(metric.text))
            if metric.tag == ID_TERMINAL:
                if metric.text == "true":
                    self.terminal = True
                elif metric.text == "false":
                    self.terminal = False
                else:
                    raise ValueError("Unknown value for ID_TERMINAL")
            #add if for each property to make sure everything is written in order
            #if metric.tag == ID_NEW .. 

    def read_config(self,root):
        '''
        
        reads the config file and stores the work plan for later use

        @input - root the root of the xml file to read
        @output - %
        @preconditions - %
        @postconditions - %
        '''
        #{PartA: {{1:{M1:{M2:10}}}}}
        property_val = -1
        dest_dict = {}
        src_dict = {}
        procstep_dict = {}

        self.machines = []
        for part in root:
            for procstep in part:
                for src in procstep:
                    for dest in src:
                        for property in dest:
                            if property.tag == ID_PROCTIME:
                                property_val = int(float(property.text))
                        dest_dict.update({dest.tag:property_val})
                        if not dest.tag in self.machines:
                            self.machines.append(dest.tag) 
                        property_val = -1
                    src_dict.update({src.tag:dest_dict})
                    #if not src.tag in self.machines:
                    #        self.machines.append(src.tag) 
                    dest_dict = {}
                procstep_dict.update({procstep.tag:src_dict})
                src_dict = {}
            self.workplan.update({part.tag:procstep_dict})
            procstep_dict = {}
              
        #print(json.dumps(self.workplan[PARTB]["P3"], sort_keys=False, indent=4))
        #print(self.workplan)
        self.totalMachine = len(self.machines)
    def write_command(self, commandtype, action=(None,None,None)):
        '''
        Writes a command into an xml-formated file. 

        @input action: (parttype, source, destination)
        @input commandtype:
                    - COMMAND_ACTION_MOVE: a move action, as defined in the action shall be performed
                    - COMMAND_SETUP_DONE: simulation can start the episode now
                    - COMMAND_TRAINING_DONE: the entire tranining is done, stop simulation
        '''
        #writing the file
        root = ET.Element("command")
        child_command = ET.SubElement(root,"commandtype")
        child_command.attrib = {"type": "string"}
        
        if commandtype == COMMAND_SETUP_DONE:
            child_command.text = COMMAND_SETUP_DONE
        elif commandtype == COMMAND_TRAINING_DONE:
            child_command.text = COMMAND_TRAINING_DONE
        elif commandtype == COMMAND_EXPERIMENT_DONE:
            child_command.text = COMMAND_EXPERIMENT_DONE
        elif commandtype == COMMAND_ACTION_MOVE:
            child_command.text = COMMAND_ACTION_MOVE
            child_source = ET.SubElement(root,"source")
            child_source.attrib = {"type": "string"}
            child_source.text = action[1]

            child_destination = ET.SubElement(root,"destination")
            child_destination.attrib = {"type": "string"}
            child_destination.text = action[2]

            child_parttype = ET.SubElement(root,"parttype")
            child_parttype.attrib = {"type": "string"}
            child_parttype.text = action[0]
        else:
            raise ValueError("Command type does not exist")
            
        debug_print(commandtype, DEBUG_COMMAND)
        
        #write string to .temp file and rename it to ensure that the file 
        #is complete before the simulation starts reading
        finishedText = self.format_output(root)
        if os.path.exists(FILE_PATH + EVENT_COMMAND + EXTENSION_TEMP):
            os.remove(FILE_PATH + EVENT_COMMAND + EXTENSION_TEMP)
            
        myFile = open(FILE_PATH + EVENT_COMMAND + EXTENSION_TEMP, "w") #"a" = append
        myFile.write(finishedText)
        myFile.close()

        while os.path.exists(FILE_PATH + EVENT_COMMAND + EXTENSION_XML):
            pass
        
        os.rename(FILE_PATH + EVENT_COMMAND + EXTENSION_TEMP, FILE_PATH + EVENT_COMMAND + EXTENSION_XML)
        if os.path.exists(FILE_PATH + EVENT_COMMAND + EXTENSION_XML):
            debug_print(FILE_PATH + EVENT_COMMAND + EXTENSION_XML, DEBUG_FILECREATION)

        
    def define_action_space(self): 
        '''
        Creates a set of all possible actions. The actions are not necessarily valid at every time step
        @input : %
        @output: %
        @preconditions: the config file must have been read to create the workplan
        @postconditions: %
        '''
        if self.workplan == {}:
            raise RuntimeError("Cannot define action space, workplan has not been initialized yet")

        i = 0
        for parttype in self.workplan:
            for processingstep in self.workplan[parttype]:
                for source in self.workplan[parttype][processingstep]:
                    for dest in self.workplan[parttype][processingstep][source]: 
                        self.actions.update({i:(parttype,source,dest)}) #add possible action to action space
                        i += 1

    def calculate_reward(self, action): #TODO: add switch for different reward functions
        '''
        calculates the reward for the chosen action

        @input isValid - bool is action is valid
        @output reward - numerical value indicating how good the action was
        @precondition  - action was performed
        @postcondition - %
        '''
        isValid = self.is_valid_action(action)
        isMovedToDrain = self.moved_to_drain(action)
        if self.reward_type == "mayer":   
            reward = 0 
            if not isValid:
                return -5       #punish invalid action
            elif isMovedToDrain:
                reward += 20    #reward finishing product
            return int(reward + self.totalTimeThisEpisode/100) #stress agent to finish fast, by using current running time as punishment
        elif self.reward_type == "simple":
            if not isValid:
                return -1
            else:
                return int(10*self.rewardProperties[ID_THROUGHPUTPERHOUR] + 20) #+1 just for now, because in the beginning itis 0 for a while
    def moved_to_drain(self,action):
        #parttype = 0
        #source = 1
        destination = 2
        if "Drain" in action[destination]:
            return True
        else:
            return False 

    def is_valid_action(self,action):
        '''
        An action is valid, if 
            - the source from which an part shall be moved is occupied 
            - the source contains a part, that matches the partype of the action
            - the destination is not occupied
            - the action is a defined action as per workplan

        An action is also valid, the source contains a part, that has not finished its process yet. Then the system waits till the remaining time is equal to 0 and then
        performs the action

        @input: action, consisting of a triple: {(parttype, source, destination)}
        @output: boolean, if action is valid

        @precondition: the current state of the system
        @precondition: workplan is defined, (=config file has been read)
        '''
        if self.workplan == {}:
            raise RuntimeError("Cannot define action space, workplan has not been initialized yet")

        if self.state == {}:
            raise RuntimeError("Cannot define action space, state has not been initialized yet")

        #state = {Machine}:{Occupation, RemainingProcTime,PartType}}
        #workplan = {Parttype:{ProcessingStep:{{machine_src: {{machine_dest:totalproctime}}}}} 
        parttype = 0
        source = 1
        destination = 2

        is_in_workplan = False
        for procStep in self.workplan[action[parttype]]:
            if action[source] in self.workplan[action[parttype]][procStep]:
                if action[destination] in self.workplan[action[parttype]][procStep][action[source]]:
                    is_in_workplan = True
        
        #1. matching part types, includes if none does resolve to false AND 2. destination is not occupied AND 3.action is defined as per workplan
        is_valid = (action[parttype] == self.state[action[source]][ID_PARTTYPE]) and not self.state[action[destination]][ID_OCCUPIED] and is_in_workplan
        
        return is_valid
        
    def format_xml(self,file):
        ''' 
        Shows the content of the XML file. This function is used for debug purposes
        Input: file - the xml-file, that should be read
        Output: string, containing the content of "file" 
        '''
        tree = ET.parse(file)
        root = tree.getroot()
        rough_string = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    def format_output(self,text):
        '''
        Formats a given text to be easier to read
        '''
        rough_string = ET.tostring(text, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    def load_experiment(self,experimentID):
        tree = ET.parse( EXPERIMENT_PATH + EXPERIMENT + EXTENSION_XML)
        root = tree.getroot()
        
        for numberofExperiment in root: #id of experiment
            if int(numberofExperiment.text) == experimentID:
                for configtype in numberofExperiment: #agent, simulation..
                    if configtype.tag == ID_AGENT: 
                        for parameter in configtype: #learningrate, discount_factor .. 
                            if parameter.tag == ID_DISCOUNT_FACTOR:
                                self.discount_factor = float(parameter.text)
                            elif parameter.tag == ID_LEARNING_RATE:
                                self.learning_rate = float(parameter.text)
                            elif parameter.tag == ID_EPISODES:
                                self.episodes = int(parameter.text)
                            elif parameter.tag == ID_EXPLORATION_RATE:
                                self.exploration_rate = float(parameter.text)
                            elif parameter.tag == ID_BATCH_SIZE:
                                self.batch_size = int(parameter.text)
                            elif parameter.tag == ID_ACTION_TYPE:
                                self.action_type = int(parameter.text)
                            elif parameter.tag == ID_REWARD_TYPE:
                                self.reward_type = parameter.text
                            elif parameter.tag == ID_AGENT_TYPE:
                                self.agent_type = parameter.text
                            elif parameter.tag == ID_FOLDERNAME: 
                                self.foldername = parameter.text
                            elif parameter.tag == ID_ANALYSIS_TYPE:
                                self.analysis_type = parameter.text
        debug_print("ID "+ str(experimentID) + ": " + str(self.discount_factor)+str(self.learning_rate)+str(self.episodes)+str(self.exploration_rate)+str(self.batch_size)+str(self.action_type)+str(self.reward_type)+str(self.agent_type), DEBUG_CURRENT_EXPERIMENT)

    def save_results(self):
        
        #writing the file
        text = ""
        for loglist,name  in zip(self.allResultsToLog,self.namesofResults):
            if not loglist == []:
                text += name + "=" + str(loglist) + "\n"

        if self.analysis_type == "training":  
            myFile = open(EXPERIMENT_PATH + self.foldername + "//resultsTrain.txt", "w") #"a" = append
        elif self.analysis_type == "evaluation":
            myFile = open(EXPERIMENT_PATH + self.foldername + "//resultsEval.txt", "w") #"a" = append
        myFile.write(text)
        myFile.close()
