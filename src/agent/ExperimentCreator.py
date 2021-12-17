
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
import itertools
from dynamicConfigurations import EXPERIMENT_PATH

class ExperimentCreator: 
    def __init__(self):
        '''
        Add variable to agent or simulation, then choose if it is dynamic or static 
        
        '''
        #TODO show more specifc which values may be changed + ranges
        #list of all agent related params
        
        #dynamic
        self.discount_factors  = {"discount_factor":[0.99]} #0.3,0.5
        self.learning_rates    = {"learning_rate":[0.005]} #0.005, 0.1
        self.episodes          = {"episodes":[200]}
        #self.max_timesteps     = {"max_timesteps": [10.000]}
        self.exploration_rates = {"exploration_rate": [0]} #.001,0.1
        self.batch_sizes       = {"batch_size":[1]} #10 
        self.reward_type = {"reward_type" : [1]}
        self.action_type = {"action_type" : [1]}
        self.agent_type  = {"agent_type"  : ["ppo", "random"]}


        temp_dyn      = [self.discount_factors,self.learning_rates,self.episodes,self.exploration_rates,self.batch_sizes, self.reward_type, self.action_type, self.agent_type]
        self.agent_param_dyn = dict()

        for elem in temp_dyn:
            self.agent_param_dyn.update(elem)

        #statics  
        #temp_stat      = [self.reward_type, self.action_type, self.agent_type]
        #self.agent_param_stat = dict()

        #for elem in temp_stat:
        #    self.agent_param_stat.update(elem)


        #list of all simulation related parameter
        self.demands          = {"demand": [10,200]} 

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

    #TODO delete old config`?`
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
                foldername = foldername + key + "-" + str(experiments[id][key]) + "-"

            
            child_agent = ET.SubElement(child_ID,"agent")
            for key in self.agent_param_dyn.keys():  
                #print(key,experiments[id][key])
                child_params = ET.SubElement(child_agent,key)
                child_params.text = str(experiments[id][key])
                foldername = foldername + key + "-" + str(experiments[id][key]) + "-"
            
            #for key in self.agent_param_stat.keys():  
            #    child_params = ET.SubElement(child_agent,key)
            #    child_params.text = str(self.agent_param_stat[key])
            #    foldername = foldername + key + "-" + str(self.agent_param_stat[key]) + "-"
            
            id += 1
            
            child_foldername = ET.SubElement(child_agent,"foldername")
            child_foldername.text = foldername
            
        
        finishedText = self.format_output(root)
        
        
        #print(EXPERIMENT_PATH)
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
        root = ET.Element("configuration")
        foldername = ""
        #print(experiment)

        child_sim = ET.SubElement(root,"simulation")
        for key in self.simulation_params.keys():  
            #print(key,experiment[key])
            child_params = ET.SubElement(child_sim,key)
            child_params.text = str(experiment[key])
            foldername = foldername + key + "-" + str(experiment[key]) + "-"
        
        child_agent = ET.SubElement(root,"agent")
        for key in self.agent_param_dyn.keys():  
            #print(key,experiment[key])
            child_params = ET.SubElement(child_agent,key)
            child_params.text = str(experiment[key])
            foldername = foldername + key + "-" + str(experiment[key]) + "-"
        

        #for key in self.agent_param_stat.keys():  
        #    child_params = ET.SubElement(child_agent,key)
        #    child_params.text = str(self.agent_param_stat[key])
        #    foldername = foldername + key + "-" + str(self.agent_param_stat[key]) + "-"
                   
        finishedText = self.format_output(root)
        
        os.mkdir(EXPERIMENT_PATH + foldername)
        myFile = open(EXPERIMENT_PATH  + foldername + "//" + foldername + ".xml", "w") #"a" = append
        myFile.write(finishedText)
        myFile.close()
