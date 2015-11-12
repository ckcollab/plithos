from deap import algorithms, base, creator, tools

from ..simulator import Simulator


class DEAPSingleDroneExperiment(Simulator):
    ACTIONS = ('up', 'down', 'left', 'right')

    def __init__(self, *args, **kwargs):
        super(DEAPSingleDroneExperiment, self).__init__(*args, **kwargs)
        print "Starting experiment..."

        self.deap_toolbox = base.Toolbox()
        self.deap_toolbox.register("mate", tools.cxTwoPoint)
        self.deap_toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.2)
        self.deap_toolbox.register("select", tools.selTournament, tournsize=3)
        self.deap_toolbox.register("evaluate", self.evaluate_individual)

    def evaluate_individual(self, individual):
        """The fitness of an individual is how many steps it took to find the target"""
        return len(individual)

    def start(self):
        self.init_game()

        while True:
            self._check_pygame_events()




            # Eval









            self._draw()
