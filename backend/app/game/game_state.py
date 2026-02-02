from enum import Enum, auto

class GameState(Enum):
    SETUP = auto()
    WAITING_FOR_ROLL = auto()
    DICE_ROLLED = auto()
    STAGE_1_MOVES = auto()
    STAGE_2_MOVES = auto()
    WAITING_FOR_MOVES = auto()
    GAME_OVER = auto()
