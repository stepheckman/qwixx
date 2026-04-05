"""
Analyze the trained RL model's strategy by probing its decisions
across a variety of game scenarios.

Usage:
    cd backend && python -m app.training.analyze_strategy
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import torch
import torch.nn.functional as F
import numpy as np
from app.training.model import QwixxNet
from app.training.config import TrainingConfig
from app.training.simulator import QwixxSimulator, action_to_color_number, color_number_to_action, COLORS
from app.training.state_encoder import encode_state, get_action_mask, STATE_SIZE, ACTION_SIZE
from app.core.die import DieColor
from app.core.scoresheet import Scoresheet


def load_model(path="app/training/models/best_model.pt"):
    config = TrainingConfig()
    model = QwixxNet(config)
    checkpoint = torch.load(path, map_location="cpu", weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    return model


def get_probs(model, state, valid_actions):
    """Get action probabilities from the model."""
    mask = get_action_mask(valid_actions)
    state_t = torch.FloatTensor(state).unsqueeze(0)
    mask_t = torch.FloatTensor(mask).unsqueeze(0)
    with torch.no_grad():
        logits, value = model(state_t, mask_t)
    probs = F.softmax(logits, dim=-1).squeeze(0).numpy()
    return probs, value.item()


def action_name(a):
    if a == 44:
        return "SKIP"
    result = action_to_color_number(a)
    if result:
        color, num = result
        return f"{color.value.upper()}-{num}"
    return f"action-{a}"


def make_scoresheet(marks=None, penalties=0):
    """Create a scoresheet with specified marks. marks is dict of color -> list of numbers."""
    ss = Scoresheet()
    if marks:
        for color, numbers in marks.items():
            for num in sorted(numbers, key=lambda n: ss.rows[color].numbers.index(n)):
                ss.mark_number(color, num)
    ss.penalties = penalties
    return ss


def make_dice(w1, w2, r, y, g, b):
    return {"white1": w1, "white2": w2, "red": r, "yellow": y, "green": g, "blue": b}


def analyze_scenario(model, name, player_ss, opp_ss, dice, is_rolling, stage,
                     locked_colors=None, valid_actions=None, turn=0):
    """Analyze a single scenario and print the model's preferences."""
    locked = locked_colors or set()
    state = encode_state(player_ss, opp_ss, dice, is_rolling, stage, locked, turn, 200)

    if valid_actions is None:
        # Build valid actions from a simulator to be accurate
        valid_actions = []
        white_sum = dice["white1"] + dice["white2"]
        for color in COLORS:
            if color in locked:
                continue
            if stage == 1:
                if player_ss.can_mark_number(color, white_sum):
                    valid_actions.append(color_number_to_action(color, white_sum))
            elif stage == 2:
                for w in [dice["white1"], dice["white2"]]:
                    for c_key, c_color in [("red", DieColor.RED), ("yellow", DieColor.YELLOW),
                                            ("green", DieColor.GREEN), ("blue", DieColor.BLUE)]:
                        if c_color == color and c_color not in locked:
                            s = w + dice[c_key]
                            if player_ss.can_mark_number(color, s):
                                valid_actions.append(color_number_to_action(color, s))
        valid_actions = list(set(valid_actions))
        valid_actions.append(44)

    probs, value = get_probs(model, state, valid_actions)

    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    print(f"  State value: {value:+.3f}")
    print(f"  Preferences:")

    # Sort valid actions by probability
    action_probs = [(a, probs[a]) for a in valid_actions if probs[a] > 0.001]
    action_probs.sort(key=lambda x: -x[1])

    for a, p in action_probs:
        bar = "█" * int(p * 40)
        print(f"    {action_name(a):>12s}  {p:6.1%}  {bar}")

    return action_probs


def main():
    print("Loading best model...")
    model = load_model()
    print("Loaded.\n")

    blank = make_scoresheet()
    opp_blank = make_scoresheet()

    # =========================================================================
    print("\n" + "=" * 60)
    print(" LESSON 1: SKIP vs MARK — How aggressive is the agent?")
    print("=" * 60)

    # Early game, white sum = 7 (middling), all colors available
    analyze_scenario(model,
        "Early game: white sum 7, all rows empty (stage 1)",
        make_scoresheet(), make_scoresheet(),
        make_dice(3, 4, 2, 5, 3, 6), is_rolling=True, stage=1)

    # Early game, white sum = 3 (low, risky for red/yellow since it skips 2)
    analyze_scenario(model,
        "Early game: white sum 3, all rows empty — skip 2? (stage 1)",
        make_scoresheet(), make_scoresheet(),
        make_dice(1, 2, 4, 3, 5, 6), is_rolling=True, stage=1)

    # Early game, white sum = 11 (high, risky for green/blue since it skips 12)
    analyze_scenario(model,
        "Early game: white sum 11, all rows empty — skip 12? (stage 1)",
        make_scoresheet(), make_scoresheet(),
        make_dice(5, 6, 3, 2, 4, 1), is_rolling=True, stage=1)

    # =========================================================================
    print("\n\n" + "=" * 60)
    print(" LESSON 2: ROW DENSITY — Does it prefer building dense rows?")
    print("=" * 60)

    # Has red 2,3,4 marked. White sum = 6. Should eagerly take red-6 (small gap)?
    analyze_scenario(model,
        "Red has 2,3,4 marked. White sum 6 — take it (gap of 1)?",
        make_scoresheet({DieColor.RED: [2, 3, 4]}), make_scoresheet(),
        make_dice(2, 4, 5, 3, 6, 1), is_rolling=True, stage=1)

    # Has red 2 marked. White sum = 8. Big gap to jump.
    analyze_scenario(model,
        "Red has only 2 marked. White sum 8 — big gap of 5",
        make_scoresheet({DieColor.RED: [2]}), make_scoresheet(),
        make_dice(3, 5, 4, 2, 6, 1), is_rolling=True, stage=1)

    # Has red 2,3,4,5,6 marked. White sum = 7. Perfect sequential.
    analyze_scenario(model,
        "Red has 2-6 marked. White sum 7 — perfect next number",
        make_scoresheet({DieColor.RED: [2, 3, 4, 5, 6]}), make_scoresheet(),
        make_dice(3, 4, 2, 5, 6, 1), is_rolling=True, stage=1)

    # =========================================================================
    print("\n\n" + "=" * 60)
    print(" LESSON 3: COLOR PREFERENCE — Any color bias?")
    print("=" * 60)

    # White sum = 7, all rows empty, all colors available
    analyze_scenario(model,
        "White sum 7, all empty — which color does it prefer?",
        make_scoresheet(), make_scoresheet(),
        make_dice(3, 4, 2, 5, 4, 3), is_rolling=True, stage=1)

    # =========================================================================
    print("\n\n" + "=" * 60)
    print(" LESSON 4: STAGE 2 — Colored die combos")
    print("=" * 60)

    # Rolling player, stage 2. White=3+4, Red=2 → red options: 5 or 6
    analyze_scenario(model,
        "Stage 2: White 3+4, Red die=2. Red row empty. Options: Red-5, Red-6",
        make_scoresheet(), make_scoresheet(),
        make_dice(3, 4, 2, 5, 6, 1), is_rolling=True, stage=2)

    # Stage 2 with multiple color options
    analyze_scenario(model,
        "Stage 2: White 3+4, many colored options available",
        make_scoresheet(), make_scoresheet(),
        make_dice(3, 4, 3, 4, 4, 3), is_rolling=True, stage=2)

    # =========================================================================
    print("\n\n" + "=" * 60)
    print(" LESSON 5: ENDGAME — Lock row vs safe play")
    print("=" * 60)

    # Red has 2,3,4,5,6,7,8,9,10,11 — can lock with 12!
    analyze_scenario(model,
        "Red has 2-11 marked. White sum 12 — CAN LOCK ROW!",
        make_scoresheet({DieColor.RED: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]}),
        make_scoresheet(),
        make_dice(6, 6, 3, 4, 5, 2), is_rolling=True, stage=1)

    # Close to locking but would need to skip numbers
    analyze_scenario(model,
        "Red has 2,3,4,5,6,7,8. White sum 12 — skip 9,10,11 to lock?",
        make_scoresheet({DieColor.RED: [2, 3, 4, 5, 6, 7, 8]}),
        make_scoresheet(),
        make_dice(6, 6, 3, 4, 5, 2), is_rolling=True, stage=1)

    # Only 5 marks — can't lock (need 5+ marks + lock number)
    analyze_scenario(model,
        "Red has 2,3,4,5,6 (5 marks). White sum 12 — skip to 12? (can't lock yet)",
        make_scoresheet({DieColor.RED: [2, 3, 4, 5, 6]}),
        make_scoresheet(),
        make_dice(6, 6, 3, 4, 5, 2), is_rolling=True, stage=1)

    # =========================================================================
    print("\n\n" + "=" * 60)
    print(" LESSON 6: DEFENSIVE — React to opponent progress")
    print("=" * 60)

    # Opponent close to locking red (has 2-10). We have nothing in red.
    analyze_scenario(model,
        "Opponent has Red 2-10 (close to lock). We have empty red. White sum 7.",
        make_scoresheet(),
        make_scoresheet({DieColor.RED: [2, 3, 4, 5, 6, 7, 8, 9, 10]}),
        make_dice(3, 4, 2, 5, 6, 1), is_rolling=True, stage=1)

    # Opponent has nothing, we're behind on score
    analyze_scenario(model,
        "We have 3 penalties, opponent has 0. White sum 7. Desperate?",
        make_scoresheet(penalties=3),
        make_scoresheet({DieColor.RED: [2, 3, 4, 5], DieColor.YELLOW: [2, 3, 4, 5]}),
        make_dice(3, 4, 2, 5, 6, 1), is_rolling=True, stage=1)

    # =========================================================================
    print("\n\n" + "=" * 60)
    print(" LESSON 7: MULTI-ROW — Spread vs focus")
    print("=" * 60)

    # Has progress in red (2,3,4). White sum 5. Can take red-5 or start yellow-5.
    analyze_scenario(model,
        "Red has 2,3,4. White sum 5 — extend Red or start Yellow?",
        make_scoresheet({DieColor.RED: [2, 3, 4]}),
        make_scoresheet(),
        make_dice(2, 3, 4, 5, 6, 1), is_rolling=True, stage=1)

    # Already have 2 strong rows. White sum = 4. Start a 3rd row?
    analyze_scenario(model,
        "Red 2-6, Yellow 2-5. White sum 4. Start Green/Blue-4 or skip?",
        make_scoresheet({DieColor.RED: [2, 3, 4, 5, 6], DieColor.YELLOW: [2, 3, 4, 5]}),
        make_scoresheet(),
        make_dice(1, 3, 5, 6, 4, 2), is_rolling=True, stage=1)

    # =========================================================================
    print("\n\n" + "=" * 60)
    print(" LESSON 8: SKIP TOLERANCE — When to eat a penalty")
    print("=" * 60)

    # Non-rolling player, only option is white sum in a bad position
    analyze_scenario(model,
        "Non-rolling, white sum 10. Red has 2,3. Skip 4-9 to take Red-10?",
        make_scoresheet({DieColor.RED: [2, 3]}),
        make_scoresheet(),
        make_dice(4, 6, 3, 2, 5, 1), is_rolling=False, stage=1)

    # =========================================================================
    print("\n\n" + "=" * 60)
    print(" LESSON 9: VALUE FUNCTION — How does it evaluate positions?")
    print("=" * 60)

    dice = make_dice(3, 4, 3, 4, 3, 4)

    positions = [
        ("Empty board", make_scoresheet(), make_scoresheet()),
        ("Red 2-6 (we're ahead)",
         make_scoresheet({DieColor.RED: [2, 3, 4, 5, 6]}), make_scoresheet()),
        ("Both have Red 2-6 (even)",
         make_scoresheet({DieColor.RED: [2, 3, 4, 5, 6]}),
         make_scoresheet({DieColor.RED: [2, 3, 4, 5, 6]})),
        ("Opponent has Red 2-8 (we're behind)",
         make_scoresheet(), make_scoresheet({DieColor.RED: [2, 3, 4, 5, 6, 7, 8]})),
        ("We have 2 strong rows",
         make_scoresheet({DieColor.RED: [2, 3, 4, 5, 6, 7], DieColor.YELLOW: [2, 3, 4, 5, 6]}),
         make_scoresheet()),
        ("We have 3 penalties (desperate)",
         make_scoresheet(penalties=3), make_scoresheet()),
        ("Near lock: Red 2-11",
         make_scoresheet({DieColor.RED: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]}),
         make_scoresheet()),
    ]

    print(f"\n{'Position':<45s} {'Value':>8s}")
    print("-" * 55)
    for name, pss, oss in positions:
        state = encode_state(pss, oss, dice, True, 1, set(), 20, 200)
        mask = get_action_mask([44])  # just need value
        state_t = torch.FloatTensor(state).unsqueeze(0)
        mask_t = torch.FloatTensor(mask).unsqueeze(0)
        with torch.no_grad():
            _, value = model(state_t, mask_t)
        print(f"  {name:<43s} {value.item():+.3f}")

    # =========================================================================
    print("\n\n" + "=" * 60)
    print(" LESSON 10: GAME REPLAY — Watch its actual choices")
    print("=" * 60)

    sim = QwixxSimulator()
    sim.reset()

    def tracked_policy(s, pid, valid, stage):
        state = encode_state(
            s.players[pid].scoresheet,
            s.players[1 - pid].scoresheet,
            s.dice_results, pid == s.current_player_idx, stage,
            s.locked_colors, s.turn_count, s.max_turns
        )
        mask = get_action_mask(valid)
        state_t = torch.FloatTensor(state)
        mask_t = torch.FloatTensor(mask)
        action, lp, ent, val = model.get_action_and_value(state_t, mask_t)
        if action not in valid:
            action = 44
        move = action_to_color_number(action)
        move_str = f"{move[0].value}-{move[1]}" if move else "skip"
        ws = s.dice_results["white1"] + s.dice_results["white2"]
        print(f"  Turn {s.turn_count:>3d} | P{pid} | Stage {stage} | "
              f"WS={ws:>2d} | chose {move_str:<12s} | val={val:+.3f}")
        return action

    from app.core.ai_player import AIPlayer

    heuristic = AIPlayer("H", 1, difficulty="hard")

    def heuristic_policy(s, pid, valid, stage):
        from app.training.simulator import action_to_color_number as a2cn
        available = []
        for a in valid:
            if a != 44:
                r = a2cn(a)
                if r:
                    available.append(r)
        if not available:
            return 44
        heuristic.scoresheet = s.players[pid].scoresheet

        class GP:
            def __init__(self, sim, pid):
                self.sim = sim
                self._pid = pid
            def get_players(self):
                class PP:
                    def __init__(self, sp):
                        self.scoresheet = sp.scoresheet
                    def get_scoresheet(self):
                        return self.scoresheet
                return [PP(p) for p in self.sim.players]
            def get_current_player(self):
                class PP:
                    def __init__(self, sp):
                        self.scoresheet = sp.scoresheet
                    def get_scoresheet(self):
                        return self.scoresheet
                return PP(self.sim.players[self.sim.current_player_idx])
            def get_locked_colors(self):
                return self.sim.locked_colors
            def get_dice_results(self):
                return self.sim.dice_results

        move = heuristic._make_hard_decision(GP(s, pid), available)
        if move is None:
            return 44
        return color_number_to_action(move[0], move[1])

    print("\n  RL Agent (P0) vs Hard AI (P1):\n")
    result = sim.rollout(tracked_policy, heuristic_policy)
    print(f"\n  Final: RL={result['scores'][0]}, Hard AI={result['scores'][1]}, "
          f"Winner={'RL!' if result['winner'] == 0 else 'Hard AI' if result['winner'] == 1 else 'Draw'}")


if __name__ == "__main__":
    main()
