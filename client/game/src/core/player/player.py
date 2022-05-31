import asyncio
from asyncio import wait
from math import sqrt, atan2, degrees, cos, sin, pi
from time import sleep

import pygame

from client.game.src.core.stat_bar.stat_bar import StatBar
from client.game.src.utils.config import Config
from client.game.src.utils.sprite import TankSprite


class Player:
    def __init__(self, game, id: int, position=None):
        if position is None:
            position = (400, 400)
        self.game = game
        self.screen = game.screen
        self.map = game.map
        self.tank = None
        self.id = id
        self.position = position
        self.angle = 0
        self.points = 0
        self.longest_side = None
        self.lives = Config.player['lives']
        self.bullets = Config.player['tank']['magazine']
        self.reload = 0
        self._tank_scale = Config.player['tank']['scale']
        self._alive = True
        self._kill_count = 0
        self.reload_time = 0
        self.is_current = False
        self.lastMove = None
        self.create_tank()
        self.points = 0

    def change_current(self):
        self.is_current = not self.is_current
        self._update_hearts_ui()
        StatBar.show_avatar(self.screen, False)
        StatBar.show_points(self.screen, self)

    def create_tank(self):
        tank = pygame.image.load('assets/textures/tank' + str((self.id % 3) + 1) + '.png')
        self.position = self.map.get_spawn_point
        (x, y) = self.position
        temp_pos = (x + self.game.assets.width/2,  y + self.game.assets.width/2)
        self.position = temp_pos
        self.tank = TankSprite(self.position, pygame.transform.scale(tank, self.get_tank_size()))
        self.rotate(self.init_angle())
        self.game.refresh_players()

    def init_angle(self):
        map_x, map_y = self.screen.get_size()
        map_x /= 2
        map_y /= 2
        x, y = self.position
        return -degrees(atan2(map_y - y, map_x - x))

    def draw(self):
        if self.is_alive():
            self.screen.blit(self.tank.image, self.tank.rect)
        pass

    def _wall_collide(self):
        for wall in pygame.sprite.spritecollide(self.tank, self.map.walls, False):
            if pygame.sprite.collide_mask(wall, self.tank):
                return True
        return False

    def _player_collide(self):
        for player in self.game.players:
            if self == player:
                continue

            if player.is_alive() and pygame.sprite.collide_mask(self.tank, player.tank):
                return True

        return False

    def _collide(self):
        return self._player_collide() or self._wall_collide()

    def move(self, position):
        self.tank.move(position)
        if self._collide():
            self.tank.move(self.position)
        else:
            self.position = position
            self.game.refresh_players()
        # TODO: Emit information to the server
        pass

    def rotate(self, angle, bot = 0):
        self.tank.rotate(self.angle + angle)
        if self._collide() and not bot:
            self.tank.rotate(self.angle)
        else:
            self.angle += angle
            if self.angle >= 360:
                self.angle = self.angle - 360
            if self.angle < 0:
                self.angle = 360 + self.angle

            #if self.lastMove != None and self.lastMove - 1 < self.angle < self.lastMove + 1:
             #   self.angle = self.lastMove

            self.game.refresh_players()
        # TODO: Emit information to the server
        pass

    def shot(self):
        if self.bullets > 0:
            self.bullets -= 1
            new_x, new_y = self.get_barrel_position()
            self.game.bullet_controller.add_bullet(self, (new_x, new_y), self.angle)
            # TODO: Create bullet & emit information to the server

    def reload_magazine(self):
        self.bullets = Config.player['tank']['magazine']

    def get_tank_size(self):
        (w, h) = self.screen.get_size()
        width = w / self.map.width * self._tank_scale
        height = h / self.map.height * self._tank_scale
        return width, height

    def get_barrel_position(self):
        x, y = self.position
        w, h = self.get_tank_size()
        h /= 1.5
        radians = -self.angle * pi / 180
        new_x = x + (h * cos(radians))
        new_y = y + (h * sin(radians))
        return new_x, new_y

    def die(self):
        self.lives -= 1
        self._alive = False
        del self.tank

        if self.is_current:
            StatBar.show_avatar(self.screen, True)
            self._update_hearts_ui()


    def was_hit(self):
        self.lives -= 1
        if self.is_current:
            self._update_hearts_ui()

    def _update_hearts_ui(self):
        if self.is_current:
            StatBar.show_lives(self.screen, self)

    def is_alive(self):
        return self._alive

    def add_kill(self):
        self._kill_count += 1
        self.points += Config.rewards['kill']
        if self.is_current:
            StatBar.show_points(self.screen, self)

    def add_hit(self):
        self.points += Config.rewards['hit']
        if self.is_current:
            StatBar.show_points(self.screen, self)
        # TODO: Add points
        pass
