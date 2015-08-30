import logging
import numpy as np
import pygame

from deep_q.q_network import DeepQLearner
from deep_q.ale_agent import NeuralAgent
from deep_q.ale_experiment import ALEExperiment
from math import hypot
from pygame import *
from random import randint, choice

from utils import circle_iterator
from vec2d import Vec2d


WIDTH = 80
HEIGHT = 80
IS_DISPLAYING = False


class Entity(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((2, 2))
        self.rect = self.image.get_rect()
        self.velocity_x = randint(-2, 2)
        self.velocity_y = randint(-2, 2)
        self.acceleration_x = .1
        self.acceleration_y = .1
        self.friction = 0.01

    @property
    def x(self):
        return self.rect.center[0]

    @property
    def y(self):
        return self.rect.center[1]
    #def thrust(self, direction):


# class Sensor(pygame.sprite.Sprite):
#
#     def __init__(self, radius):
#         pygame.sprite.Sprite.__init__(self)
#         self.image = pygame.Surface((radius, radius))
#         self.image.fill(pygame.color.Color('white'))
#         self.rect = self.image.get_rect()
#         self.rect.center = (
#             randint(WIDTH * .9, WIDTH),
#             randint(HEIGHT * .9, HEIGHT)
#         )
#         self.radius = radius
#
#     def update(self):
#         pygame.draw.circle(self.image, (255,0,0), (self.rect.x, self.rect.y), self.radius, 2)


class Drone(Entity):

    def __init__(self, simulator, sensor_type='visible', sensor_radius=8):
        super(Drone, self).__init__()
        self.simulator = simulator
        self.sensor_type = sensor_type
        self.sensor_radius = sensor_radius

        # Keeping track of distance from target search area
        self.goal_last_seen_x = WIDTH * 0.1
        self.goal_last_seen_y = HEIGHT * 0.1
        self._old_distance_from_target_area = 0
        self.current_distance_from_target_area = 0

        # Make the sprite a big enough rectangle to display the sensor distance
        self.image = pygame.Surface((self.sensor_radius * 2, self.sensor_radius * 2))
        self.image.set_colorkey((0, 0, 0))
        self.image.fill((0, 0, 0))
        # Drones start in bottom right
        self.rect.center = (
            randint(WIDTH * .7, WIDTH * .9), #randint(WIDTH * .9, WIDTH),
            randint(HEIGHT * .7, HEIGHT * .9), #randint(HEIGHT * .9, HEIGHT)
        )

        # self.sensor_distance is
        pygame.draw.circle(
            self.image,
            (100, 0, 0),  # light red color
            (self.sensor_radius, self.sensor_radius),  # center of circle ??
            self.sensor_radius,  # radius for the circle
            1
        )

        # Place the rectangle in the middle, -1 sensor distance so it is right in the center instead of offset
        # to the bottom right
        pygame.draw.rect(
            self.image,
            pygame.color.Color('white'),
            (self.sensor_radius - 1, self.sensor_radius - 1, 1, 1),
            1
        )

    def _move(self, direction):
        if direction == 'up':
            self.rect.y -= 1
        elif direction == 'down':
            self.rect.y += 1
        elif direction == 'left':
            self.rect.x -= 1
        elif direction == 'right':
            self.rect.x += 1

    # @property
    # def state(self):
    #     '''Returns the area around the drone starting from the top left, skipping drones location, and
    #     continues to the bottom right. Also, appends the distance to the target area as the last
    #     element in the state list.'''
    #     state = []
    #     for x in range(-1, 2):
    #         for y in range(-1, 2):
    #             if x == 0 and y == 0:
    #                 continue  # skip our location
    #             print x, ",", y
    #             state.append(self.simulator.map[self.x + x][self.y + y])
    #
    #     # Also append distance to where goal was last seen
    #     goal_last_seen_x = WIDTH * 0.05
    #     goal_last_seen_y = HEIGHT * 0.05
    #     state.append(hypot(goal_last_seen_x - self.x, goal_last_seen_y - self.y))
    #     return state
    def _get_current_reward(self):
        '''Reward system:
            - +1 for each unexplored tile
            - -5 for each drone next to you
            - +1 if new position is closer to target'''
        reward = 0

        # Did we find it?
        # if self.is_goal_in_range(Simulator._instance.objectives[0].x, Simulator._instance.objectives[0].y):
        #     reward += 100

        # Are we closer?
        # if self.current_distance_from_target_area < self._old_distance_from_target_area:
        #     reward += 1
        # else:
        #     reward -= 1
        reward += self.current_distance_from_target_area / 10

        # Handle tiles in our sensor radius
        for _, _, tile in self.get_tiles_within_sensor_radius():
            if tile == 0:  # unexplored tile
                reward += 1
            elif tile == -1:  # explored tile
                reward -= 0.25
            elif tile == None:  # tile out of bounds
                reward -= 0.05

        # If we go out of bounds really remove a lot of points
        # if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
        #     reward -= 1

        # print "self x/y:", self.x, self.y
        # print "center x/y:", self.rect.center[0], self.rect.center[1]
        # print "current reward: ", reward
        self.reward = reward

    def _fill_in_explored_area(self):
        global IS_DISPLAYING
        for x, y, tile in self.get_tiles_within_sensor_radius():
            # If the tile has not been explored and isn't a drone/objective (1/2), mark it as explored
            if tile <= 0:
                # Mark our old tile as explored (-1 is explored)
                try:
                    self.simulator.map[x][y] = -1

                    # Put a pixel at the explored tile
                    if IS_DISPLAYING:
                        self.simulator.explored_layer.fill(
                            Simulator.EXPLORED_MAP_COLOR,
                            ((x, y), (1, 1))
                        )
                except IndexError:
                    pass

    def do_action(self, action):
        '''Move to the new tile but record old reward and get new one. Also mark explored tiles.

        action is a direction from Simulator.ACTIONS'''
        global IS_DISPLAYING

        # Save old distance
        if self.current_distance_from_target_area != 0:
            self._old_distance_from_target_area = self.current_distance_from_target_area
        else:
            self._old_distance_from_target_area = hypot(
                self.goal_last_seen_x - self.x,
                self.goal_last_seen_y - self.y
            )

        # Mark old tile as explored, it was set tp 1 for drone
        try:
            self.simulator.map[self.x + self.sensor_radius][self.y + self.sensor_radius] = -1
        except IndexError:
            pass
        # Put a pixel at the explored tile
        if IS_DISPLAYING:
            self.simulator.explored_layer.fill(
                Simulator.EXPLORED_MAP_COLOR,
                ((self.x + self.sensor_radius, self.y + self.sensor_radius), (1, 1))
            )

        self._move(action)  # action is a direction here

        # Mark new tile as drone (1 means drone)
        try:
            self.simulator.map[self.x + self.sensor_radius][self.y + self.sensor_radius] = 1
        except IndexError:
            pass

        self.current_distance_from_target_area = hypot(
            self.goal_last_seen_x - self.x,
            self.goal_last_seen_y - self.y
        )

        # Mark explored tiles but, _before_ marking them check what our reward was
        self._get_current_reward()
        self._fill_in_explored_area()

    def is_out_of_bounds(self):
        return self.x < 0 or self.x > WIDTH or self.y < 0 or self.y >= HEIGHT

    def get_tiles_within_sensor_radius(self):
        '''Returns (x, y, tile_value)'''
        center_x, center_y = self.rect.center
        for circle_x, circle_y in circle_iterator(center_x, center_y, self.sensor_radius):
            try:
                yield circle_x + self.sensor_radius, \
                      circle_y + self.sensor_radius, \
                      self.simulator.map[circle_x + self.sensor_radius][circle_y + self.sensor_radius]
            except IndexError:
                yield circle_x + self.sensor_radius, \
                      circle_y + self.sensor_radius, \
                      None

    def is_goal_in_range(self, goal_x, goal_y):
        # Offset our x/y with the sensor radius because the self x/y are the top left of the drone sprite
        return hypot(
            self.x + self.sensor_radius - goal_x,
            self.y + self.sensor_radius - goal_y,
        ) <= self.sensor_radius



class Objective(Entity):
    def __init__(self):
        super(Objective, self).__init__()
        self.image.fill(pygame.color.Color('green'))
        # Drones start in top left
        self.rect.center = (
            randint(WIDTH * .05, WIDTH * .2),
            randint(WIDTH * .05, HEIGHT * .2)
        )


class Simulator(object):
    ACTIONS = ('up', 'left', 'down', 'right')
    EXPLORED_MAP_COLOR = (0, 100, 100)
    TILE_OUT_OF_BOUNDS = None
    TILE_EXPLORED = -1
    TILE_UNEXPLORED = 0
    TILE_DRONE = 1
    TILE_OBJECTIVE = 2

    # Singleton stuff
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Simulator, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, screen):
        self.screen = screen

    def get_all_entities(self):
        return self.drones + self.objectives # + self.sensors

    def reset_map(self):
        '''
        Sets self.map points where drones/objectives exist.

        Current map legend:
            - 0 is unexplored, nothing there
            - 1 is a drone
            #- 2 is the objective
            - < 0 is explored, but updated each tick. So -1 was just explored, -0.99 was explored 1 tick ago..
                  something like that
        '''
        self.map = np.zeros((WIDTH, HEIGHT), dtype=np.int)

        try:
            for drone in self.drones:
                self.map[drone.x][drone.y] = 1
            #for objective in self.objectives:
            #    self.map[objective.x][objective.y] = 2
        except IndexError:
            pass

    def reset_game(self):
        self.drones = [Drone(self) for _ in range(1)]  # limit to 1 drone for now
        self.objectives = [Objective()]
        #self.sensors = [drone.sensor for drone in self.drones]
        #self.map = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.reset_map()

        # Setup background & explored layer
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))  # black
        self.screen.blit(self.background, (0, 0))

        self.explored_layer = pygame.Surface(self.screen.get_size())
        self.explored_layer = self.explored_layer.convert()
        self.explored_layer.set_colorkey((0, 0, 0))
        self.explored_layer.fill((0, 0, 0))

        # Add all sprites to sprite group
        self.sprites = pygame.sprite.Group()
        for entity in self.get_all_entities():
            self.sprites.add(entity)

    def act(self, action):
        '''action is string like "right", "up"'''
        # we can't do multiple drones yet...
        self.drones[0].do_action(action)
        #self.update()
        return self.drones[0].reward

    # def is_game_over(self):
    #     return self.does_any_drone_see_target()

    def does_any_drone_see_target(self):
        for drone in self.drones:
            if drone.is_goal_in_range(self.objectives[0].x, self.objectives[0].y):
                return True
        return False

    def is_any_drone_out_of_bounds(self):
        return any(drone.is_out_of_bounds() for drone in self.drones)


class PlithosExperiment(object):
    def __init__(self, simulator, agent, num_epochs, epoch_length, test_length, frame_skip, rng):
        # self.ale = ale
        self.simulator = simulator
        self.agent = agent
        self.num_epochs = num_epochs
        self.epoch_length = epoch_length
        self.test_length = test_length
        self.frame_skip = frame_skip
        self.min_action_set = simulator.ACTIONS # self.min_action_set = ale.getMinimalActionSet()
        # self.width, self.height = ale.getScreenDims()
        self.maximum_number_of_steps_before_giving_up = 1000

        self.buffer_length = 2
        self.buffer_count = 0
        # self.screen_buffer = np.empty((self.buffer_length, WIDTH, HEIGHT),
        #                               dtype=np.uint8)

        # self.terminal_lol = False # Most recent episode ended on a loss of life
        # self.max_start_nullops = max_start_nullops
        self.rng = rng

    def run(self):
        """
        Run the desired number of training epochs, a testing epoch
        is conducted after each training epoch.
        """
        for epoch in range(1, self.num_epochs + 1):
            print "On epoch:", epoch, "of", self.num_epochs + 1
            self.run_epoch(epoch, self.epoch_length)
            self.agent.finish_epoch(epoch)
            if self.test_length > 0:
                self.agent.start_testing()
                self.run_epoch(epoch, self.test_length, True)
                self.agent.finish_testing(epoch)

    def run_epoch(self, epoch, num_steps, testing=False):
        """ Run one 'epoch' of training or testing, where an epoch is defined
        by the number of steps executed.  Prints a progress report after
        every trial
        Arguments:
        epoch - the current epoch number
        num_steps - steps per epoch
        testing - True if this Epoch is used for testing and not training
        """
        self.terminal_lol = False # Make sure each epoch starts with a reset.
        steps_left = num_steps
        while steps_left > 0:
            prefix = "testing" if testing else "training"
            logging.info(prefix + " epoch: " + str(epoch) + " steps_left: " +
                         str(steps_left))
            num_steps = self.run_episode(steps_left, testing)
            steps_left -= num_steps

    #def _adjust_reward_based_on_step_count(self, steps_since):

    def run_episode(self, max_steps, testing):
        """Run a single training episode.
        The boolean terminal value returned indicates whether the
        episode ended because the game ended or the agent died (True)
        or because the maximum number of steps was reached (False).
        Currently this value will be ignored.
        Return: (terminal, num_steps)
        """
        #self._init_episode()
        self.simulator.reset_game()

        #start_lives = self.ale.lives()

        action = self.agent.start_episode(self.simulator.map)#(self.get_observation())
        num_steps = 0
        done = False
        while True:
            reward = self._step(self.min_action_set[action])

            if self.simulator.does_any_drone_see_target():
                # Base reward for finding target
                reward += 100
                # Adjust reward based on step count
                reward += float(self.maximum_number_of_steps_before_giving_up) / float(num_steps)
                print "@@ Found target in", num_steps, "steps; reward =", reward
                done = True

            # elif self.simulator.is_any_drone_out_of_bounds():
            #     #print "Drone out of bounds in", num_steps, "steps"
            #     done = True
            elif num_steps >= self.maximum_number_of_steps_before_giving_up:
                print "Aborting! Drone took >=", num_steps, "steps"
                done = True

            num_steps += 1

            if done or num_steps >= max_steps:
                unique, counts = np.unique(self.simulator.map, return_counts=True)
                # First element in counts array is -1 which is our explored tile count
                explored_tiles = counts[0]
                other_tiles = counts[1] if len(counts) > 1 else 0
                total_tiles = explored_tiles + other_tiles
                percentage_explored = (float(explored_tiles) / float(total_tiles)) * 100
                print "\tPercentage explored this episode:", percentage_explored, "%"
                self.agent.end_episode(reward, done)
                break

            action = self.agent.step(reward, self.simulator.map)
        return num_steps

    def _step(self, action):
        """ Repeat one action the appopriate number of times and return
        the summed reward. """
        reward = 0
        for _ in range(self.frame_skip):
            reward += self.simulator.act(action)
        return reward


def main():
    # Setup pygame stuff
    global IS_DISPLAYING
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 24)
    clock = pygame.time.Clock()
    simulator = Simulator(screen)

    # Setup machine learning stuff
    # Taken from run_nature.py Defaults
    network = DeepQLearner(
        WIDTH,  # input_width
        HEIGHT,  # input_height
        len(Simulator.ACTIONS),  # num_actions
        4,  # num_frames
        0.99,  # discount
        0.00025,  # learning_rate
        0.95,  # rho
        0.01,  # rms_epsilon
        0,  # momentum
        1.0,  # clip_delta
        10000,  # freeze_interval
        32,  # batch_size
        'linear',  # network_type
        'sgd',#'deepmind_rmsprop',  # update_rule
        'sum',  # batch_accumulator
        np.random.RandomState(),  # rng
    )

    agent = NeuralAgent(
        network,  # network,
        1.0,  # parameters.epsilon_start,
        0.1,  # parameters.epsilon_min,
        1000000,  # parameters.epsilon_decay,
        1000000,  # parameters.replay_memory_size,
        "plithos_",  # parameters.experiment_prefix,
        50000,  # parameters.replay_start_size,
        4,  # parameters.update_frequency,
        np.random.RandomState(),  # rng
    )

    experiment = PlithosExperiment(
        # ale
        simulator,
        agent,  # agent,
        # WIDTH,  # defaults.RESIZED_WIDTH,
        # HEIGHT,  # defaults.RESIZED_HEIGHT,
        # #,  # parameters.resize_method,
        20,#200,  # parameters.epochs,
        60000,#250000,  # parameters.steps_per_epoch,
        12500,#12500,  # parameters.steps_per_test,
        4,  # parameters.frame_skip,
        # ,  # parameters.death_ends_episode,
        # ,  # parameters.max_start_nullops,
        np.random.RandomState(),  # rng
    )

    print "@" * 80
    print "Begin training..."

    experiment.run()

    print "training completed!"
    print "@" * 80


    # Start with random action
    action = 2









    simulator.reset_game()








    IS_DISPLAYING = True
    WE_FOUND_HIM = False
    CURRENT_SEARCH_STEPS = 0



    while 1:
        for i in pygame.event.get():
            if i.type == pygame.QUIT or (i.type == KEYDOWN and i.key == K_ESCAPE):
                pygame.quit()
                exit()
            elif i.type == KEYDOWN and i.key == K_SPACE:
                WE_FOUND_HIM = False
                CURRENT_SEARCH_STEPS = 0
                simulator.reset_game()

        if not WE_FOUND_HIM:
            reward = experiment._step(experiment.min_action_set[action])

            print "Previous action:", action, simulator.ACTIONS[action], "reward =", reward

            action = experiment.agent.step(reward, experiment.simulator.map) # this sets action for the next time around

            # if simulator.is_any_drone_out_of_bounds():
            #     simulator.reset_game()
            if CURRENT_SEARCH_STEPS > 3000:
                print "Resetting game, reached", CURRENT_SEARCH_STEPS, "steps"
                simulator.reset_game()
                CURRENT_SEARCH_STEPS = 0
            else:
                CURRENT_SEARCH_STEPS += 1

            if simulator.does_any_drone_see_target():
                WE_FOUND_HIM = True

        else:
            print "WE DID IT! Hit space to release the drones again"

        simulator.sprites.clear(screen, simulator.background)
        simulator.sprites.update()
        simulator.screen.blit(simulator.explored_layer, (0, 0))
        simulator.sprites.draw(screen)

        pygame.display.flip()
        clock.tick(10)


if __name__ == '__main__':
    main()
