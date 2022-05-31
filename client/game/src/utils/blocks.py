class Blocks:
    wall = 'wall'
    ground = 'ground'
    spawn_point = 'spawn'

    @staticmethod
    def getAll():
        return {Blocks.wall, Blocks.ground}

    @staticmethod
    def getBlock(char):
        if char == '#':
            return Blocks.wall
        if char == '.':
            return Blocks.ground
        if char == 'S':
            return Blocks.spawn_point
