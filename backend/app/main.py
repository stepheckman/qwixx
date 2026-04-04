from typing import Dict, List, Optional, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.game.game import Game
from app.game.die import DieColor
from app.game.game_state import GameState

# In-memory store for active games
# In a production app, this would be in Redis or a DB
sessions: Dict[str, Game] = {}

class GameConfig(BaseModel):
    num_players: int = 2
    ai_strategy: str = "medium"

class MarkRequest(BaseModel):
    player_id: int
    color: str
    number: int

class GameStateResponse(BaseModel):
    state: str
    message: str
    dice_results: Optional[Dict[str, int]]
    players: List[Dict[str, Any]]
    locked_colors: List[str]
    current_player_id: int

app = FastAPI(title="Qwixx API")

# CORS Middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def process_ai_turns(game: Game) -> None:
    """Process any pending AI moves until it's a human player's turn or game is over."""
    max_iterations = 20  # safety limit
    for _ in range(max_iterations):
        if game.state == GameState.GAME_OVER:
            break
        current = game.get_current_player()
        is_ai = hasattr(current, 'is_ai') and current.is_ai

        if game.state == GameState.STAGE_1_MOVES:
            # Let AI players make stage 1 moves
            for player in game.get_players():
                if hasattr(player, 'is_ai') and player.is_ai:
                    available_moves = player.get_available_moves(game)
                    if available_moves and player.should_make_move_in_stage(game, 1):
                        move = player.make_move_decision(game, available_moves)
                        if move:
                            color, number = move
                            game.try_mark_number(player, color, number)
                    game.stage_1_players_finished.add(player.get_id())
            # Don't auto-advance stage 1 — let human click Done
            break

        elif game.state == GameState.STAGE_2_MOVES:
            if is_ai:
                available_moves = current.get_available_moves(game)
                if available_moves and current.should_make_move_in_stage(game, 2):
                    move = current.make_move_decision(game, available_moves)
                    if move:
                        color, number = move
                        game.try_mark_number(current, color, number)
                game.stage_2_done()
            else:
                break  # Human's turn in stage 2

        elif game.state == GameState.WAITING_FOR_ROLL:
            if is_ai:
                game.roll_dice()
            else:
                break  # Human's turn to roll
        else:
            break

def get_game_state_dict(game: Game) -> Dict[str, Any]:
    return {
        "state": game.state.name,
        "message": game.message,
        "dice_results": game.dice_results,
        "locked_colors": [c.value for c in game.locked_colors],
        "current_player_id": game.get_current_player().get_id(),
        "players": [
            {
                "id": p.get_id(),
                "name": p.get_name(),
                "is_active": p.is_active_player(),
                "total_score": p.get_total_score(),
                "penalties": p.get_scoresheet().penalties,
                "rows": {
                    color.value: {
                        "marked": list(row.marked),
                        "is_locked": row.is_locked
                    } for color, row in p.get_scoresheet().rows.items()
                }
            } for p in game.get_players()
        ]
    }

@app.post("/game/setup")
def start_game(config: GameConfig):
    session_id = "default"  # Simplification for single user
    game = Game(num_players=config.num_players, ai_strategy=config.ai_strategy)
    sessions[session_id] = game
    process_ai_turns(game)
    return get_game_state_dict(game)

@app.get("/game/state")
def get_state():
    session_id = "default"
    if session_id not in sessions:
        return {"error": "No active game"}
    return get_game_state_dict(sessions[session_id])

@app.post("/game/roll")
def roll_dice():
    session_id = "default"
    if session_id not in sessions:
        return {"error": "No active game"}
    game = sessions[session_id]
    game.roll_dice()
    process_ai_turns(game)
    return get_game_state_dict(game)

@app.post("/game/mark")
def mark_number(request: MarkRequest):
    session_id = "default"
    if session_id not in sessions:
        return {"error": "No active game"}
    game = sessions[session_id]
    
    # Simple lookup for player and color
    player = next((p for p in game.get_players() if p.get_id() == request.player_id), None)
    try:
        color = DieColor(request.color)
    except ValueError:
        return {"error": "Invalid color"}
        
    if not player:
        return {"error": "Player not found"}
        
    success = game.try_mark_number(player, color, request.number)
    process_ai_turns(game)
    return {
        "success": success,
        "game_state": get_game_state_dict(game)
    }

@app.post("/game/done")
def player_done():
    session_id = "default"
    if session_id not in sessions:
        return {"error": "No active game"}
    game = sessions[session_id]
    game.player_done_making_moves()
    process_ai_turns(game)
    return get_game_state_dict(game)

@app.get("/")
def root():
    return {"message": "Welcome to Qwixx API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
