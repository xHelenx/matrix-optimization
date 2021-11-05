from abc import abstractproperty
from typing import Text
import xml.etree.ElementTree as ET
from xml.dom import minidom
import json

from globalConstants import ID_PROCTIME, MYPATH, EVENT_CONFIG,EVENT_REWARD, \
EVENT_ACTION,EVENT_STATE, EXTENSION_XML,EXTENSION_TEMP, ID_OCCUPIED, \
ID_PARTTYPE, ID_REMAININGPROCTIME, NONE, PARTA, PARTB, debug_print

class DataExchanger:
    def __init__(self):
        self.workplan = dict() #{Parttype:{ProcessingStep:{{machine_src: {{machine_dest:totalproctime}}}}} 
        #latter extend with total processing type to see performance consequences for RL
        self.state = dict() #{Machine}:{Occupation, RemainingProcTime,PartType}}
        self.actions = set() #{{Parttype:{src:dest}}..}
        self.reward = 0 #float 

    def read_file(self, event):
        debug_print(event + EXTENSION_XML)
        tree = ET.parse(event + EXTENSION_XML)
        root = tree.getroot()

        if event == EVENT_CONFIG:
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
                debug_print({part.tag:procstep_dict})
                self.workplan.update({part.tag:procstep_dict})
                procstep_dict = {}
                    
            #print(json.dumps(self.workplan[PARTB]["P3"], sort_keys=False, indent=4))
            print(self.workplan)
            
        elif event == EVENT_STATE:
            for machine in root:
                #print(machine.tag)
                machine_properties = {}
                for property in machine:
                    if property.tag == ID_OCCUPIED:
                        if property.text == "true":
                            machine_properties.update({ID_OCCUPIED:True})
                        else:
                            machine_properties.update({ID_OCCUPIED:False})
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
        elif event == EVENT_ACTION:
            pass
        elif event == EVENT_REWARD:
            pass
        

    def format_xml(self,file):
        ''' shows the content of the XML file. This function is used for debug purposes
        Input: file - the xml-file, that should be read
        Output: string, containing the content of "file" 
        '''
        tree = ET.parse(file)
        root = tree.getroot()
        rough_string = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
