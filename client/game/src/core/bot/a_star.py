

from heapq import *

from client.game.src.core.bot.maze import path_from


class A_Star:

    def __init__(self, maze):
        self.maze = maze

    def distance(self, child, end_node):
        return abs(child.x - end_node.x) + abs(child.y - end_node.y)

    def astar(self):
        maze = self.maze
        start_node = maze.find_node('S')
        start_node.visited = True
        end_node = maze.find_node('E')
        start_node.cost = 0
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
                    nowy_koszt = node.cost + maze.move_cost(child)
                    if nowy_koszt < child.cost:
                        child.cost = nowy_koszt
                        child.parent = node
                        nowy_koszt = nowy_koszt + self.distance(child, end_node)
                        id += 1
                        heappush(q, (nowy_koszt, id, child))

        return None

