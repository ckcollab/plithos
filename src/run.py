import argparse

from plithos.simulations.random_mover import RandomMover
from plithos.simulations.deap_genetic import DEAPSingleDroneExperiment
#from plithos.simulations.dqn_single_drone import DQNSingleDroneExperiment
from plithos.simulations.hand_controlled import HandControlled
from plithos.simulations.manual_ai import ManualAIExperiment


if __name__ == '__main__':
    simulations = {
        'random': RandomMover,
        #'deepq': DQNSingleDroneExperiment,
        'hand': HandControlled,
        'ai': ManualAIExperiment,
        'deap': DEAPSingleDroneExperiment,
    }
    simulations_string = ', '.join(simulations.keys())

    parser = argparse.ArgumentParser(description='Run search simulation', add_help=False)
    parser.add_argument(
        'simulation', default='ai', nargs='?', type=str, help='type of simulation, options: %s' % simulations_string
    )
    parser.add_argument(
        '-w', '--width', default=40, type=int, help='width'
    )
    parser.add_argument(
        '-h', '--height', default=40, type=int, help='height'
    )
    parser.add_argument(
        '-r', '--radius', default=4, type=int, help='sensor radius of each drone'
    )
    parser.add_argument(
        '-d', '--drone_count', default=1, type=int, help='number of drones to spawn in simulation'
    )
    parser.add_argument("-?", "--help", action="help", help="show this help message and exit")

    args = parser.parse_args()

    if args.simulation not in simulations.keys():
        print "Simulation name not recognized, must be one of: %s" % simulations_string
        exit(-1)

    experiment_class = simulations[args.simulation]

    experiment = experiment_class(
        width=args.width,
        height=args.height,
        sensor_radius=args.radius,
        drone_count=args.drone_count,
    )
    experiment.start()


