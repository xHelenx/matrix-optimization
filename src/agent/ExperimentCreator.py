import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
import itertools
from dynamicConfigurations import  EXPERIMENT_PATH

class ExperimentCreator: 
    def __init__(self):
        '''
        How to create your experiment: 
        You can change the following parameters within the shown range 
        - discount factor   [0,1]                                                                 
        - learning rate     (0,1]
        - episode           [1,inf] (dramatically increases computation time, max tested is 400)
        - exploration rate  [0,1]
        - batch size        [1,inf] (needs to be smaller than episodes)
        - reward type       {"mayer","mayer_-_100_-5","mayer_-_10000_-5","mayer_-_10000_-25", "mayer_+_100_-5","mayer_+_10000_-5","mayer_+_10000_-25"}
        - agent type        {"ppo", "ddqn"}
        - demand  (line 52) [1,inf] (drasticall increases computation time, max tests is 100)

        by adding values to list inside the dictionary.
        Examples are given behind each parameter.
        After editing the configurations, run "GenerateExperiments.py". 
        Also refer to chapter 6 of Annex A, as it explains the setup of experiments.
        
        '''
      #-------> HERE    
        #dynamic
        self.discount_factors  = {"discount_factor":[0.99]} #[0.3,0.5,0.99]
        self.learning_rates    = {"learning_rate":[0.001]} #[0.005, 0.001, 0.1]
        self.episodes          = {"episodes":[100]} #[20,100,150]
        self.exploration_rates = {"exploration_rate": [0, 0.01]} #[]0, 0.001,0.1]
        self.batch_sizes       = {"batch_size":[1]} # [1,10] 
        self.reward_type = {"reward_type" : ["mayer_+_10000_-5",]} 
        #["mayer","mayer_-_100_-5","mayer_-_10000_-5","mayer_-_10000_-25"]
        self.action_type = {"action_type" : [1]} #extendible in the future
        self.agent_type  = {"agent_type"  : ["ppo"]} #["ppo", "ddqn"]
        
        
        
        
        
        self.analysis_type = {"analysis_type":["training" , "evaluation"]} #ORDER IS MANDATORY
        temp_dyn      = [self.analysis_type, self.discount_factors,self.learning_rates,self.episodes,self.exploration_rates,self.batch_sizes, self.reward_type, self.action_type, self.agent_type]
        self.agent_param_dyn = dict()

        for elem in temp_dyn:
            self.agent_param_dyn.update(elem)

        #list of all simulation related parameter
    #-------> HERE 
        self.demands          = {"demand": [100]} 

        temp =  [self.demands]
        self.simulation_params = dict()
        for elem in temp:
            self.simulation_params.update(elem)

        #combined
        self.hyper_params = dict()
        self.hyper_params.update(self.agent_param_dyn)
        self.hyper_params.update(self.simulation_params)
        
        

    def create_grid_search_experiments(self):
        #create a grid combination of all parameters defined in init
        #writes each combination towards the experiments file
            #demand for simu
            #one dict for agent, one for env..

        hypnames, hypvalues = zip(*self.hyper_params.items())
        print(hypvalues)
        grid_hyperparam = [dict(zip(hypnames, h)) for h in itertools.product(*hypvalues)]
        
        self.create_experiment_file(grid_hyperparam)
        for id in range(len(grid_hyperparam)):
            #print(grid_hyperparam[id])
            self.write_experiment_to_file(grid_hyperparam[id])

    def create_experiment_file(self, experiments):
        #writing the file of experiments
        root = ET.Element("experiments")
        

        for id in range(len(experiments)):
            foldername = ""
            child_ID = ET.SubElement(root,"ID")
            child_ID.text = str(id)    

            child_sim = ET.SubElement(child_ID,"simulation")
            for key in self.simulation_params.keys():  
                #print(key,experiments[id][key])
                child_params = ET.SubElement(child_sim,key)
                child_params.text = str(experiments[id][key])
               
            
            child_agent = ET.SubElement(child_ID,"agent")
            for key in self.agent_param_dyn.keys():  
                #print(key,experiments[id][key])
                child_params = ET.SubElement(child_agent,key)
                child_params.text = str(experiments[id][key])
              

            child_foldername = ET.SubElement(child_agent,"foldername")
            child_foldername.text = self.get_foldername(experiments[id])
            id += 1
        
        finishedText = self.format_output(root)
        
        
        myFile = open(EXPERIMENT_PATH + "experiment.xml", "w") #"a" = append
        myFile.write(finishedText)
        myFile.close()

    def format_output(self,text):
        '''
        Formats a given text to be easier to read
        '''
        rough_string = ET.tostring(text, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    def write_experiment_to_file(self, experiment):
        if experiment["analysis_type" ] == "training":

            root = ET.Element("configuration")

            child_sim = ET.SubElement(root,"simulation")
            for key in self.simulation_params.keys():  
                #print(key,experiment[key])
                child_params = ET.SubElement(child_sim,key)
                child_params.text = str(experiment[key])
                
            child_agent = ET.SubElement(root,"agent")
            for key in self.agent_param_dyn.keys():  
                #print(key,experiment[key])
                child_params = ET.SubElement(child_agent,key)
                child_params.text = str(experiment[key])
               
                    
            finishedText = self.format_output(root)
            foldername = self.get_foldername(experiment)
            os.mkdir(EXPERIMENT_PATH + foldername)
            myFile = open(EXPERIMENT_PATH  + foldername + "//agent_config.xml", "w") #"a" = append
            myFile.write(finishedText)
            myFile.close()
        elif experiment["analysis_type"] == "evaluation": 
            pass

    def get_foldername(self, currentExperiment):
        return "dem-" + str(currentExperiment["demand"]) + "-df-" + str(currentExperiment["discount_factor"]) + \
                "-lr-" + str(currentExperiment["learning_rate"]) + "-eps-" + str(currentExperiment["episodes"]) + \
                "-expl-" + str(currentExperiment["exploration_rate"]) + "-bat-" + str(currentExperiment["batch_size"]) + \
                "-" + str(currentExperiment["reward_type"]) + "-act-" +str(currentExperiment["action_type"]) +\
                "-" + str(currentExperiment["agent_type"])