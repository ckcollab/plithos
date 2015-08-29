import logging
import numpy as np
import pygame

from convnetpy2.convnet import Trainer
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


class Drone(Entity):

    def __init__(self, simulator, sensor_type='visible', sensor_radius=6):
        super(Drone, self).__init__()
        self.simulator = simulator
        self.sensor_type = sensor_type
        self.sensor_radius = sensor_radius

        # Keeping track of distance from target search area
        self.goal_last_seen_x = WIDTH * 0.05
        self.goal_last_seen_y = HEIGHT * 0.05
        self._old_distance_from_target_area = 0
        self.current_distance_from_target_area = 0

        # Make the sprite a big enough rectangle to display the sensor distance
        self.image = pygame.Surface((self.sensor_radius * 2, self.sensor_radius * 2))
        self.image.set_colorkey((0, 0, 0))
        self.image.fill((0, 0, 0))
        # Drones start in bottom right
        self.rect.center = (
            randint(WIDTH * .8, WIDTH), #randint(WIDTH * .9, WIDTH),
            randint(HEIGHT * .8, HEIGHT), #randint(HEIGHT * .9, HEIGHT)
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

    def _get_current_reward(self):
        '''Reward system:
            - +1 for each unexplored tile
            - -5 for each drone next to you
            - +1 if new position is closer to target'''
        reward = 0

        # Are we closer?
        if self.current_distance_from_target_area < self._old_distance_from_target_area:
            reward += 1

        # How many tiles in our sensor radius are unexplored?
        for _, _, tile in self.get_tiles_within_sensor_radius():
            if tile == 0:
                reward += 0.5

        # If we go out of bounds really remove a lot of points
        if self.x < 5 or self.x > WIDTH - 5 or self.y < 5 or self.y > HEIGHT - 5:
            reward -= 5

        # print "self x/y:", self.x, self.y
        # print "center x/y:", self.rect.center[0], self.rect.center[1]
        # print "current reward: ", reward
        self.reward = reward

    def _fill_in_explored_area(self):
        for x, y, tile in self.get_tiles_within_sensor_radius():
            # If the tile has not been explored and isn't a drone/objective (1/2), mark it as explored
            if tile <= 0:
                # Mark our old tile as explored (-1 is explored)
                try:
                    self.simulator.map[x][y] = -1
                except IndexError:
                    pass
                # Put a pixel at the explored tile
                if IS_DISPLAYING:
                    self.simulator.explored_layer.fill(
                        Simulator.EXPLORED_MAP_COLOR,
                        ((x, y), (1, 1))
                    )

    def do_action(self, action):
        '''Move to the new tile but record old reward and get new one. Also mark explored tiles.

        action is a direction from Simulator.ACTIONS'''
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

        # Mark explored tiles; but, before marking them check what our reward was
        self._get_current_reward()
        self._fill_in_explored_area()

    def get_tiles_within_sensor_radius(self):
        '''Returns (x, y, tile_value)'''
        center_x, center_y = self.rect.center
        for circle_x, circle_y in circle_iterator(center_x, center_y, self.sensor_radius):
            try:
                yield circle_x + self.sensor_radius, \
                      circle_y + self.sensor_radius, \
                      self.simulator.map[circle_x + self.sensor_radius][circle_y + self.sensor_radius]
            except IndexError:
                pass

    def is_goal_in_range(self, goal_x, goal_y):
        return hypot(
            self.x - goal_x,
            self.y - goal_y,
        ) <= self.sensor_radius



class Objective(Entity):
    def __init__(self):
        super(Objective, self).__init__()
        self.image.fill(pygame.color.Color('green'))
        # Drones start in top left
        self.rect.center = (
            randint(0, WIDTH * .1),
            randint(0, HEIGHT * .1)
        )


class Simulator(object):
    ACTIONS = ('up', 'left', 'down', 'right')
    EXPLORED_MAP_COLOR = (0, 100, 100)

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
            - 2 is the objective
            - < 0 is explored, but updated each tick. So -1 was just explored, -0.99 was explored 1 tick ago..
                  something like that
        '''
        self.map = np.zeros((WIDTH, HEIGHT), dtype=np.int)

        try:
            for drone in self.drones:
                self.map[drone.x][drone.y] = 1
            for objective in self.objectives:
                self.map[objective.x][objective.y] = 2
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

    def is_game_over(self):
        for drone in self.drones:
            if drone.is_goal_in_range(self.objectives[0].x, self.objectives[0].y):
                return True
        return False


def main():
    # Setup pygame stuff
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 24)
    clock = pygame.time.Clock()
    simulator = Simulator(screen)



    brain = Trainer(
        WIDTH * HEIGHT, # number of states
        len(Simulator.ACTIONS),
        opt={

        }
    )

    simulator.reset_game()

    # for _ in range(1000):
    #     action = brain.forward(simulator.map)
    #     reward = simulator.drones[0].reward
    #     brain.backward(reward)






    #simulator.reset_game()
    #import ipdb;ipdb.set_trace()
    IS_DISPLAYING = True









    while 1:
        for i in pygame.event.get():
            if i.type == pygame.QUIT or (i.type == KEYDOWN and i.key == K_ESCAPE):
                pygame.quit()
                exit()


        #
        # for drone in simulator.drones:
        #     # [up, down, left, right]
        #     # unexplored [0, 0, 0, 0]
        #     # explored [1, 1, 1, 1]
        #     # input is: [
        #     #     is explored [up, down, left, right],
        #     #     sensor_found_objective [0, 1]
        #     #     angle_to_goal_area [0-360]
        #     #
        #     # output is 'up', 'down', 'left', 'right'
        #     classifier.partial_fit(state, decision, classes=('up', 'down', 'left', 'right'))



        # for drone in simulator.drones:
        #     pygame.draw.circle(screen, pygame.color.Color('blue'), (drone.rect.x, drone.rect.y), 50, 2)


        # Randomly moving
        # for drone in simulator.drones:
        #     # drone.rect.x += randint(-1, 1)
        #     # drone.rect.y += randint(-1, 1)
        #     drone.do_action(choice(Simulator.ACTIONS))

        #action = self.agent.step(reward, simulator.map)
        # reward = experiment._step(experiment.min_action_set[action])
        #
        # print "Previous action:", action, simulator.ACTIONS[action], "reward =", reward
        #
        # action = experiment.agent.step(reward, experiment.simulator.map) # this sets action for the next time around


        # for _ in range(1000):
        action = brain.forward(simulator.map)
        print "Doing action:", action
        simulator.act(action)
        reward = simulator.drones[0].reward
        brain.backward(reward)





        simulator.sprites.clear(screen, simulator.background)
        simulator.sprites.update()
        simulator.screen.blit(simulator.explored_layer, (0, 0))
        simulator.sprites.draw(screen)

        pygame.display.flip()
        clock.tick(10)


if __name__ == '__main__':
    main()
