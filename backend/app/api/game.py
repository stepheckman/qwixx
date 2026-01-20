from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.core.game import Game
from app.core.die import DieColor
from app.schemas.game import (
    GameStateSchema,
    MoveRequest,
    DoneRequest,
    GameSetupRequest,
    PlayerSchema,
    ScoreSheetSchema,
)

router = APIRouter()

# Global game instance for now (in-memory)
_game: Optional[Game] = None


def get_game():
    global _game
    if _game is None:
        _game = Game()
    return _game


def format_game_state(game: Game) -> GameStateSchema:
    players = []
    for p in game.players:
        ss = p.get_scoresheet()
        # Convert internal rows and their marked sets
        marked = {color.value: list(row.marked) for color, row in ss.rows.items()}

        scoresheet_schema = ScoreSheetSchema(
            marked_numbers=marked,
            penalties=ss.penalties,
            total_score=ss.calculate_total_score(),
            is_game_over=ss.is_game_over(),
        )

        players.append(
            PlayerSchema(
                id=p.get_id(),
                name=p.get_name(),
                is_active=p.is_active,
                is_ai=getattr(p, "is_ai", False),
                scoresheet=scoresheet_schema,
            )
        )

    return GameStateSchema(
        state=game.state.name,
        current_player_index=game.current_player_index,
        dice_results=game.dice_results,
        locked_colors=[c.value for c in game.locked_colors],
        message=game.message,
        players=players,
    )


@router.post("/setup", response_model=GameStateSchema)
async def setup_game(request: GameSetupRequest):
    global _game
    _game = Game(num_players=request.num_players, ai_strategy=request.ai_strategy)
    return format_game_state(_game)


@router.get("/state", response_model=GameStateSchema)
async def get_state(game: Game = Depends(get_game)):
    return format_game_state(game)


@router.post("/roll", response_model=GameStateSchema)
async def roll_dice(game: Game = Depends(get_game)):
    game.roll_dice()
    return format_game_state(game)


@router.post("/mark", response_model=GameStateSchema)
async def mark_number(move: MoveRequest, game: Game = Depends(get_game)):
    try:
        color = DieColor(move.color)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid color: {move.color}")

    # Find the player by id
    player = next((p for p in game.players if p.get_id() == move.player_id), None)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    if not game.try_mark_number(player, color, move.number):
        raise HTTPException(status_code=400, detail="Invalid move")

    return format_game_state(game)


@router.post("/done", response_model=GameStateSchema)
async def player_done(request: DoneRequest, game: Game = Depends(get_game)):
    # Find the player by id
    player = next((p for p in game.players if p.get_id() == request.player_id), None)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    game.player_done_making_moves(player)
    return format_game_state(game)
