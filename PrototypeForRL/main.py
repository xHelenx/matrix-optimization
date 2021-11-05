import os
from watchdog.observers import Observer
from watchdog.events import DirModifiedEvent, FileModifiedEvent, FileSystemEventHandler
from DataExchanger import DataExchanger
from globalConstants import MYPATH, EVENT_CONFIG,EVENT_REWARD,EVENT_ACTION, \
    EVENT_STATE,EXTENSION_XML,EXTENSION_TEMP, debug_print
class FileHandler(FileSystemEventHandler):
    
    def on_created(self, event):
        if   event.src_path == (MYPATH + EVENT_STATE + EXTENSION_XML):
            debug_print("STATE")
        elif event.src_path == (MYPATH + EVENT_ACTION + EXTENSION_XML):
            debug_print("ACTION")
        elif event.src_path == (MYPATH + EVENT_REWARD + EXTENSION_XML):
            debug_print("REWARD")
        elif event.src_path == (MYPATH + EVENT_CONFIG + EXTENSION_XML):
            debug_print("CONFIG")
        elif not (event == MYPATH + EVENT_CONFIG + EXTENSION_TEMP or event == MYPATH + EVENT_STATE + EXTENSION_TEMP \
            or event == MYPATH + EVENT_ACTION + EXTENSION_TEMP or event == MYPATH + EVENT_REWARD + EXTENSION_TEMP):
            raise ValueError("Unknown file type created, no event exists to handle this file")
    

if __name__ ==  "__main__":
    de = DataExchanger()
    de.read_file(EVENT_CONFIG)
    while(True):
        pass





    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler,  path=MYPATH,  recursive=False)
    observer.start()

    
    #clean up old files 
    all_events = [EVENT_ACTION,EVENT_REWARD,EVENT_CONFIG,EVENT_STATE]
    for file in all_events:
        try:    
            os.remove(MYPATH + file + EXTENSION_XML)
        except: 
            pass
    
    while(True):
       pass
