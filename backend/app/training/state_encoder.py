"""
Encodes Qwixx game state into feature vectors for neural network input.
"""

import numpy as np
from typing import List

from app.core.die import DieColor

COLORS = [DieColor.RED, DieColor.YELLOW, DieColor.GREEN, DieColor.BLUE]
STATE_SIZE = 123
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


def encode_state(simulator, player_id: int, stage: int) -> np.ndarray:
    """
    Encode the full game state from a player's perspective.

    Returns feature vector of size STATE_SIZE (123):
    - Player scoresheet: 57 features
    - Opponent scoresheet: 57 features
    - Dice values: 6 features
    - White sum: 1 feature
    - Is rolling player: 1 feature
    - Stage: 1 feature

    Total: 123
    """
    player = simulator.players[player_id]
    opponent = simulator.players[1 - player_id]

    # Player's own scoresheet (57 features)
    player_features = encode_scoresheet(player.scoresheet)

    # Opponent's scoresheet (57 features)
    opponent_features = encode_scoresheet(opponent.scoresheet)

    # Dice values normalized to 0-1 (6 features)
    dice = simulator.dice_results or {}
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
    is_rolling = np.array(
        [1.0 if player_id == simulator.current_player_idx else 0.0],
        dtype=np.float32,
    )

    # Stage (1 feature, normalized)
    stage_feature = np.array([stage / 2.0], dtype=np.float32)

    state = np.concatenate([
        player_features,     # 57
        opponent_features,   # 57
        dice_features,       # 6
        white_sum_feature,   # 1
        is_rolling,          # 1
        stage_feature,       # 1
    ])

    assert state.shape[0] == STATE_SIZE, f"Expected {STATE_SIZE}, got {state.shape[0]}"
    return state


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
