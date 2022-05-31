class Config:
    player = {
        'speed': {                      # normal | simulation
            'drive': {
                'forward': 70,         # 70     | 560
                'backward': 90         # 90     | 720
            },
            'rotate': 150              # 150    | 1200
        },
        'tank': {
            'scale': 0.7,
            'magazine': 8,
            'reload_bullet': 2,
            'reload_magazine': 4
        },
        'lives': 3
    }

    game = {
        'fps': 200,
        'timeout': 40
    }

    bullet = {
        'speed': 440,                   # 120    | 880
        'scale': 0.09
    }

    screen = {
        'resolution': {
            'width': 800,
            'height': 800
        },
        'stat_bar': 80
    }

    rewards = {
        'hit': 50,
        'kill': 200
    }
