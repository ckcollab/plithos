import random
import pygame

from pygame import *

from ..simulator import Simulator


class HandControlled(Simulator):
    ACTIONS = ('up', 'down', 'left', 'right')

    def _check_pygame_events(self):
        for i in pygame.event.get():
            if i.type == pygame.QUIT or (i.type == KEYDOWN and i.key == K_ESCAPE):
                pygame.quit()
                exit()
            elif i.type == KEYDOWN:
                if i.key == K_RIGHT: move = 'right'
                if i.key == K_DOWN: move = 'down'
                if i.key == K_LEFT: move = 'left'
                if i.key == K_UP: move = 'up'

                if move:
                    self.drones[0].do_action(move)
                    self.print_map()
                    print "(%s, %s)" % (self.drones[0].x, self.drones[0].y)

    def start(self):
        self.init_game()

        while True:
            self._check_pygame_events()

            self._draw()
