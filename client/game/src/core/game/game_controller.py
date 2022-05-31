import time

import pygame

from client.game.src.core.bot.bot import Bot
from client.game.src.core.bot.bot_controller import BotController
from client.game.src.core.game.game import Game
from client.game.src.core.player.player import Player
from client.game.src.core.player.player_controller import PlayerController
from client.game.src.utils.config import Config


class GameController:
    def __init__(self, screen):
        self.screen = screen
        self.timer = 0
        self.game = Game(screen)
        self.game.load_assets()
        self.game.refresh_map()
        self.current_player = None
        self.bot = None
        self.bot2 = None

    def join(self):
        id = len(self.game.players)
        player = Player(self.game, id)
        if self.current_player is None:
            player.change_current()
            # self.current_player = PlayerController(player, self.screen, 0)
            self.current_player = BotController(self.screen, self.game, player, id)
            self.bot2 = self.current_player
        else:
            self.bot = BotController(self.screen, self.game, player, id)

        self.game.add_player(player)

    def start(self):
        self.timer = time.perf_counter()
        if self.bot:
            self.bot.set_enemy()
        if self.bot2:
            self.bot2.set_enemy()
        self.game.refresh_map()
        return self.loop()

    def get_winner(self):
        winners = []
        all_alive = True
        for player in self.game.players:
            if player.is_alive():
                winners.append(player.id)
            else:
                all_alive = False
        if len(winners) and not all_alive:
            return winners
        return None

    def loop(self):
        clock = pygame.time.Clock()
        running = True
        winner = None
        while running:
            frame_time = clock.tick(Config.game['fps'])
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.current_player.paul(frame_time / 1000) #poul is following bot with dodge
            self.bot.john(frame_time / 1000) # johin is getaway bot
            #self.bot.piotrek(frame_time / 1000) #piotrek is following bot
            self.game.bullet_controller.update_bullets(frame_time / 1000)
            self.game.refresh_map()
            pygame.display.set_caption('FurryTanks - %.2f FPS' % clock.get_fps())
            """if time.perf_counter() - self.timer >= Config.game['timeout']:
                return []"""
            winners = self.get_winner()
            if winners is not None:
                return winners
        return None
