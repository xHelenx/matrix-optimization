from tensorforce.environments import Environment
import os
import numpy as np
from time import sleep
from DataExchanger import DataExchanger
from globalConstants import  COMMAND_ACTION_MOVE, debug_print, SLEEP_TIME
from dynamicConfigurations import  DEBUG_COMMAND 

class SPSEnvironmnet(Environment):
    def __init__(self):
        super().__init__()
        #terminal func or var?
        self.dataEx = DataExchanger()
        self.cnt = 0
    
    def states(self):
        '''
        Defines format of state
        '''
        return dict(type="int", shape=(1,), num_values=(pow(2,self.dataEx.totalMachine)-1)) #each machine can either be occupied or not
    
    def actions(self):
        '''
        Defines format of the actions
        '''
        return dict(type="int", shape=(1,), num_values=(len(self.dataEx.actions)-1))
    
    def reset(self):
        '''
        resets the simulation on the agent sides
        '''
        self.dataEx.terminal = False
        return np.zeros(shape=(1,), dtype=np.int)
    
    #def max_episode_timesteps(self):
    #    '''
    #    defines maximal time steps per episode
    #    '''
    #    return 50000
    def reward(self):
        '''
        Define reward as numerical value, init 0    
        '''
        return 0
    def execute(self,actions):
        '''
        Lets the simulation perform the chosen action
        @input actions - action to perform
        @ouput next_state - the consecutive state
               terminal   - whehter the last state was an end state of this episode
               reward     - given reward for action 
        '''

        if not self.dataEx.is_valid_action(actions): 
            #Action is invalid: so dont transfer information (everything can be calculated here)

            debug_print(str(actions) + ": \t invalid", DEBUG_COMMAND)

            next_state, reward = [self.dataEx.map_state_to_key()], self.dataEx.calculate_reward(actions) #state does not change, terminal, punish invalid action
            return next_state, self.dataEx.terminal, reward
        else:
            #Action is valid: send action, get reward, get state 
            self.dataEx.validActionsCounter += 1 
            debug_print(str(actions) + ": \t valid", DEBUG_COMMAND)
            #send action to simulation
            self.dataEx.write_command(commandtype=COMMAND_ACTION_MOVE, action=actions)
            
            #wait for receiving reward properties
            while not self.dataEx.received_reward:
                sleep(SLEEP_TIME)
            self.dataEx.received_reward = False

            #calculate reward according to reward properties, update terminal
            reward = self.dataEx.calculate_reward(actions) 
            
            debug_print(self.dataEx.terminal, DEBUG_COMMAND)
            #wait for new state 
            while (not self.dataEx.received_state) and (not self.dataEx.terminal):
                sleep(SLEEP_TIME)
            self.dataEx.received_state = False 

            return [self.dataEx.map_state_to_key()], self.dataEx.terminal, reward


