"""
Encodes Qwixx game state into feature vectors for neural network input.
"""

import numpy as np
from typing import List

from app.core.die import DieColor

COLORS = [DieColor.RED, DieColor.YELLOW, DieColor.GREEN, DieColor.BLUE]
STATE_SIZE = 172
ACTION_SIZE = 45  # 4 colors × 11 numbers + 1 skip


def encode_scoresheet(scoresheet) -> np.ndarray:
    """
    Encode a single player's scoresheet into features.
    Returns 57 features: 4 rows × 14 features + 1 penalty.
    """
    features = []

    for color in COLORS:
        row = scoresheet.rows[color]
        # 11 binary features: which numbers are marked
        for number in row.numbers:
            features.append(1.0 if number in row.marked else 0.0)
        # Rightmost marked position (normalized 0-1)
        features.append(row.rightmost_marked / 10.0 if row.rightmost_marked >= 0 else 0.0)
        # Mark count (normalized 0-1, max ~12)
        features.append(len(row.marked) / 12.0)
        # Is locked
        features.append(1.0 if row.is_locked else 0.0)

    # Penalty count (normalized)
    features.append(scoresheet.penalties / 4.0)

    return np.array(features, dtype=np.float32)


def encode_state(
    player_scoresheet,
    opponent_scoresheet,
    dice_results: dict,
    is_rolling: bool,
    stage: int,
    locked_colors: set,
    turn_count: int = 0,
    max_turns: int = 200,
) -> np.ndarray:
    """
    Encode the full game state from a player's perspective.

    Returns feature vector of size STATE_SIZE (172):
    - Player scoresheet: 57 features
    - Opponent scoresheet: 57 features
    - Dice values: 6 features
    - White sum: 1 feature
    - Is rolling player: 1 feature
    - Stage: 1 feature
    - Dead numbers bitmask: 44 features
    - Game progress: 1 feature
    - Locked colors: 4 features

    Total: 172
    """
    # Player and Opponent scoresheets (114 features)
    player_features = encode_scoresheet(player_scoresheet)
    opponent_features = encode_scoresheet(opponent_scoresheet)

    # Dice values normalized to 0-1 (6 features)
    dice = dice_results or {}
    dice_features = np.array([
        dice.get("white1", 0) / 6.0,
        dice.get("white2", 0) / 6.0,
        dice.get("red", 0) / 6.0,
        dice.get("yellow", 0) / 6.0,
        dice.get("green", 0) / 6.0,
        dice.get("blue", 0) / 6.0,
    ], dtype=np.float32)

    # White sum normalized (1 feature)
    white_sum = (dice.get("white1", 0) + dice.get("white2", 0)) / 12.0
    white_sum_feature = np.array([white_sum], dtype=np.float32)

    # Is rolling player (1 feature)
    is_rolling_feature = np.array([1.0 if is_rolling else 0.0], dtype=np.float32)

    # Stage (1 feature, normalized)
    stage_feature = np.array([stage / 2.0], dtype=np.float32)

    # Dead numbers bitmask (44 features)
    # A number is dead if it's behind the rightmost marked number in its row
    dead_features = []
    for color in COLORS:
        row = player_scoresheet.rows[color]
        rightmost = row.rightmost_marked
        for i, number in enumerate(row.numbers):
            # In Qwixx, once you mark a number, all numbers to its left are dead.
            # rightmost is the index in row.numbers (0-10)
            is_dead = 1.0 if (rightmost >= 0 and i < rightmost and number not in row.marked) else 0.0
            dead_features.append(is_dead)
    dead_features = np.array(dead_features, dtype=np.float32)

    # Game progress (1 feature)
    progress_feature = np.array([turn_count / max_turns], dtype=np.float32)

    # Global locked colors (4 features)
    locked_features = np.array([1.0 if c in locked_colors else 0.0 for c in COLORS], dtype=np.float32)

    state = np.concatenate([
        player_features,       # 57
        opponent_features,     # 57
        dice_features,         # 6
        white_sum_feature,     # 1
        is_rolling_feature,    # 1
        stage_feature,         # 1
        dead_features,         # 44
        progress_feature,      # 1
        locked_features,       # 4
    ])

    assert state.shape[0] == STATE_SIZE, f"Expected {STATE_SIZE}, got {state.shape[0]}"
    return state


def encode_simulator_state(simulator, player_id: int, stage: int) -> np.ndarray:
    """Helper to encode state from the simulator object."""
    player = simulator.players[player_id]
    opponent = simulator.players[1 - player_id]
    
    return encode_state(
        player.scoresheet,
        opponent.scoresheet,
        simulator.dice_results,
        player_id == simulator.current_player_idx,
        stage,
        simulator.locked_colors,
        simulator.turn_count,
        simulator.max_turns
    )


def get_action_mask(valid_actions: List[int]) -> np.ndarray:
    """
    Create a boolean mask for valid actions.
    True = valid, False = invalid.
    """
    mask = np.zeros(ACTION_SIZE, dtype=np.float32)
    for action in valid_actions:
        if 0 <= action < ACTION_SIZE:
            mask[action] = 1.0
    return mask
