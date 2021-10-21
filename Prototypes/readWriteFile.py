import xml.etree.ElementTree as ET
from xml.dom import minidom

class FileWriter:
    def __init__(self):
        self.m1_occupied = True
        self.m2_occupied = True

    def read_file(self,filename):
        tree = ET.parse(filename)
        root = tree.getroot()

        ##tag for identifier, text for value, attr for cases like:  <country name="Liechtenstein">
        for items in root[0]:
            print(items.tag, ":", items.text)

    def read_state(self,filename):
        tree = ET.parse(filename)
        root = tree.getroot()

        self.m1_occupied = root[0][0].text == "true" #M1,Occupied:
        self.m2_occupied = root[1][0].text == "true"
        
    def write_action_file(self,filename, source):
        root = ET.Element("action")

        child_source = ET.SubElement(root,"source")
        child_source.text = source

        child_destination = ET.SubElement(root,"destination")
        ##very simple version for decison making
        
        destination = "XX"
        
        if (self.m1_occupied) and (not self.m2_occupied):
            destination = "M2"
        elif (not self.m1_occupied) and (self.m2_occupied):
            destination = "M1"
        elif (self.m1_occupied) and (self.m2_occupied):
            destination = "M1"
        elif (not self.m1_occupied) and (not self.m2_occupied):
            destination = "M2"
        
        child_destination.text = destination

        finishedText = self.format_output(root)
        myFile = open(filename, "w") #"a" append
        myFile.write(finishedText)
        myFile.close()
        #print(format_output(root))

    def write_reward_file(self,filename):
        root = ET.Element("reward")
        child_item =ET.SubElement(root,"StatThroughputPerMinute")
        child_item.text = "99"

        finishedText = self.format_output(root)
        myFile = open(filename, "w") #"a" append
        myFile.write(finishedText)
        myFile.close()

    def format_output(self,text):
        rough_string = ET.tostring(text, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
