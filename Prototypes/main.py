from os import write
from  readWriteFile import FileWriter
import os
from watchdog.observers import Observer
from watchdog.events import DirModifiedEvent, FileModifiedEvent, FileSystemEventHandler

class MyHandler(FileSystemEventHandler):
    #def __init__(self):
    #    self.updated = False
    def on_created(self, event):
        if event == FileModifiedEvent or DirModifiedEvent:
            state = "state.xml"
            file_writer.read_state(state)
            file_writer.write_action_file("action.xml", "Station0")
            os.remove(state)
    

if __name__ ==  "__main__":
    file_writer = FileWriter()
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler,  path='E:\Bachelorarbeit\Prototypes',  recursive=False)
    observer.start()
    try:
        os.remove("state.xml")
    except: 
        pass

    while(True):
       pass


