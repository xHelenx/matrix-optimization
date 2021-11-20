from tensorforce.environments import Environment

from DataExchanger import DataExchanger

class SPSEnvironmnet(Environment):
    def __init__(self):
        super().__init__()
        #terminal func or var?
        self.dataEx = DataExchanger()
    def states(self):
        return self.dataEx.state 
    def actions(self):
        return self.dataEx.actions  ###maybe has to be a dict?!
    def max_episode_timsteps(self):
        return 0
    def execute(self,actions):
        return 0
    def reward(self):
        return 0