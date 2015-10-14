import numpy as np
import pygame

from math import hypot
from pygame import *
from random import randint, choice

from utils import circle_iterator


class Entity(pygame.sprite.Sprite):

    def __init__(self, simulator):
        pygame.sprite.Sprite.__init__(self)
        self.simulator = simulator
        self.image = pygame.Surface((2, 2))
        self.rect = self.image.get_rect()
        self.map_width = simulator.width
        self.map_height = simulator.height

    @property
    def x(self):
        return self.rect.center[0]

    @property
    def y(self):
        return self.rect.center[1]


class Drone(Entity):

    def __init__(self, simulator, sensor_type='visible', sensor_radius=4, *args, **kwargs):
        super(Drone, self).__init__(simulator, *args, **kwargs)
        self.sensor_type = sensor_type
        self.sensor_radius = sensor_radius

        # Make the sprite a big enough rectangle to display the sensor distance
        self.image = pygame.Surface((self.sensor_radius * 2, self.sensor_radius * 2))
        self.image.set_colorkey((0, 0, 0))
        self.image.fill((0, 0, 0))

        # Drones start in bottom right
        self.rect.center = (
            randint(self.map_width * .7, self.map_width * .9), #randint(WIDTH * .9, WIDTH),
            randint(self.map_height * .7, self.map_height * .9), #randint(HEIGHT * .9, HEIGHT)
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

    @property
    def x(self):
        return self.rect.center[0] + self.sensor_radius

    @property
    def y(self):
        return self.rect.center[1] + self.sensor_radius

    def _move(self, direction):
        if direction == 'up':
            self.rect.y -= 1
        elif direction == 'down':
            self.rect.y += 1
        elif direction == 'left':
            self.rect.x -= 1
        elif direction == 'right':
            self.rect.x += 1

    def _fill_in_explored_area(self):
        '''Called after executing an action'''
        # Before anything else remove our drone tile from state map
        try:
            self.simulator.map[self.x][self.y] = Simulator.TILE_EXPLORED
        except IndexError:
            pass

        for x, y in self.get_tiles_within_sensor_radius():
            self.simulator.explored_layer.fill(
                Simulator.EXPLORED_MAP_COLOR,
                ((x - 1, y - 1), (1, 1))
            )
            try:
                self.simulator.map[x][y] = Simulator.TILE_EXPLORED
            except IndexError:
                pass

        # mark all drones in case sensor radius overrode their tile
        self.simulator._mark_drone_locations()

    def do_action(self, action):
        self._move(action)  # action is a direction here
        self._fill_in_explored_area()

    def is_out_of_bounds(self):
        return self.x < 0 or self.x > self.width or self.y < 0 or self.y >= self.height

    def get_tiles_within_sensor_radius(self):
        '''Returns (x, y, tile_value)'''
        for circle_x, circle_y in circle_iterator(self.x, self.y, self.sensor_radius):
            yield circle_x, circle_y

    def is_goal_in_sensor_range(self, goal_x, goal_y):
        # Offset our x/y with the sensor radius because the self x/y are the top left of the drone sprite
        return hypot(
            self.x - goal_x,
            self.y - goal_y,
        ) <= self.sensor_radius


class Objective(Entity):

    def __init__(self, *args, **kwargs):
        super(Objective, self).__init__(*args, **kwargs)
        self.image.fill(pygame.color.Color('green'))
        # Objectives start in top left
        self.rect.center = (
            randint(self.map_width * .05, self.map_width * .2),
            randint(self.map_height * .05, self.map_height * .2)
        )


class Simulator(object):
    EXPLORED_MAP_COLOR = (0, 100, 100)
    TILE_OUT_OF_BOUNDS = None
    TILE_EXPLORED = -1
    TILE_UNEXPLORED = 0
    TILE_DRONE = 1
    TILE_OBJECTIVE = 2
    TILE_SENSOR_RADIUS = 4  # may not be used. could put our sensor radius around the drone in the state map...
                            # but might not be that useful....

    def __init__(self, width=40, height=40, sensor_radius=4):
        self.screen = pygame.display.set_mode((width, height), 0, 24)
        self.width = width
        self.height = height
        self.default_sensor_radius = sensor_radius

    def init_game(self):
        self.map = np.zeros((self.width, self.height), dtype=np.int)
        self.drones = [Drone(self, sensor_radius=self.default_sensor_radius) for _ in range(1)]  # limit to 1 drone for now
        self.objectives = [Objective(self)]

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
        for entity in self.drones + self.objectives:
            self.sprites.add(entity)

    def print_map(self):
        '''Print out map in ASCII'''
        for row in self.map:
            new_row = []
            for i in row:
                if i == Simulator.TILE_EXPLORED:
                    i = '*'
                new_row.append(str(i))
            print ''.join(new_row)

    def _check_pygame_events(self):
        for i in pygame.event.get():
            if i.type == pygame.QUIT or (i.type == KEYDOWN and i.key == K_ESCAPE):
                pygame.quit()
                exit()
            # elif i.type == KEYDOWN:
            #     if i.key == K_RIGHT: move = 'right'
            #     if i.key == K_DOWN: move = 'down'
            #     if i.key == K_LEFT: move = 'left'
            #     if i.key == K_UP: move = 'up'
            #
            #     if move:
            #         self.drones[0].do_action(move)

            # TODO: when we have a decently trained
            # elif i.type == KEYDOWN and i.key == K_SPACE:
            #     WE_FOUND_HIM = False
            #     CURRENT_SEARCH_STEPS = 0
            #     simulator.reset_game()
            #     simulator.turn_on_drawing()

    def _draw(self):
        self.sprites.clear(self.screen, self.background)
        self.sprites.update()
        self.screen.blit(self.explored_layer, (0, 0))
        self.sprites.draw(self.screen)

        pygame.display.flip()

    def _mark_drone_locations(self):
        for drone in self.drones:
            try:
                self.map[drone.x][drone.y] = Simulator.TILE_DRONE
            except IndexError:
                pass

    def start(self):
        self.init_game()

        clock = pygame.time.Clock()

        while True:
            self._check_pygame_events()

            #import random
            #self.drones[0].do_action(random.choice(['up', 'down', 'left', 'right']))

            self._draw()

            clock.tick(10)
