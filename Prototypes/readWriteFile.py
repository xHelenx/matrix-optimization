import xml.etree.ElementTree as ET
from xml.dom import minidom

def read_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    ##tag for identifier, text for value, attr for cases like:  <country name="Liechtenstein">
    for items in root[0]:
        print(items.tag, ":", items.text)

def write_action_file(filename,item, source, destination):
    root = ET.Element("action")
    child_item =ET.SubElement(root,"item")
    child_item.text = item

    child_source = ET.SubElement(root,"source")
    child_source.text = source

    child_destination = ET.SubElement(root,"destination")
    child_destination.text = destination

    finishedText = format_output(root)
    myFile = open(filename, "w") #"a" append
    myFile.write(finishedText)
    myFile.close()
    #print(format_output(root))

def write_reward_file(filename):
    root = ET.Element("reward")
    child_item =ET.SubElement(root,"StatThroughputPerMinute")
    child_item.text = "99"

    finishedText = format_output(root)
    myFile = open(filename, "w") #"a" append
    myFile.write(finishedText)
    myFile.close()

def format_output(text):
    rough_string = ET.tostring(text, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
