
from  readWriteFile import FileWriter
import os
from watchdog.observers import Observer
from watchdog.events import DirModifiedEvent, FileModifiedEvent, FileSystemEventHandler

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        print(event)
        if event.src_path == 'E:\Bachelorarbeit\src\simulation\state.xml':
            try:
                os.remove("action.xml")
            except: 
                pass
           
            state = "state.xml"
            file_writer.read_state(state)
            os.remove(state)
            file_writer.write_action_file("action", "Source1")
        
    

if __name__ ==  "__main__":
    file_writer = FileWriter()
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler,  path='E:\Bachelorarbeit\src\simulation',  recursive=False)
    observer.start()
    
    try:    
        os.remove("state.xml")
    except: 
        pass
    
    try:    
        os.remove("action.xml")
    except: 
        pass
  
    while(True):
       pass


