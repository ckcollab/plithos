import numpy as np
import pygame

from math import hypot
from pygame import *
from random import randint

from vec2d import Vec2d


WIDTH = 500
HEIGHT = 500


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
        return self.rect.x

    @property
    def y(self):
        return self.rect.y

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

    def __init__(self, simulator, sensor_type='visible', sensor_distance=8):
        super(Drone, self).__init__()
        self.simulator = simulator
        self.sensor_type = sensor_type
        self.sensor_distance = sensor_distance

        # Make the sprite a big enough rectangle to display the sensor distance
        self.image = pygame.Surface((self.sensor_distance * 2, self.sensor_distance * 2))
        self.image.set_colorkey((0, 0, 0))
        self.image.fill((0, 0, 0))
        # Drones start in bottom right
        self.rect.center = (
            randint(WIDTH * .9, WIDTH),
            randint(HEIGHT * .9, HEIGHT)
        )

        # self.sensor_distance is
        pygame.draw.circle(
            self.image,
            (100, 0, 0),  # light red color
            (self.sensor_distance, self.sensor_distance),  # center of circle ??
            self.sensor_distance,  # radius for the circle
            1
        )

        # Place the rectangle in the middle, -1 sensor distance so it is right in the center instead of offset
        # to the bottom right
        pygame.draw.rect(
            self.image,
            pygame.color.Color('white'),
            (self.sensor_distance - 1, self.sensor_distance - 1, 1, 1),
            1
        )

    @property
    def state(self):
        '''Returns the area around the drone starting from the top left, skipping drones location, and
        continues to the bottom right. Also, appends the distance to the target area as the last
        element in the state list.'''
        state = []
        for x in range(-1, 2):
            for y in range(-1, 2):
                if x == 0 and y == 0:
                    continue  # skip our location
                print x, ",", y
                state.append(self.simulator.map[self.x + x][self.y + y])

        # Also append distance to where goal was last seen
        goal_last_seen_x = WIDTH * 0.05
        goal_last_seen_y = HEIGHT * 0.05
        state.append(hypot(goal_last_seen_x - self.x, goal_last_seen_y - self.y))
        return state


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

    def __init__(self):
        self.drones = [Drone(self) for _ in range(10)]
        self.objectives = [Objective()]
        #self.sensors = [drone.sensor for drone in self.drones]
        #self.map = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.update_map()

    def get_all_entities(self):
        return self.drones + self.objectives # + self.sensors

    def update_map(self):
        '''
        Sets self.map points where drones/objectives exist.

        A drone is a 1, an objective is a 2, 0 is nothing, -1 is explored
        '''
        self.map = np.zeros((WIDTH, HEIGHT), dtype=np.int)
        for drone in self.drones:
            self.map[drone.x, drone.y] = 1

        for objective in self.objectives:
            self.map[objective.x, objective.y] = 2



def main():
    # Setup pygame stuff
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 24)
    clock = pygame.time.Clock()
    simulator = Simulator()
    sprites = pygame.sprite.Group()
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))  # black
    screen.blit(background, (0, 0))

    for entity in simulator.get_all_entities():
        sprites.add(entity)

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
        for drone in simulator.drones:
            drone.rect.x += randint(-1, 1)
            drone.rect.y += randint(-1, 1)






        # Inputs:
        # Sensor data, 1 input binary: was something found?
        # Area data, 4 input directions: in each direction, is it explored?
        #










        # Moving with acceleration
        # dt = float(clock.get_time()) / 100
        # print dt
        # for drone in simulator.drones:
        #     drone.rect.x += drone.velocity_x * dt
        #     drone.rect.y += drone.velocity_y * dt
        #     drone.velocity_x += drone.acceleration_x * dt
        #     drone.velocity_y += drone.acceleration_y * dt
            # drone.acceleration_x -= drone.friction
            # drone.acceleration_y -= drone.friction

            # drone.rect.x += drone.velocity_x
            # drone.rect.y += drone.velocity_y
            #
            # if drone.velocity_x > 0:
            #     drone.velocity_x = drone.velocity_x - drone.friction
            # else:
            #     drone.velocity_x = drone.velocity_x + drone.friction
            #
            # if drone.velocity_y > 0:
            #     drone.velocity_y = drone.velocity_y - drone.friction
            # else:
            #     drone.velocity_y = drone.velocity_y + drone.friction


        # following the CUD Rule (Clear, Update, Draw)
        background.fill((0, 0, 0))  # black
        sprites.clear(screen, background)
        sprites.update()
        sprites.draw(screen)
        pygame.display.flip()
        clock.tick(30)


if __name__ == '__main__':
    main()
