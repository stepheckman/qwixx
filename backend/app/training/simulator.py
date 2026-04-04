"""
Fast headless Qwixx game simulator for self-play training.
Reuses core game classes but bypasses logging/API overhead.
"""

import random
from typing import List, Tuple, Optional, Dict, Callable

from app.core.die import DieColor
from app.core.scoresheet import Scoresheet
from app.core.dice_roller import DiceRoller


# Action constants
SKIP_ACTION = -1
COLORS = [DieColor.RED, DieColor.YELLOW, DieColor.GREEN, DieColor.BLUE]


def action_to_color_number(action_idx: int) -> Optional[Tuple[DieColor, int]]:
    """Convert action index (0-44) to (color, number) or None for skip."""
    if action_idx == 44:  # skip
        return None
    color_idx = action_idx // 11
    number_offset = action_idx % 11
    color = COLORS[color_idx]
    # Red/Yellow: 2-12, Green/Blue: 12-2 (but we index 0-10 in both cases)
    if color in (DieColor.RED, DieColor.YELLOW):
        number = 2 + number_offset  # 2..12
    else:
        number = 12 - number_offset  # 12..2
    return (color, number)


def color_number_to_action(color: DieColor, number: int) -> int:
    """Convert (color, number) to action index (0-43)."""
    color_idx = COLORS.index(color)
    if color in (DieColor.RED, DieColor.YELLOW):
        number_offset = number - 2
    else:
        number_offset = 12 - number
    return color_idx * 11 + number_offset


class SimPlayer:
    """Lightweight player for simulation."""

    def __init__(self, player_id: int):
        self.player_id = player_id
        self.scoresheet = Scoresheet()
        self.white_sum_used = False
        self.colored_combo_used = False
        self.total_moves_this_turn = 0

    def start_new_turn(self):
        self.white_sum_used = False
        self.colored_combo_used = False
        self.total_moves_this_turn = 0

    def can_use_white_sum(self) -> bool:
        return not self.white_sum_used

    def can_use_colored_combination(self, is_active: bool) -> bool:
        if not is_active:
            return False
        return not self.colored_combo_used and self.total_moves_this_turn < 2


class QwixxSimulator:
    """
    Fast Qwixx game simulator for RL training.
    Drives the full game loop: roll → stage 1 → stage 2 → penalty check → next turn.
    """

    def __init__(self):
        self.dice_roller = DiceRoller()
        self.players: List[SimPlayer] = []
        self.current_player_idx = 0
        self.locked_colors: set = set()
        self.dice_results: Optional[Dict[str, int]] = None
        self.done = False
        self.turn_count = 0
        self.max_turns = 200  # Safety limit

    def reset(self) -> None:
        """Reset to a fresh game."""
        self.players = [SimPlayer(0), SimPlayer(1)]
        self.current_player_idx = 0
        self.locked_colors = set()
        self.dice_results = None
        self.done = False
        self.turn_count = 0

    def get_valid_actions_stage1(self, player_id: int) -> List[int]:
        """Get valid action indices for stage 1 (white dice sum)."""
        if not self.dice_results:
            return [44]  # skip only

        player = self.players[player_id]
        if not player.can_use_white_sum():
            return [44]

        white_sum = self.dice_results["white1"] + self.dice_results["white2"]
        actions = []

        for color in COLORS:
            if color in self.locked_colors:
                continue
            if player.scoresheet.can_mark_number(color, white_sum):
                actions.append(color_number_to_action(color, white_sum))

        actions.append(44)  # can always skip
        return actions

    def get_valid_actions_stage2(self, player_id: int) -> List[int]:
        """Get valid action indices for stage 2 (white + colored combos, rolling player only)."""
        if not self.dice_results:
            return [44]

        player = self.players[player_id]
        is_active = (player_id == self.current_player_idx)
        if not player.can_use_colored_combination(is_active):
            return [44]

        white_colored_sums = self.dice_roller.get_white_plus_colored_sums()
        actions = []

        for color, sums in white_colored_sums.items():
            if color in self.locked_colors:
                continue
            for sum_value in sums:
                if player.scoresheet.can_mark_number(color, sum_value):
                    actions.append(color_number_to_action(color, sum_value))

        # Deduplicate (two white dice can give same sum)
        actions = list(set(actions))
        actions.append(44)  # can always skip
        return actions

    def apply_action(self, player_id: int, action_idx: int, is_stage1: bool) -> Dict:
        """
        Apply an action for a player. Returns info dict with reward shaping signals.
        """
        info = {"marked": False, "locked": False, "penalty": False}

        if action_idx == 44:  # skip
            return info

        result = action_to_color_number(action_idx)
        if result is None:
            return info

        color, number = result
        player = self.players[player_id]

        if color in self.locked_colors:
            return info
        if not player.scoresheet.can_mark_number(color, number):
            return info

        # Validate move type
        if is_stage1:
            white_sum = self.dice_results["white1"] + self.dice_results["white2"]
            if number != white_sum:
                return info
            if not player.can_use_white_sum():
                return info
        else:
            is_active = (player_id == self.current_player_idx)
            if not player.can_use_colored_combination(is_active):
                return info

        # Mark the number
        if player.scoresheet.mark_number(color, number):
            info["marked"] = True
            if is_stage1:
                player.white_sum_used = True
            else:
                player.colored_combo_used = True
            player.total_moves_this_turn += 1

            # Check for row lock
            if player.scoresheet.can_lock_row(color):
                player.scoresheet.lock_row(color)
                self.locked_colors.add(color)
                info["locked"] = True

        return info

    def check_game_over(self) -> bool:
        """Check if game is over. Returns True if done."""
        if len(self.locked_colors) >= 2:
            self.done = True
            return True
        for player in self.players:
            if player.scoresheet.penalties >= 4:
                self.done = True
                return True
        if self.turn_count >= self.max_turns:
            self.done = True
            return True
        return False

    def get_scores(self) -> Tuple[int, int]:
        """Get final scores for both players."""
        return (
            self.players[0].scoresheet.calculate_total_score(),
            self.players[1].scoresheet.calculate_total_score(),
        )

    def get_winner(self) -> Optional[int]:
        """Get winner player_id, or None for tie."""
        s0, s1 = self.get_scores()
        if s0 > s1:
            return 0
        elif s1 > s0:
            return 1
        return None

    def rollout(
        self,
        policy_fn_0: Callable,
        policy_fn_1: Callable,
        collect_trajectories: bool = False,
    ) -> Dict:
        """
        Play a complete game using two policy functions.

        Each policy_fn takes (simulator, player_id, valid_actions, stage) and returns action_idx.

        Returns dict with game results and optionally trajectories.
        """
        self.reset()
        policy_fns = [policy_fn_0, policy_fn_1]

        trajectories = {0: [], 1: []}  # (state_info, action, reward) per player

        while not self.done:
            rolling_player = self.current_player_idx
            other_player = 1 - rolling_player

            # Reset turn tracking
            for p in self.players:
                p.start_new_turn()

            # Roll dice
            self.dice_results = self.dice_roller.roll_all()

            rolling_made_any_move = False

            # --- Stage 1: Both players can use white dice sum ---
            for pid in [rolling_player, other_player]:
                valid = self.get_valid_actions_stage1(pid)
                if len(valid) > 1:  # more than just skip
                    action = policy_fns[pid](self, pid, valid, 1)
                    if action not in valid:
                        action = 44  # invalid → skip

                    info = self.apply_action(pid, action, is_stage1=True)

                    if collect_trajectories:
                        reward = 0.0
                        if info["marked"]:
                            reward += 0.1
                        if info["locked"]:
                            reward += 0.5
                        trajectories[pid].append({
                            "player_id": pid,
                            "stage": 1,
                            "action": action,
                            "valid_actions": valid,
                            "reward": reward,
                            "is_rolling": pid == rolling_player,
                        })

                    if pid == rolling_player and info["marked"]:
                        rolling_made_any_move = True

                if self.check_game_over():
                    break

            if self.done:
                break

            # --- Stage 2: Only rolling player can use white + colored combos ---
            valid = self.get_valid_actions_stage2(rolling_player)
            if len(valid) > 1:  # more than just skip
                action = policy_fns[rolling_player](self, rolling_player, valid, 2)
                if action not in valid:
                    action = 44

                info = self.apply_action(rolling_player, action, is_stage1=False)

                if collect_trajectories:
                    reward = 0.0
                    if info["marked"]:
                        reward += 0.1
                    if info["locked"]:
                        reward += 0.5
                    trajectories[rolling_player].append({
                        "player_id": rolling_player,
                        "stage": 2,
                        "action": action,
                        "valid_actions": valid,
                        "reward": reward,
                        "is_rolling": True,
                    })

                if info["marked"]:
                    rolling_made_any_move = True

            if self.check_game_over():
                break

            # --- Penalty check: rolling player gets penalty if no moves made ---
            if not rolling_made_any_move:
                self.players[rolling_player].scoresheet.add_penalty()
                if collect_trajectories:
                    trajectories[rolling_player].append({
                        "player_id": rolling_player,
                        "stage": 0,  # penalty event
                        "action": -1,
                        "valid_actions": [],
                        "reward": -0.2,
                        "is_rolling": True,
                    })

            if self.check_game_over():
                break

            # Next turn
            self.current_player_idx = 1 - self.current_player_idx
            self.turn_count += 1

        # Add terminal rewards
        winner = self.get_winner()
        scores = self.get_scores()

        if collect_trajectories and winner is not None:
            for pid in [0, 1]:
                terminal_reward = 1.0 if pid == winner else -1.0
                if trajectories[pid]:
                    trajectories[pid][-1]["reward"] += terminal_reward

        return {
            "winner": winner,
            "scores": scores,
            "turn_count": self.turn_count,
            "trajectories": trajectories if collect_trajectories else None,
        }
