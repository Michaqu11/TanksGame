import pygame

from client.game.src.utils.config import Config
from client.game.src.utils.sprite import Sprite


class StatBar:
    @staticmethod
    def show_lives(screen, player):
        asset_size = Config.screen['stat_bar'] / 2
        height = Config.screen['resolution']['height']
        offset = asset_size * 2
        full = pygame.image.load('assets/textures/heart/full.png')
        empty = pygame.image.load('assets/textures/heart/empty.png')
        for live in range(Config.player['lives']):
            heart = empty
            if live < player.lives:
                heart = full

            heart = pygame.transform.scale(heart, (asset_size, asset_size))

            heart = Sprite((offset, height), heart)
            offset += asset_size
            screen.blit(heart.image, heart.rect)
            heart.kill()

    @staticmethod
    def show_magazine(screen, player):
        asset_size = Config.screen['stat_bar'] / 2
        height = Config.screen['resolution']['height'] + asset_size
        offset = asset_size * 2
        full = pygame.image.load('assets/textures/bullet.png')
        empty = pygame.image.load('assets/textures/cross.png')

        for i in range(Config.player['tank']['magazine']):
            bullet = empty
            if i < player.bullets:
                bullet = full

            bullet = pygame.transform.scale(bullet, (asset_size, asset_size))

            bullet = Sprite((offset, height), bullet)
            offset += asset_size
            screen.blit(bullet.image, bullet.rect)
            bullet.kill()

    @staticmethod
    def show_reload(screen, player):
        font_size = 20
        asset_size = Config.screen['stat_bar']
        height = Config.screen['resolution']['height'] + (asset_size / 2) + ((asset_size / 2 - font_size) / 2)
        offset = asset_size + (asset_size * Config.player['tank']['magazine'] / 2)

        font = pygame.font.Font('assets/fonts/connection.ttf', font_size)
        text = font.render('WWWW', True, (0, 0, 0), (0, 0, 0))
        text = Sprite((offset, height), text)
        screen.blit(text.image, text.rect)
        if player.reload_time > 0:
            font = pygame.font.Font('assets/fonts/connection.ttf', 20)
            text = font.render('%.1fs' % player.reload_time, True, (255, 255, 255))
            text = Sprite((offset, height), text)
            screen.blit(text.image, text.rect)

    @staticmethod
    def show_points(screen, player):
        font_size = 24
        width = Config.screen['resolution']['width'] - ((Config.screen['stat_bar'] + font_size) / 4)
        height = Config.screen['resolution']['height'] + Config.screen['stat_bar'] - ((Config.screen['stat_bar'] + font_size) / 2)

        font = pygame.font.Font('assets/fonts/connection.ttf', font_size)

        text = font.render('Points: WWWWW', True, (0, 0, 0), (0, 0, 0))
        text = Sprite((width - text.get_rect()[2], height), text)
        screen.blit(text.image, text.rect)
        text = font.render('Points: %6d' % player.points, True, (255, 255, 255))
        text = Sprite((width - text.get_rect()[2], height), text)
        screen.blit(text.image, text.rect)

    @staticmethod
    def show_avatar(screen, die=False):
        asset_size = Config.screen['stat_bar']
        height = Config.screen['resolution']['height']

        avatar = pygame.image.load('assets/avatars/kbl.tif')
        avatar = pygame.transform.scale(avatar, (asset_size, asset_size))

        avatar = Sprite((0, height), avatar)

        screen.blit(avatar.image, avatar.rect)

        if die:
            dead = pygame.image.load('assets/avatars/broken_glass2.png')
            dead = pygame.transform.scale(dead, (asset_size, asset_size))

            dead = Sprite((0, height), dead)

            screen.blit(dead.image, dead.rect)