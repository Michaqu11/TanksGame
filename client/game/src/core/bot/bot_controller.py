import sys
from enum import Enum
from heapq import *
from math import cos, sin, pi, sqrt, tan, nan
import random

import pygame
import copy

from client.game.src.core.bot.a_star import A_Star
from client.game.src.core.bot.maze import Maze, path_from
from client.game.src.core.stat_bar.stat_bar import StatBar
from client.game.src.utils.config import Config

class Drive(Enum):
    FORWARD = 0
    BACKWARD = 1


class Rotate(Enum):
    LEFT = 0
    RIGHT = 1


class ExpectRotate(float, Enum):
    UP = 270
    DOWN = 90
    LEFT = 180
    RIGHT = 0


class DirectionAngle(float, Enum):
    UP = 90
    DOWN = 270
    LEFT = 180
    RIGHT = 0


class BotController:
    SHOT_DISTANCE = 30
    ANGLE_OFFSET = 10
    POS_OFFSET = 20
    COLISION_OFFSET = 10
    DETECTION_OFFSET = 30
    FLEE_ANGLE = 70
    DISTANCE_OFFSET = 15
    ANGLE_SENSITIVITY = 30


    def __init__(self, screen, game, player, id):
        self.id = id
        self.screen = screen
        self.game = game
        self.player = player
        self.map = self.read_map(game.map.data)
        self.node = None
        self.x = 0
        self.y = 0
        self.glitch_time = 0
        self.flee_timer = 0
        self.flee_dir = 0
        self.last_bullet_angle = 0
        self.enemy = None

    def distance(self, player):
        return abs(self.player.position[0] - player.position[0]) + abs(self.player.position[1] - player.position[1])

    def set_enemy(self):
        self.enemy = self.find_closest_player()

    def find_closest_player(self):
        minDistance = sys.maxsize
        minPlayer = None

        for player in self.game.players:
            if player != self.player:
                if minDistance > self.distance(player):
                    minDistance = self.distance(player)
                    minPlayer = player
        return minPlayer

    def read_map(self, map):
        # for i in range(len(map)):
        #     print(map[i])
        for i in range(len(map)):
            map[i] = list(map[i])
            for j in range(len(map[i])):
                if map[i][j] == 'S':
                    map[i][j] = '.'

        return map

    def astar(self, maze):
        start_node = maze.find_node('S')
        self.node = (start_node.x, start_node.y)
        start_node.visited = True
        end_node = maze.find_node('E')
        start_node.cost = abs(end_node.x - start_node.x) + abs(end_node.y - start_node.y)
        q = []
        id = 0
        heappush(q, (start_node.cost, id, start_node))
        while q:
            node = heappop(q)[2]  # LIFO
            node.visited = True
            if node.type == 'E':
                return path_from(node)

            children = maze.get_possible_movements(node)
            for child in children:
                if not child.visited:
                    child.parent = node
                    child.moves_cost = node.moves_cost + maze.move_cost(child)
                    child.cost = abs(end_node.x - child.x) + abs(end_node.y - child.y) + child.moves_cost
                    id += 1
                    heappush(q, (child.cost, id, child))

        return None

    def find_path(self):
        # player = self.find_closest_player()  # gdyby bylo wiecej graczy trzeba uzywac tej metody
        player = self.enemy
        new_map = copy.deepcopy(self.map)
        width = self.game.assets.width
        height = self.game.assets.height

        self.x = int(self.player.position[0] / width)
        self.y = int(self.player.position[1] / height)

        new_map[self.y][self.x] = 'S'
        x2 = int(player.position[0] / width)
        y2 = int(player.position[1] / height)
        new_map[y2][x2] = 'E'

        if (self.x, self.y) == (x2, y2):
            return None, None, 0
        maze = Maze(new_map)
        maze.path = self.astar(maze)
        # maze.draw()

        act = maze.path[len(maze.path) - 1]
        new = maze.path[len(maze.path) - 2]
        return (act.x, act.y), (new.x, new.y), len(maze.path)

    def move(self):
        if self.enemy.is_alive():
            actual_point, new_point, length = self.find_path()
            if actual_point:
                if actual_point[1] < new_point[1]:
                    return length, ExpectRotate.UP
                if actual_point[1] > new_point[1]:
                    return length, ExpectRotate.DOWN
                if actual_point[0] < new_point[0]:
                    return length, ExpectRotate.RIGHT
                if actual_point[0] > new_point[0]:
                    return length, ExpectRotate.LEFT
        return 0, self.player.angle  # stay

    def diagonal_distance(self):
        """
        :return: diagonal distance between bot and an enemy.
        :rtype: float
        """
        e_x, e_y = self.enemy.position
        b_x, b_y = self.player.position
        return sqrt(pow(b_x - e_x, 2) + pow(b_y - e_y, 2))

    def checkMove(self, directory, pos):
        # for i in range(len(self.map)):
        #   print(self.map[i])

        if directory == DirectionAngle.DOWN and self.map[pos[1] + 1][pos[0]] != "#":
            return True
        elif directory == DirectionAngle.UP and self.map[pos[1] - 1][pos[0]] != "#":
            return True
        elif directory == DirectionAngle.RIGHT and self.map[pos[1]][pos[0] + 1] != "#":
            return True
        elif directory == DirectionAngle.LEFT and self.map[pos[1]][pos[0] - 1] != "#":
            return True

        return False

    @property
    def move2(self):
        moves = []
        self.actual_pos = ""
        if self.enemy.is_alive():
            self.actual_pos, new_point, length = self.find_path()
            if self.actual_pos:
                moves = [DirectionAngle.DOWN, DirectionAngle.UP, DirectionAngle.RIGHT, DirectionAngle.LEFT]
                opponent_possition = None
                if (self.actual_pos[1] < new_point[1]):
                    opponent_possition = DirectionAngle.DOWN
                elif (self.actual_pos[1] > new_point[1]):
                    opponent_possition = DirectionAngle.UP
                elif (self.actual_pos[0] < new_point[0]):
                    opponent_possition = DirectionAngle.RIGHT
                elif (self.actual_pos[0] > new_point[0]):
                    opponent_possition = DirectionAngle.LEFT

                # print("oppo:", opponent_possition)
                moves.remove(opponent_possition)
                for move in moves:
                    if not self.checkMove(move, self.actual_pos):
                        moves.remove(move)

                if len(moves) == 0 and self.checkMove(opponent_possition, self.actual_pos):
                    moves.append(opponent_possition)

        if len(moves):
            # print(self.actual_pos, new_point, moves, self.player.angle, self.player.lastMove)
            for angle in moves:
                # if self.lastMove and ((angle - 1 < self.lastMove < angle + 1) or (angle == DirectionAngle.RIGHT and 359 < self.lastMove < 361)):  # stay
                if self.player.lastMove != None and angle == self.player.lastMove and self.checkMove(self.player.lastMove, self.actual_pos):
                    return length, self.player.lastMove

            r = random.randrange(0, len(moves), 1)
            self.player.lastMove = moves[r]
            # print("a? ", moves[r])
            return length, moves[r]
        # print("C")
        self.player.lastMove = self.player.angle
        return 0, self.player.angle  # stay

    def shot_condition(self, length):
        """
        Checks if enemy is in a straight line with a bot and if bot faces the enemy.
        :param int length: Length of a shortest path between bot and an enemy in a number of tiles.
        :return: If bot is supposed to shot.
        :rtype: bool
        """
        if self.enemy.is_alive():
            e_x, e_y = self.enemy.position
            b_x, b_y = self.player.position
            b_angle = self.player.angle
            width = self.game.assets.width
            height = self.game.assets.height
            tile_size = (width + height) / 2
            if length - 1 <= self.diagonal_distance() / tile_size:
                if b_x - self.POS_OFFSET <= e_x <= b_x + self.POS_OFFSET:
                    # enemy above
                    if b_y > e_y:
                        if DirectionAngle.UP - self.ANGLE_OFFSET <= b_angle <= DirectionAngle.UP + self.ANGLE_OFFSET:
                            return True
                    # enemy below
                    if b_y < e_y:
                        if DirectionAngle.DOWN - self.ANGLE_OFFSET <= b_angle <= DirectionAngle.DOWN + self.ANGLE_OFFSET:
                            return True
                elif b_y - self.POS_OFFSET <= e_y <= b_y + self.POS_OFFSET:
                    # enemy on a left
                    if b_x > e_x:
                        if DirectionAngle.LEFT - self.ANGLE_OFFSET <= b_angle <= DirectionAngle.LEFT + self.ANGLE_OFFSET:
                            return True
                    # enemy on a right
                    if b_x < e_x:
                        if DirectionAngle.RIGHT - self.ANGLE_OFFSET <= b_angle <= DirectionAngle.RIGHT + self.ANGLE_OFFSET:
                            return True
        return False

    @staticmethod
    def whole_angle(angle):
        """
        Check which angle from {0, 90, 180, 270} is closest to the given one.
        :param float angle:
        :return: angle from a range of {0, 90, 180, 270}.
        :rtype: float
        """
        if 45 < angle <= 135:
            return 90
        elif 135 < angle <= 225:
            return 180
        elif 225 < angle <= 315:
            return 270
        else:
            return 0

    def on_trajectory(self, bullet):
        """
        Checks if bot is on the bullet whole trajectory, including the one behind it.
        :param bullet: Bullet Object
        :return: If bot is on the bullet trajectory. If yes also bullet angle.
        :rtype: bool, float
        """
        bullet_x, bullet_y = bullet.position
        bot_x, bot_y = self.player.position
        offset = 2
        if 90 - offset <= bullet.angle <= 90 + offset:
            hit_x = bullet_x
            hit_y = bot_y
        elif 0 <= bullet.angle <= offset or 360 - offset <= bullet.angle <= 360:
            hit_x = bot_x
            hit_y = bullet_y
        elif 270 - offset <= bullet.angle <= 270 + offset:
            hit_x = bullet_x
            hit_y = bot_y
        elif 180 - offset <= bullet.angle <= 180 + offset:
            hit_x = bot_x
            hit_y = bullet_y
        else:
            bullet_a = tan(-bullet.angle * pi / 180)
            bullet_b = bullet_y - (bullet_a * bullet_x)

            bot_a = - 1 / bullet_a if bullet_a else - 1 / pow(10, -20)
            bot_b = bot_y - (bot_a * bot_x)

            hit_x = (bot_b - bullet_b) / (bullet_a - bot_a) if bullet_a - bot_a else (bot_b - bullet_b) / pow(10, -20)
            hit_y = (bullet_a * hit_x) + bullet_b

        dist = sqrt(pow(bot_x - hit_x, 2) + pow(bot_y - hit_y, 2))

        if dist < self.DETECTION_OFFSET:
            return True, bullet.angle
        return False, None
        # return True, object.angle

    def at_gunpoint(self):
        """
        Check if bot might get hit by any bullet on a map except his.
        :return: If bot might get hit if not moved. If yes also bullet angle.
        :rtype: bool, float
        """
        for bullet in self.game.bullet_controller.bullets:
            if bullet.player.id != self.player.id:

                bullet_x, bullet_y = bullet.position
                bot_x, bot_y = self.player.position
                if bullet_x < bot_x - self.DETECTION_OFFSET and 90 <= bullet.angle <= 270:
                    # print("x< ", self.id)
                    continue
                elif bullet_x > bot_x + self.DETECTION_OFFSET and (
                        0 <= bullet.angle <= 90 and 270 <= bullet.angle <= 360):
                    # print("x> ", self.id)
                    continue
                elif bullet_y < bot_y - self.DETECTION_OFFSET and 0 <= bullet.angle <= 180:
                    # print("y< ", self.id)
                    continue
                elif bullet_y > bot_y + self.DETECTION_OFFSET and 180 <= bullet.angle <= 360:
                    # print("y> ", self.id)
                    continue
                else:
                    # print("check")
                    endangered, angle = self.on_trajectory(bullet)
                    if endangered:
                        return endangered, angle
        return False, None

    def paul(self, time):
        if self.player.is_alive():
            flee, bullet_angle = self.at_gunpoint()
            if self.flee_timer <= 0 or flee:
                self._reload(time)
                length, rotate = self.move()
                shot = self.shot_condition(length)
                angle = self.player.angle - rotate
                width = self.game.assets.width
                height = self.game.assets.height

                if self.player.angle > 180 and rotate == DirectionAngle.RIGHT:
                    angle = angle - 360
                elif self.player.angle <= 0 and rotate == DirectionAngle.DOWN:
                    angle = (360 + angle)

                if angle != 0 and (-1 < self.player.angle < 1 and self.x * width > self.player.position[0] - width / 2
                                   or 179 < self.player.angle < 181 and self.player.position[0] > (
                                           self.x + 1) * width - width / 2
                                   or 269 < self.player.angle < 271 and self.y * height >= self.player.position[
                                       1] - height / 2
                                   or 89 < self.player.angle < 91 and self.player.position[1] > (
                                           self.y + 1) * height - height / 2)\
                                   or 359 < self.player.angle < 361 and self.player.position[0] > (
                                           self.x + 1) * width - width / 2:
                    angle = 0

                if shot:
                    self.shot()

                move_value = 0
                if flee:
                    self.last_bullet_angle = bullet_angle
                    self.flee_timer = 20
                    rev_b_angle = (bullet_angle + 180) % 360
                    if rev_b_angle - self.FLEE_ANGLE <= self.player.angle <= rev_b_angle + self.FLEE_ANGLE:
                        if self.flee_dir:
                            self.rotate(Rotate.LEFT, 3 * time)
                        else:
                            self.rotate(Rotate.RIGHT, 3 * time)
                        self.drive(Drive.BACKWARD, time)
                    else:
                        self.drive(Drive.BACKWARD, time)
                elif self.glitch_time < 0:
                    self.drive(Drive.BACKWARD, time)
                    if self.flee_dir:
                        self.rotate(Rotate.LEFT, time / 2)
                    else:
                        self.rotate(Rotate.LEFT, time / 2)
                    move_value = 1
                elif angle > 1:
                    self.rotate(Rotate.RIGHT, time)
                elif angle < -1:
                    self.rotate(Rotate.LEFT, time)
                else:
                    self.flee_dir = 0 if self.flee_dir else 1
                    self.player.rotate(self.whole_angle(self.player.angle) - self.player.angle, time)
                    b_x, b_y = self.player.position
                    e_x, e_y = self.enemy.position
                    re_angle = (self.enemy.angle + 180) % 360
                    dist_offset = self.DISTANCE_OFFSET
                    ang_offset = self.ANGLE_SENSITIVITY
                    # bot and enemy facing each other and on the +/- same x position
                    if re_angle - ang_offset <= self.player.angle <= re_angle + ang_offset and \
                            e_x - dist_offset <= b_x <= e_x + dist_offset and \
                            e_y - self.COLISION_OFFSET <= b_y <= e_y + self.COLISION_OFFSET:
                        if length <= 3 and \
                                (90 - ang_offset <= re_angle <= 90 + ang_offset or \
                                270 - ang_offset <= re_angle <= 270 + ang_offset):
                            move_value = -10
                        else:
                            move_value = self.drive(Drive.FORWARD, time)
                    # bot and enemy facing each other and on the +/- same y position
                    elif re_angle - ang_offset <= self.player.angle <= re_angle + ang_offset and \
                            e_y - dist_offset <= b_y <= e_y + dist_offset and \
                            e_x - self.COLISION_OFFSET <= b_x <= e_x + self.COLISION_OFFSET:
                        if length <= 3 and \
                                (0 <= re_angle <= ang_offset or 360 - ang_offset <= re_angle <= 360 or \
                                180 - ang_offset <= re_angle <= 180 + ang_offset):
                            move_value = -10
                        else:
                            move_value = self.drive(Drive.FORWARD, time)
                    # bot or enemy is turned to the other one in a 90 degree angle
                    elif re_angle + 90 - ang_offset <= self.player.angle <= re_angle + 90 + ang_offset or \
                          re_angle - 90 - ang_offset <= self.player.angle <= re_angle - 90 + ang_offset: \
                        move_value = self.drive(Drive.FORWARD, time)
                    elif length > 2:
                        move_value = self.drive(Drive.FORWARD, time)
                    else:
                        move_value = -10 - random.randrange(10)
                self.glitch_time += move_value
                if self.glitch_time >= 100:
                    self.glitch_time = -40 + random.randrange(10)
                elif move_value == 0:
                    self.glitch_time = 0
            else:
                shot = self.shot_condition(1)
                self.flee_timer -= 1

    def piotrek(self, time):
        if self.player.is_alive():
            self._reload(time)
            length, rotate = self.move()
            shot = self.shot_condition(length)
            angle = self.player.angle - rotate
            width = self.game.assets.width
            height = self.game.assets.height

            if self.player.angle > 180 and rotate == DirectionAngle.RIGHT:
                angle = angle - 360
            elif self.player.angle <= 0 and rotate == DirectionAngle.DOWN:
                angle = (360 + angle)

            if angle != 0 and (-1 < self.player.angle < 1 and self.x * width > self.player.position[0] - width / 2
                               or 179 < self.player.angle < 181 and self.player.position[0] > (
                                       self.x + 1) * width - width / 2
                               or 269 < self.player.angle < 271 and self.y * height >= self.player.position[
                                   1] - height / 2
                               or 89 < self.player.angle < 91 and self.player.position[1] > (
                                       self.y + 1) * height - height / 2)\
                               or 359 < self.player.angle < 361 and self.player.position[0] > (
                                       self.x + 1) * width - width / 2:
                angle = 0

            if shot:
                self.shot()

            move_value = 0
            if self.glitch_time < 0:
                self.drive(Drive.BACKWARD, time)
                if self.flee_dir:
                    self.rotate(Rotate.LEFT, time / 2)
                else:
                    self.rotate(Rotate.LEFT, time / 2)
                move_value = 1
            elif angle > 1:
                self.rotate(Rotate.RIGHT, time)
            elif angle < -1:
                self.rotate(Rotate.LEFT, time)
            else:
                self.flee_dir = 0 if self.flee_dir else 1
                self.player.rotate(self.whole_angle(self.player.angle) - self.player.angle, time)
                b_x, b_y = self.player.position
                e_x, e_y = self.enemy.position
                re_angle = (self.enemy.angle + 180) % 360
                dist_offset = self.DISTANCE_OFFSET
                ang_offset = self.ANGLE_SENSITIVITY
                # bot and enemy facing each other and on the +/- same x position
                if re_angle - ang_offset <= self.player.angle <= re_angle + ang_offset and \
                        e_x - dist_offset <= b_x <= e_x + dist_offset and \
                        e_y - self.COLISION_OFFSET <= b_y <= e_y + self.COLISION_OFFSET:
                    if length <= 3 and \
                            (90 - ang_offset <= re_angle <= 90 + ang_offset or \
                            270 - ang_offset <= re_angle <= 270 + ang_offset):
                        move_value = -10
                    else:
                        move_value = self.drive(Drive.FORWARD, time)
                # bot and enemy facing each other and on the +/- same y position
                elif re_angle - ang_offset <= self.player.angle <= re_angle + ang_offset and \
                        e_y - dist_offset <= b_y <= e_y + dist_offset and \
                        e_x - self.COLISION_OFFSET <= b_x <= e_x + self.COLISION_OFFSET:
                    if length <= 3 and \
                            (0 <= re_angle <= ang_offset or 360 - ang_offset <= re_angle <= 360 or \
                            180 - ang_offset <= re_angle <= 180 + ang_offset):
                        move_value = -10
                    else:
                        move_value = self.drive(Drive.FORWARD, time)
                # bot or enemy is turned to the other one in a 90 degree angle
                elif re_angle + 90 - ang_offset <= self.player.angle <= re_angle + 90 + ang_offset or \
                      re_angle - 90 - ang_offset <= self.player.angle <= re_angle - 90 + ang_offset: \
                    move_value = self.drive(Drive.FORWARD, time)
                elif length > 2:
                    move_value = self.drive(Drive.FORWARD, time)
                else:
                    move_value = -10 - random.randrange(10)
            self.glitch_time += move_value
            if self.glitch_time >= 100:
                self.glitch_time = -40 + random.randrange(10)
            elif move_value == 0:
                self.glitch_time = 0

    def john(self, time):
        if self.player.is_alive():
            self._reload(time)
            length, rotate = self.move2
            shot = self.shot_condition(length)
            angle = self.player.angle - rotate
            width = self.game.assets.width
            height = self.game.assets.height

            if self.player.angle > 180 and rotate == DirectionAngle.RIGHT:
                angle = angle - 360
            elif self.player.angle <= 0 and rotate == DirectionAngle.DOWN:
                angle = (360 + angle)

            if angle != 0 and (-1 < self.player.angle < 1 and self.x * width > self.player.position[0] - width / 2
                               or 179 < self.player.angle < 181 and self.player.position[0] > (
                                       self.x + 1) * width - width / 2 + 6
                               or 269 < self.player.angle < 271 and self.y * height >= self.player.position[
                                   1] - height / 2 + 7
                               or 89 < self.player.angle < 91 and self.player.position[1] > (
                                       self.y + 1) * height - height / 2
                    or 359 < self.player.angle < 361 and self.player.position[0] > (
                    self.x + 1) * width - width / 2 + 6):

                # print("b")
                angle = 0

            if shot:
                self.shot()
            if angle > 1:
                self.rotate(Rotate.RIGHT, 2*time)
            elif angle < -1:
                self.rotate(Rotate.LEFT, 2*time)
            else:
                if angle > 0.05:
                    self.rotate(Rotate.RIGHT, time/5)
                elif angle < -0.05:
                    self.rotate(Rotate.LEFT, time/5)

                if self.glitch_time < 0:
                    self.drive(Drive.BACKWARD, time)
                    move_value = 1
                    self.player.lastMove = None
                else:
                    move_value = self.drive(Drive.FORWARD, time)

                self.glitch_time += move_value
                if self.glitch_time == 100:
                    self.glitch_time = -50
                elif move_value == 0:
                    self.glitch_time = 0

    def _reload(self, time):
        self.player.reload_time -= time
        StatBar.show_reload(self.screen, self.player)
        if self.player.reload_time <= 0:
            if self.player.is_current:
                StatBar.show_magazine(self.screen, self.player)

    def _reload_magazine(self):
        if self.player.bullets != Config.player['tank']['magazine']:
            self.player.reload_magazine()
            self.player.reload_time = Config.player['tank']['reload_magazine']

    def drive(self, drive: Drive, time):
        x, y = self.player.position
        radians = -self.player.angle * pi / 180
        if drive == Drive.FORWARD:
            speed = Config.player['speed']['drive']['forward'] * time
            new_x = x + (speed * cos(radians))
            new_y = y + (speed * sin(radians))
        else:
            speed = Config.player['speed']['drive']['backward'] * time
            new_x = x - (speed * cos(radians))
            new_y = y - (speed * sin(radians))

        new_position = (new_x, new_y)

        self.player.move(new_position)
        if (x, y) == self.player.position:
            return 1
        else:
            return 0
        # TODO: Send new position to the server

    def rotate(self, angle: Rotate, time):
        rotate_speed = Config.player['speed']['rotate'] * time
        if angle == Rotate.LEFT:
            new_angle = rotate_speed
        else:
            new_angle = -rotate_speed

        if new_angle > 360:
            new_angle -= 360
        elif new_angle < -360:
            new_angle += 360

        self.player.rotate(new_angle, 1)
        # TODO: Send new angle to the server

    def shot(self):
        if self.player.reload_time <= 0:
            self.player.reload_time = Config.player['tank']['reload_bullet']
            self.player.shot()
            if self.player.is_current:
                StatBar.show_magazine(self.screen, self.player)
            if self.player.bullets == 0:
                self._reload_magazine()
            # TODO: Send bullet position to the server

