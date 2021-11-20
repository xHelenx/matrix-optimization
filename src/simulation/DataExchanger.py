import xml.etree.ElementTree as ET
from xml.dom import minidom
import json
import os

from globalConstants import ID_PROCTIME, MYPATH, EVENT_CONFIG,EVENT_REWARD, \
EVENT_ACTION,EVENT_STATE, EXTENSION_XML,EXTENSION_TEMP, ID_OCCUPIED, \
ID_PARTTYPE, ID_REMAININGPROCTIME, NONE, PARTA, PARTB, debug_print, \
received_config, received_state

class DataExchanger:
    def __init__(self):
        self.workplan = dict() #{Parttype:{ProcessingStep:{{machine_src: {{machine_dest:totalproctime}}}}} 
        #latter extend with total processing type to see performance consequences for RL
        self.state = dict() #{Machine}:{Occupation, RemainingProcTime,PartType}}
        self.actions = set() #{{Parttype:{src:dest}}..}
        self.reward = 0 #float 

    def is_valid_action(action):
        return False

    def read_file(self, event):
        debug_print(event + EXTENSION_XML)
        tree = ET.parse(event + EXTENSION_XML)
        root = tree.getroot()

        if event == EVENT_CONFIG:
            self.read_config(root)
        elif event == EVENT_STATE:
            self.read_state(root)
        #elif event == EVENT_ACTION:
        #    pass #TODO
        elif event == EVENT_REWARD:
            pass #TODO
        
    def read_state(self, root):
        for machine in root:
            #print(machine.tag)
            machine_properties = {}
            for property in machine:
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
                self.state.update({machine.tag:machine_properties})
                #print(json.dumps(self.state, sort_keys=False, indent=4))
        received_state

    def read_config(self,root):
        #{PartA: {{1:{M1:{M2:10}}}}}
        property_val = -1
        dest_dict = {}
        src_dict = {}
        procstep_dict = {}

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
                        property_val = -1
                    src_dict.update({src.tag:dest_dict})
                    dest_dict = {}
                procstep_dict.update({procstep.tag:src_dict})
                src_dict = {}
            #debug_print({part.tag:procstep_dict})
            self.workplan.update({part.tag:procstep_dict})
            procstep_dict = {}
              
        #print(json.dumps(self.workplan[PARTB]["P3"], sort_keys=False, indent=4))
        #print(self.workplan)
        received_config = True

    def write_action(self, action):
        '''
        Writes the action into an xml-formated file. 

        @input action: (parttype, source, destination)

        '''
        root = ET.Element("action")

        child_parttype = ET.SubElement(root,"parttype")
        child_parttype.attrib = {"type": "string"}
        child_parttype.text = action[0]
        
        child_source = ET.SubElement(root,"source")
        child_source.attrib = {"type": "string"}
        child_source.text = action[1]

        child_destination = ET.SubElement(root,"destination")
        child_destination.attrib = {"type": "string"}
        child_destination.text = action[2]

        finishedText = self.format_output(root)
        myFile = open(EVENT_ACTION + EXTENSION_TEMP, "w") #"a" = append
        myFile.write(finishedText)
        myFile.close()

        os.rename(EVENT_ACTION + EXTENSION_TEMP, EVENT_ACTION + EXTENSION_XML)

        

        
    def define_action_space(self): #TODO call after config file read
        '''
        Creates a set of all possible actions. The actions are not necessarily valid at every time step

        @precondition: the config file must have been read to create the workplan
        '''
        if self.workplan == {}:
            raise RuntimeError("Cannot define action space, workplan has not been initialized yet")

        for parttype in self.workplan:
            for processingstep in self.workplan[parttype]:
                for source in self.workplan[parttype][processingstep]:
                    for dest in self.workplan[parttype][processingstep][source]: 
                        self.actions.add((parttype,source,dest))
        
    
    def is_valid_action(self,action):
        '''
        An action is valid, if 
            - the source from which an part shall be moved is occupied 
            - the source contains a part, that matches the parrtype of the action
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
        return (action[parttype] == self.state[action[source]][ID_PARTTYPE]) and not self.state[action[destination]][ID_OCCUPIED] and is_in_workplan
        
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
