import concurrent
import multiprocessing as mp
from concurrent.futures import thread, as_completed

from client.game.src.core.screen import Screen
import os

"""os.environ["SDL_VIDEODRIVER"] = "dummy"
statistic = {'0': 0, '1': 0}
executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)


def simulation(id):
    # print(id)
    try:
        screen = Screen()
        return screen.new_game()
    except:
        return []


def info(num_of_sim, iter):
    bar_size = 10
    progress = int((iter / num_of_sim) * bar_size) + 1
    result = "["
    for _ in range(progress):
        result += "*"
    for _ in range(bar_size - progress):
        result += "."
    result += "] " + str(statistic) + " iteration=" + str(iter)
    print(result)


if __name__ == "__main__":
    done = 0
    num_of_simulations = 100

    simulations = []

    for i in range(num_of_simulations):
        simulations.append(executor.submit(simulation, (i)))

    if len(simulations) > 0:
        for future in as_completed(simulations):
            # print("future: {}, result {} ".format(future, future.result()))
            for winner in future.result():
                statistic[str(winner)] += 1
                done += 1
                info(num_of_simulations, done)"""

screen = Screen()
screen.new_game()