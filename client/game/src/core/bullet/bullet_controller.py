from math import sin, cos, pi

import pygame

from client.game.src.core.bullet.bullet import Bullet
from client.game.src.utils.config import Config


class BulletController:
    def __init__(self, game):
        self.game = game
        self.bullets = []
        self.consumed_bullets = []

    def add_bullet(self, player, position, angle):
        self.bullets.append(Bullet(self.game.screen, player, position, angle))

    def draw(self):
        for bullet in self.bullets:
            bullet.draw()

    def update_bullets(self, time):
        for bullet in self.bullets:
            self.move(bullet, time)
        # TODO: Send position to the server

        for bullet in self.consumed_bullets:
            self.bullets.remove(bullet)
            self._delete_bullet(bullet)
        self.consumed_bullets.clear()

    def move(self, bullet, time):
        speed = Config.bullet['speed'] * time
        x, y = bullet.position
        radians = -bullet.angle * pi / 180
        new_x = x + (speed * cos(radians))
        new_y = y + (speed * sin(radians))
        bullet.move((new_x, new_y))

        # TODO: Check if additional collision check isn't needed before moving bullet
        if self._collide(bullet):
            self.consumed_bullets.append(bullet)
            player = self._player_collide(bullet)
            if player:
                if player.lives > 1:
                    bullet.player.add_hit()
                    player.was_hit()
                else:
                    bullet.player.add_kill()
                    player.die()

    @staticmethod
    def _delete_bullet(bullet):
        bullet.delete_sprite()
        del bullet

    def _wall_collide(self, bullet):
        for wall in pygame.sprite.spritecollide(bullet.bullet, self.game.map.walls, False):
            if pygame.sprite.collide_mask(wall, bullet.bullet):
                return True
        return False

    def _player_collide(self, bullet):
        for player in self.game.players:
            if player.is_alive() and pygame.sprite.collide_mask(bullet.bullet, player.tank):
                return player
        return None

    def _collide(self, bullet):
        return self._player_collide(bullet) or self._wall_collide(bullet)

