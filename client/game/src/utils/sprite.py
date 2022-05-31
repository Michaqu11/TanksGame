import pygame

from client.game.src.utils.config import Config


class Sprite(pygame.sprite.Sprite):
    def __init__(self, position, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=position)


class TankSprite(pygame.sprite.Sprite):
    def __init__(self, position, image):
        super().__init__()
        self.image = image
        self._image = image
        self._position = position
        self.rect = self.image.get_rect(center=position)

    def move(self, position):
        self._position = position
        self.rect = self.image.get_rect(center=position)

    def rotate(self, angle):
        self.image = pygame.transform.rotate(self._image, angle)
        self.rect = self.image.get_rect(center=self._position)


class BulletSprite(pygame.sprite.Sprite):
    def __init__(self, position, angle):
        super().__init__()
        self._position = position
        self._angle = angle
        self.image = pygame.image.load("assets/textures/bullet.png")
        self.rect = self.image.get_rect(center=self._position)
        self.create()

    def create(self):
        size_scale = Config.bullet["scale"]
        self.image = pygame.transform.scale(self.image, (self.rect.width * size_scale, self.rect.height * size_scale))
        self.rect = self.image.get_rect(center=self._position)
        self.rotate(self._angle)

    def move(self, position):
        self._position = position
        self.rect = self.image.get_rect(center=self._position)

    def rotate(self, angle):
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=self._position)
