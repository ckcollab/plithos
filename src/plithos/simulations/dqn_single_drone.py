import numpy as np

from ..deep_q_learner import DQNAgent
from ..numpy_surfarray import array2d
from ..simulator import Simulator


class DQNSingleDroneExperiment(Simulator):
    ACTIONS = ('up', 'down', 'left', 'right')

    def __init__(self, *args, **kwargs):
        super(DQNSingleDroneExperiment, self).__init__(*args, **kwargs)
        print "Starting experiment..."
        print "  state_num =", self.height * self.width
        self.agent = DQNAgent(self.height * self.width, len(self.ACTIONS))

    def start(self):
        self.init_game()

        while True:
            self._check_pygame_events()

            state = self.map.copy()
            import ipdb;ipdb.set_trace()
            action = self.agent.get_action(state)
            reward = 0


            self.drones[0].do_action(self.ACTIONS[action])

            # Get state after action
            next_state = self.map.copy()

            self.agent.learn(state, action, reward, next_state)

            #import random
            #self.drones[0].do_action(random.choice(['up', 'down', 'left', 'right']))

            self._draw()
