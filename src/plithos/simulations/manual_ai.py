import math
import random
import pygame
from pygame import *
from sys import maxsize

from ..simulator import Simulator, Drone, Objective


class SearchDrone(Drone):

    MOVES = (
        # (direction, x offset, y offset)
        ('up', 0, -1),
        ('down', 0, 1),
        ('left', -1, 0),
        ('right', 1, 0),
    )

    def __init__(self, *args, **kwargs):
        super(SearchDrone, self).__init__(*args, **kwargs)
        self.score = 0










    # Let's change things.
    #
    # First let's split the map up based on sensor radius. Then let's score each tile. Tile size
    # is width=sensor_radius height=sensor_radius for smallest sensor.
    #
    # if not has_next_move():
    #   area = find_best_area()
    #   generate_moves_to_area(area)
    # else:
    #   do_next_move()
    #
    #
    # find_best_area function will score the areas based on distance from you and how recently they were explored.







    def do_best_move(self):
        # Start with random move
        best_move = None
        best_score = 0
        for move, offset_x, offset_y in self.MOVES:
            score = self.get_move_score(offset_x, offset_y)
            if score > best_score:
                best_move = move
                best_score = score

        #print "Doing move", best_move, "with score =", best_score
        self.do_move(best_move)


    # Best move version that searches over a large distance
    #
    # def do_best_move(self):
    #     # Start with random move
    #     best_move = None
    #     best_score = 30#-maxsize
    #     search_distance = 0
    #     max_search_distance = 50
    #     while best_move is None and search_distance < max_search_distance:
    #         search_distance += 1
    #         # Look for the best move while searching further and further until we find a decent direction
    #         for move, offset_x, offset_y in self.MOVES:
    #             score = self.get_move_score(offset_x * search_distance, offset_y * search_distance)
    #             if score > best_score:
    #                 best_move = move
    #                 best_score = score
    #     #print "Doing move", best_move, "with score =", best_score
    #     self.do_move(best_move)

    # Best move that searches only the immediate move options
    #
    # def do_best_move(self):
    #     # Start with random move
    #     best_move = None
    #     best_score = 0
    #     for move, offset_x, offset_y in self.MOVES:
    #         score = self.get_move_score(offset_x, offset_y)
    #         if score > best_score:
    #             best_move = move
    #             best_score = score
    #     #print "Doing move", best_move, "with score =", best_score
    #     self.do_move(best_move)

    def get_move_score(self, offset_x, offset_y):
        score = 0
        for x, y in self.get_tiles_within_sensor_radius(center_x=self.x + offset_x, center_y=self.y + offset_y):
            try:
                if not(0 < x <= self.simulator.width and 0 < y <= self.simulator.height):
                    # Huge negative for going out of bounds
                    score -= 100
                elif 0 <= self.simulator.map[x][y] <= 1:
                    # Unexplored tiles that are at 0 will now
                    score += (self.simulator.map[x][y]) + 1
                elif self.simulator.map[x][y] < 0:
                    # Explored tiles are -1 < 0 so decay the tiles from -1 (explored) to 0 (unexplored).
                    # We should be guided back to areas we haven't explored in a while
                    score += math.exp(self.simulator.map[x][y]) / 2
                elif self.simulator.map[x][y] == Simulator.TILE_DRONE:
                    # We're close to another drone, move away
                    score -= 1
            except IndexError:
                pass
        return score


class ManualAIExperiment(Simulator):

    def create_objective(self):
        return Objective(
            self,
            start_x=random.randint(self.width * .05, self.width * .7),
            start_y=random.randint(self.height * .05, self.height * .7)
        )

    def create_drone(self):
        # Custom drone creation
        return SearchDrone(self, sensor_radius=self.default_sensor_radius)

    def start(self):
        self.init_game()

        counter = 0
        found = False

        while True:
            counter += 1
            self._check_pygame_events()

            if not found:
                for drone in self.drones:
                    drone.do_best_move()
                    if drone.is_an_objective_in_sensor_range():
                        print "Found ya buddy!!"
                        found = True

                self.apply_map_decay()
                if (counter % 50) == 0:
                    self.apply_map_gravity()

            self._draw()
