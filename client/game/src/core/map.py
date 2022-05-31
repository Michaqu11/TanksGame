import pygame


class Map:
    def __init__(self, name, width, height, data):
        self.name = name
        self.width = width
        self.height = height
        self.data = data
        self.walls = pygame.sprite.Group()
        self.ground = pygame.sprite.Group()
        self.spawn_points = []
        self.map = []

    def add_wall(self, wall):
        self.walls.add(wall)

    def add_ground(self, ground):
        self.ground.add(ground)

    def add_spawn_point(self, spawn_point):
        self.spawn_points.append(spawn_point)

    @property
    def get_spawn_point(self):
        try:
            return self.spawn_points.pop()
        except IndexError as e:
            print(e)

    def __str__(self):
        return self.name + '\t' + str(self.width) + 'x' + str(self.height) + '\n' + str('\n'.join(self.data))