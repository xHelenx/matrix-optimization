from tensorforce.environments import Environment
import os
import numpy as np
from DataExchanger import DataExchanger
from globalConstants import ACTIONTYPE_MOVE, ACTIONTYPE_RESET, DEBUG_ACTIONS, DEBUG_STATES, EVENT_ACTION, MYPATH, EXTENSION_XML, debug_print

class SPSEnvironmnet(Environment):
    def __init__(self):
        super().__init__()
        #terminal func or var?
        self.dataEx = DataExchanger()
    def states(self):
        return dict(type="int", shape=(1,), num_values=(pow(2,self.dataEx.totalMachine)-1)) #each machine can either be occupied or not
    def actions(self):
        return dict(type="int", shape=(1,), num_values=(len(self.dataEx.actions)-1))
    def reset(self):
        self.dataEx.terminal = False
        return np.zeros(shape=(1,), dtype=np.int)
    def max_episode_timesteps(self):
        return 1000
    def reward(self):
        return 0
    def execute(self,actions):

        if not self.dataEx.is_valid_action(actions): #check if action is valid
            debug_print(str(actions) + ": \t invalid", DEBUG_ACTIONS)

            next_state, reward = [self.dataEx.map_state_to_key()], self.dataEx.calculate_reward(False) #state does not change, terminal, punish invalid action
            return next_state, self.dataEx.terminal, reward
        else:
            debug_print(str(actions) + ": \t valid", DEBUG_ACTIONS)
            #send action to simulation
            self.dataEx.write_action(actions, ACTIONTYPE_MOVE)
            
            #wait for receiving reward properties
            while not self.dataEx.received_reward:
                pass
            self.dataEx.received_reward = False

            #calculate reward according to reward properties, update terminal
            reward = self.dataEx.calculate_reward(True) 
            
            #wait for new state 
            while not self.dataEx.received_state:
                pass
            self.dataEx.received_state = False 
            debug_print("current state ID: " + str(self.dataEx.current_state_id), DEBUG_STATES)
            return [self.dataEx.map_state_to_key()], self.dataEx.terminal, reward

