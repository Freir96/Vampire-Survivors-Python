from dataclasses import dataclass
from typing import List


@dataclass
class Wave:
    duration: int  # in seconds
    spawn_interval: int  # in milliseconds
    enemy_type: str  # folder name in images/enemies
    spawn_amount: int  # max enemies to spawn at once? Or spawn batch size?
    # Let's say spawn interval is frequency, and amount is how many per spawn.


@dataclass
class Level:
    waves: List[Wave]


# Define Levels
LEVEL_DATA = [
    Level(
        waves=[
            Wave(duration=10, spawn_interval=1000, enemy_type="bat", spawn_amount=1),
            Wave(duration=15, spawn_interval=800, enemy_type="bat", spawn_amount=2),
            Wave(duration=20, spawn_interval=600, enemy_type="blob", spawn_amount=1),
        ]
    ),
    Level(
        waves=[
            Wave(duration=15, spawn_interval=800, enemy_type="blob", spawn_amount=2),
            Wave(
                duration=20, spawn_interval=600, enemy_type="skeleton", spawn_amount=1
            ),
            Wave(
                duration=25, spawn_interval=400, enemy_type="skeleton", spawn_amount=2
            ),
        ]
    ),
    # Add more levels as needed
]
