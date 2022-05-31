import pygame

from client.game.src.core.bullet.bullet_controller import BulletController
from client.game.src.core.map import Map
from client.game.src.utils.assets import Assets


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.map = self._load_map('kyiv')
        self.players = []
        self.assets = Assets(screen, self.map)
        self.bullet_controller = BulletController(self)
        pass

    def add_player(self, player):
        self.players.append(player)

    def load_assets(self):
        x, y = 0, 0
        for row in self.map.data:
            x = 0
            for block in row:
                self.assets.set_block(block, (x, y))
                x += self.assets.width
            y += self.assets.height

    def refresh_map(self):
        self.refresh_ground()
        self.refresh_walls()
        self.refresh_players()
        # self.refresh_bullets()
        pygame.display.update()

    def refresh_ground(self):
        self.map.ground.draw(self.screen)

    def refresh_walls(self):
        self.map.walls.draw(self.screen)

    def refresh_players(self):
        self.refresh_ground()
        for player in self.players:
            player.draw()
        self.refresh_bullets()
        pygame.display.update()

    def refresh_bullets(self):
        self.bullet_controller.draw()

    def _load_map(self, map_name: str) -> Map:
        try:
            map = open('assets/maps/' + map_name + '.map')
            lines = map.readlines()
            y = len(lines)
            x = 0
            data = []
            for line in lines:
                line = line.replace('\n', '')
                data.append(line)

                if x == 0:
                    x = len(line)
                elif len(line) != x:
                    raise Exception('Invalid map data')
            return Map(map_name, x, y, data)
        except ValueError:
            print(ValueError)

        return None
