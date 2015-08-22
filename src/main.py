import pygame

from pygame import *

from random import randint


WIDTH = 500
HEIGHT = 500


class Entity(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((2, 2))
        self.rect = self.image.get_rect()

    @property
    def x(self):
        return self.rect.x

    @property
    def y(self):
        return self.rect.y


class Drone(Entity):

    def __init__(self):
        super(Drone, self).__init__()
        self.image.fill(pygame.color.Color('white'))
        # Drones start in bottom right
        self.rect.center = (
            randint(WIDTH * .9, WIDTH),
            randint(HEIGHT * .9, HEIGHT)
        )


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

    def get_all_entities(self):
        return self.drones + self.objectives



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

        for drone in simulator.drones:
            drone.rect.x += randint(-1, 1)
            drone.rect.y += randint(-1, 1)


        # following the CUD Rule (Clear, Update, Draw)
        sprites.clear(screen, background)
        sprites.update()
        sprites.draw(screen)
        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()
