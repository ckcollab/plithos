import pygame

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

    def __init__(self):
        super(Drone, self).__init__()

        self.image = pygame.Surface((15, 15))
        self.image.set_colorkey((0, 0, 0))
        self.image.fill((0, 0, 0))
        # Drones start in bottom right
        self.rect.center = (
            randint(WIDTH * .9, WIDTH),
            randint(HEIGHT * .9, HEIGHT)
        )

        self.sensor_type = 'visible'
        self.sensor_distance = 5
        #self.sensor = Sensor(self.sensor_distance)

        #pygame.draw.circle(self.image, (255,0,0), (self.rect.x, self.rect.y), self.sensor_distance, 2)
        pygame.draw.rect(self.image, pygame.color.Color('white'), (0, 0, 2, 2), 2)

        # self.sensor_circle = pygame.Surface((5, 5))
        # pygame.draw.circle(self.sensor_circle, (255,0,0), (self.rect.x, self.rect.y), 5, 2)

    # def update(self):
    #     super(Drone, self).update()
    #     #self.sensor_image = pygame.Surface((self.sensor_distance, self.sensor_distance))
    #     pygame.draw.circle(self.image, (255,0,0), (self.rect.x, self.rect.y), 50, 2)


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
        self.drones = [Drone() for _ in range(10)]
        self.objectives = [Objective()]
        #self.sensors = [drone.sensor for drone in self.drones]

    def get_all_entities(self):
        return self.drones + self.objectives # + self.sensors



def main():
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
