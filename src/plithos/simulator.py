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
            (self.sensor_radius, self.sensor_radius, 1, 1),
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
            # self.simulator.explored_layer.fill(
            #     Simulator.EXPLORED_MAP_COLOR,
            #     ((x - 1, y - 1), (1, 1))
            # )
            try:
                self.simulator.map[x][y] = Simulator.TILE_EXPLORED
            except IndexError:
                pass

        # mark all drones in case sensor radius overrode their tile
        self.simulator._mark_drone_locations()

    def do_move(self, direction):
        self._move(direction)  # action is a direction here
        self._fill_in_explored_area()

    def is_out_of_bounds(self):
        return self.x < 0 or self.x > self.width or self.y < 0 or self.y >= self.height

    def get_tiles_within_sensor_radius(self, center_x=None, center_y=None):
        center_x = center_x if center_x else self.x
        center_y = center_y if center_y else self.y
        for circle_x, circle_y in circle_iterator(center_x, center_y, self.sensor_radius):
            yield circle_x, circle_y

    def is_an_objective_in_sensor_range(self):
        # Offset our x/y with the sensor radius because the self x/y are the top left of the drone sprite
        for objective in self.simulator.objectives:
            return hypot(
                self.x - objective.x,
                self.y - objective.y,
            ) <= self.sensor_radius


class Objective(Entity):

    def __init__(self, *args, **kwargs):
        '''The random weights are the "weights" for where we will place the objective.

        The default random weights place the objective somewhere in the top left
            (WIDTH * .05, HEIGHT * .05) and (WIDTH * .2, HEIGHT * .2)'''
        start_x = kwargs.pop('start_x', None)
        start_y = kwargs.pop('start_y', None)
        super(Objective, self).__init__(*args, **kwargs)
        self.image.fill(pygame.color.Color('green'))
        if not start_x:
            # Objectives start in top left by default
            self.rect.center = (
                randint(self.map_width * .05, self.map_width * .2),
                randint(self.map_height * .05, self.map_height * .2)
            )
        else:
            self.rect.center = (start_x, start_y)


class Simulator(object):
    EXPLORED_MAP_COLOR = (0, 100, 100)
    TILE_OUT_OF_BOUNDS = None
    TILE_EXPLORED = -1
    TILE_UNEXPLORED = 0
    TILE_DRONE = 1
    TILE_OBJECTIVE = 2
    TILE_SENSOR_RADIUS = 4  # may not be used. could put our sensor radius around the drone in the state map...
                            # but might not be that useful....

    def __init__(self, width=40, height=40, sensor_radius=4, drone_count=1):
        self.screen = pygame.display.set_mode((width, height), 0, 24)
        self.width = width
        self.height = height
        self.default_sensor_radius = sensor_radius
        self.drone_count = drone_count

    def create_objective(self):
        return Objective(self)

    def create_drone(self):
        return Drone(self, sensor_radius=self.default_sensor_radius)

    def init_game(self):
        self.map = np.zeros((self.width, self.height), dtype=np.float16)
        self.drones = [self.create_drone() for _ in range(self.drone_count)]

        self.objectives = [self.create_objective()]

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
        for y in range(self.height):
            new_row = []
            for x in range(self.width):
                tile = self.map[x][y]
                if tile < 0:  # if tile has been explored
                    tile = '*'
                elif tile == 0:
                    tile = '.'  # nicer than big 0
                else:
                    tile = int(tile)  # float to int so it displays nicely
                new_row.append(str(tile))
            print ' '.join(new_row)

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

            # TODO: when we have a decently trained thing to demo
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

    def _decay_map(self):
        # Explored areas will 'decay' back to unexplored eventually by using this function repeatedly
        decay_rate = 0.0005

        it = np.nditer(self.map, op_flags=['readwrite'], flags=['multi_index'])

        import time
        t0 = time.time()

        for y in xrange(self.height):
            for x in xrange(self.width):
                if self.map[x][y] < 0:
                    self.map[x][y] += decay_rate

                    # Tile will be from -1 < 0 so -(-1) * 100 will give us a nice degrading in color
                    weighted_color = (0, int(100 * -self.map[x][y]), int(100 * -self.map[x][y]))

                    self.explored_layer.fill(
                        weighted_color,
                        ((x - 1, y - 1), (1, 1))
                    )

        # while not it.finished:
        #     # tile = it[0]
        #     if it[0] < 0:
        #         it[0] += decay_rate
        #
        #         # Tile will be from -1 < 0 so -(-1) * 100 will give us a nice degrading in color
        #         weighted_color = (0, 100 * -it[0], 100 * -it[0])
        #
        #         self.explored_layer.fill(
        #             weighted_color,
        #             ((it.multi_index[0] - 1, it.multi_index[1] - 1), (1, 1))
        #         )
        #     elif 0 < it[0] < 1:
        #         it[0] = 0  # reset tile to 0 if it ended up being > 0 somehow
        #     it.iternext()

        t1 = time.time()
        total = t1-t0
        #print "Time to decay shit:", total

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
