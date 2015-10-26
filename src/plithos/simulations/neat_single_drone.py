from ..deep_q_learner import DQNAgent
from ..numpy_surfarray import array2d
from ..simulator import Simulator


class NEATSingleDroneExperiment(Simulator):
    ACTIONS = ('up', 'down', 'left', 'right')

    def __init__(self, *args, **kwargs):
        super(NEATSingleDroneExperiment, self).__init__(*args, **kwargs)
        print "Starting experiment..."
        self.agent = None # yet..

    def on_tick(self):
        pass

    def start(self):
        self.init_game()

        while True:
            self._check_pygame_events()

            # asdf

            self._draw()
