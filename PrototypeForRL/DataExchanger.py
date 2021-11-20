import xml.etree.ElementTree as ET
from xml.dom import minidom
import json
import os

from globalConstants import ACTIONTYPE_MOVE, ACTIONTYPE_RESET, DEBUG_ACTIONS, DEBUG_FILECREATION, DEBUG_VALID_ACTION, EVENT_MESSAGE, ID_CURRENTID, ID_PROCTIME, ID_TERMINAL, ID_THROUGHPUTPERHOUR, MSG_SETUP_DONE, MYPATH, EVENT_CONFIG,EVENT_REWARD, \
EVENT_ACTION,EVENT_STATE, EXTENSION_XML,EXTENSION_TEMP, ID_OCCUPIED, \
ID_PARTTYPE, ID_REMAININGPROCTIME, NODE_IDENTIFIER, NONE, PARTA, PARTB, debug_print

class DataExchanger:
    def __init__(self):
        self.workplan = dict() #{Parttype:{ProcessingStep:{{machine_src: {{machine_dest:totalproctime}}}}} 
        #latter extend with total processing type to see performance consequences for RL
        self.state = dict() #{Machine}:{Occupation:true|false, RemainingProcTime:float,PartType:string}}, does not include the source! -> removed to hald state space.. + not in map to key
        self.actions = dict() #{{Parttype:{src:dest}}..}
        self.rewardProperties = dict() #e.g.  {"througput":10, ... } 
        self.received_state = False
        self.received_reward = False
        self.machines = list()
        self.totalMachine = 0
        self.terminal = False 
        self.current_state_id = -1

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
        tree = ET.parse( MYPATH + event + EXTENSION_XML)
        root = tree.getroot()

        if event == EVENT_CONFIG:
            self.read_config(root)
        elif event == EVENT_STATE:
            self.read_state(root)
            self.received_state = True
        elif event == EVENT_REWARD:
            self.read_reward(root)
            self.received_reward = True
        os.remove(MYPATH + event + EXTENSION_XML)

    def read_state(self, root):
        self.state = {}
        for state in root:
            for component in state:
                if component == NODE_IDENTIFIER:
                    for item in component:
                        if item == ID_CURRENTID:
                            self.current_state_id = int(item)
                else:
                #print(machine.tag)
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
                            try:
                                float(property.text)
                            except:
                                raise ValueError("Incorrect datatype for ID_REMAININGPROCTIME")
                            machine_properties.update({ID_REMAININGPROCTIME:float(property.text)})
                        else:
                            raise ValueError("Unknown property type")
                        self.state.update({component.tag:machine_properties})
                        #print(json.dumps(self.state, sort_keys=False, indent=4))
            

    def read_reward(self,root):
        for metric in root: 
            if metric.tag == ID_THROUGHPUTPERHOUR:
                self.rewardProperties.update({ID_THROUGHPUTPERHOUR:float(metric.text)})
            if metric.tag == ID_TERMINAL:
                if metric.text == "true":
                    self.terminal = True
                elif metric.text == "false":
                    self.terminal = False
                else:
                    raise ValueError("Unknown value for ID_TERMINAL")
            #add if for each property to make sure everything is written in order
            # if .. 

    def read_config(self,root):
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
                                try:
                                    property_val = float(property.text)
                                except:
                                    raise ValueError("Incorrect datatype for ID_PROCTIME")
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
            #debug_print({part.tag:procstep_dict})
            self.workplan.update({part.tag:procstep_dict})
            procstep_dict = {}
              
        #print(json.dumps(self.workplan[PARTB]["P3"], sort_keys=False, indent=4))
        #print(self.workplan)
        self.totalMachine = len(self.machines)
    def write_action(self, action, actiontype):
        '''
        Writes the action into an xml-formated file. 

        @input action: (parttype, source, destination)

        '''
        root = ET.Element("action")

        child_source = ET.SubElement(root,"actiontype")
        child_source.attrib = {"type": "string"}
        if actiontype == ACTIONTYPE_MOVE:
            child_source.text = ACTIONTYPE_MOVE
        elif actiontype == ACTIONTYPE_RESET:
            child_source.text = ACTIONTYPE_RESET
        else:
            raise ValueError("Encountered Unknown ACTIONTYPE")

        debug_print(actiontype, DEBUG_ACTIONS)
        child_source = ET.SubElement(root,"source")
        child_source.attrib = {"type": "string"}
        child_source.text = action[1]

        child_destination = ET.SubElement(root,"destination")
        child_destination.attrib = {"type": "string"}
        child_destination.text = action[2]

        child_parttype = ET.SubElement(root,"parttype")
        child_parttype.attrib = {"type": "string"}
        child_parttype.text = action[0]
        
        finishedText = self.format_output(root)
        if os.path.exists(MYPATH + EVENT_ACTION + EXTENSION_TEMP):
            os.remove(MYPATH + EVENT_ACTION + EXTENSION_TEMP)
            
        myFile = open(MYPATH + EVENT_ACTION + EXTENSION_TEMP, "w") #"a" = append
        myFile.write(finishedText)
        myFile.close()

        os.rename(MYPATH + EVENT_ACTION + EXTENSION_TEMP, MYPATH + EVENT_ACTION + EXTENSION_XML)
        if os.path.exists(MYPATH + EVENT_ACTION + EXTENSION_XML):
            debug_print(MYPATH + EVENT_ACTION + EXTENSION_XML, DEBUG_FILECREATION)

    def write_message(self):
        root = ET.Element("message")

        child_msg = ET.SubElement(root,"messagetype")
        child_msg.attrib = {"type": "string"}
        child_msg.text = MSG_SETUP_DONE
        
        finishedText = self.format_output(root)
        if os.path.exists(MYPATH + EVENT_MESSAGE + EXTENSION_TEMP):
            os.remove(MYPATH + EVENT_MESSAGE + EXTENSION_TEMP)
            
        myFile = open(MYPATH + EVENT_MESSAGE + EXTENSION_TEMP, "w") #"a" = append
        myFile.write(finishedText)
        myFile.close()

        os.rename(MYPATH + EVENT_MESSAGE + EXTENSION_TEMP, MYPATH + EVENT_MESSAGE + EXTENSION_XML)
        if os.path.exists(MYPATH + EVENT_MESSAGE + EXTENSION_XML):
            debug_print(MYPATH + EVENT_MESSAGE + EXTENSION_XML, DEBUG_FILECREATION)


        
    def define_action_space(self): #TODO call after config file read
        '''
        Creates a set of all possible actions. The actions are not necessarily valid at every time step

        @precondition: the config file must have been read to create the workplan
        '''
        if self.workplan == {}:
            raise RuntimeError("Cannot define action space, workplan has not been initialized yet")

        i = 0
        for parttype in self.workplan:
            for processingstep in self.workplan[parttype]:
                for source in self.workplan[parttype][processingstep]:
                    for dest in self.workplan[parttype][processingstep][source]: 
                        self.actions.update({i:(parttype,source,dest)})
                        i += 1

    def calculate_reward(self, isValid):
        if not isValid:
            return -1
        else:
            return self.rewardProperties[ID_THROUGHPUTPERHOUR] +1 #+1 just for now, because in the beginning itis 0 for a while
        #add benefits etc later #TODO
    
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
            rough_string = ET.tostring(text, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            return reparsed.toprettyxml(indent="  ")
