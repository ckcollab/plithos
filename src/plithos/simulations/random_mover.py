import random
from ..simulator import Simulator


class RandomMover(Simulator):
    ACTIONS = ('up', 'down', 'left', 'right')

    def start(self):
        self.init_game()

        while True:
            self._check_pygame_events()

            for drone in self.drones:
                drone.do_action(random.choice(['up', 'down', 'left', 'right']))

            self.print_map()

            self._draw()
