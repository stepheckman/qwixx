from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.core.game import Game
from app.core.die import DieColor
from app.schemas.game import (
    GameStateSchema,
    MoveRequest,
    GameSetupRequest,
    PlayerSchema,
    ScoreSheetSchema,
    ValidMoveSchema,
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

    # Compute valid moves for each player
    valid_moves = []
    if game.state.name in ("STAGE_1_MOVES", "STAGE_2_MOVES", "WAITING_FOR_MOVES"):
        for p in game.players:
            for color in [DieColor.RED, DieColor.YELLOW, DieColor.GREEN, DieColor.BLUE]:
                if color in game.locked_colors:
                    continue
                # Check all possible numbers for this color row
                row = p.get_scoresheet().rows.get(color)
                if not row:
                    continue
                for number in row.numbers:
                    if game.is_valid_move(p, color, number):
                        valid_moves.append(
                            ValidMoveSchema(
                                player_id=p.get_id(),
                                color=color.value,
                                number=number,
                            )
                        )

    return GameStateSchema(
        state=game.state.name,
        current_player_index=game.current_player_index,
        dice_results=game.dice_results,
        locked_colors=[c.value for c in game.locked_colors],
        message=game.message,
        players=players,
        valid_moves=valid_moves,
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
    game.auto_play_ai()
    return format_game_state(game)


@router.post("/mark", response_model=GameStateSchema)
async def mark_number(move: MoveRequest, game: Game = Depends(get_game)):
    try:
        color = DieColor(move.color)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid color: {move.color}")

    # Find the player by ID (any player can mark during Stage 1)
    player = None
    for p in game.players:
        if p.get_id() == move.player_id:
            player = p
            break
    if player is None:
        raise HTTPException(status_code=400, detail=f"Invalid player ID: {move.player_id}")

    if not game.try_mark_number(player, color, move.number):
        raise HTTPException(status_code=400, detail="Invalid move")

    game.auto_play_ai()
    return format_game_state(game)


@router.post("/done", response_model=GameStateSchema)
async def player_done(game: Game = Depends(get_game)):
    game.player_done_making_moves()
    game.auto_play_ai()
    return format_game_state(game)
