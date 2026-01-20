from pydantic import BaseModel
from typing import List, Dict, Optional
from app.core.die import DieColor
from app.core.game_state import GameState


class DiceResult(BaseModel):
    white1: int
    white2: int
    red: int
    yellow: int
    green: int
    blue: int


class ScoreSheetSchema(BaseModel):
    marked_numbers: Dict[str, List[int]]
    penalties: int
    total_score: int
    is_game_over: bool


class PlayerSchema(BaseModel):
    id: int
    name: str
    is_active: bool
    is_ai: bool
    scoresheet: ScoreSheetSchema


class GameStateSchema(BaseModel):
    state: str
    current_player_index: int
    dice_results: Optional[Dict[str, int]]
    locked_colors: List[str]
    message: str
    players: List[PlayerSchema]


class MoveRequest(BaseModel):
    player_id: int
    color: str
    number: int


class DoneRequest(BaseModel):
    player_id: int


class GameSetupRequest(BaseModel):
    num_players: int = 2
    ai_strategy: str = "medium"
