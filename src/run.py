from plithos.simulations.random_mover import RandomMover
from plithos.simulations.dqn_single_drone import DQNSingleDroneExperiment
from plithos.simulations.hand_controlled import HandControlled


if __name__ == '__main__':
    experiment = DQNSingleDroneExperiment(width=40, height=40, sensor_radius=4)
    #experiment = RandomMover(width=40, height=40, sensor_radius=4)
    #experiment = HandControlled(width=40, height=40, sensor_radius=4)
    experiment.start()


