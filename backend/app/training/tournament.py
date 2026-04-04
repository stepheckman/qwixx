import argparse
import os
import torch
import numpy as np
from itertools import combinations
from typing import List, Dict

from .trainer import PPOTrainer
from .config import TrainingConfig
from .model import QwixxNet
from .simulator import QwixxSimulator

def run_tournament(model_paths: List[str], num_games: int = 100):
    """
    Run a Round Robin tournament between multiple checkpointed models.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = TrainingConfig()
    sim = QwixxSimulator()
    
    # Load all models
    models = {}
    for path in model_paths:
        name = os.path.basename(path)
        net = QwixxNet(config).to(device)
        checkpoint = torch.load(path, map_location=device, weights_only=False)
        net.load_state_dict(checkpoint["model_state_dict"])
        net.eval()
        models[name] = net
        print(f"Loaded {name}")

    model_names = list(models.keys())
    # Add Hard AI for baseline
    model_names.append("Heuristic-Hard")
    
    results = {name: {"wins": 0, "losses": 0, "draws": 0, "score": 0.0} for name in model_names}
    
    pairs = list(combinations(model_names, 2))
    print(f"\nStarting Tournament: {len(model_names)} competitors, {len(pairs)} matchups")
    
    for name1, name2 in pairs:
        print(f"Match: {name1} vs {name2} ({num_games} games)...")
        
        m1_wins = 0
        m2_wins = 0
        draws = 0
        
        for i in range(num_games):
            sim.reset()
            # Alternate slots
            p1_slot = i % 2
            p2_slot = 1 - p1_slot
            
            def get_policy(name, model):
                if name == "Heuristic-Hard":
                    from .trainer import PPOTrainer
                    # Re-use the heuristic wrapper from trainer
                    trainer = PPOTrainer(config)
                    return trainer.evaluate_vs_heuristic(0) # Not quite, let's keep it simple
                
                # RL Policy
                from .state_encoder import encode_simulator_state, get_action_mask
                def policy_fn(s, pid, valid, stage):
                    state = encode_simulator_state(s, pid, stage)
                    mask = get_action_mask(valid)
                    state_t = torch.FloatTensor(state).to(device)
                    mask_t = torch.FloatTensor(mask).to(device)
                    action, _, _, _ = model.get_action_and_value(state_t, mask_t)
                    return action
                return policy_fn

            # Handle heuristic specifically
            if name1 == "Heuristic-Hard" or name2 == "Heuristic-Hard":
                 # Actually, it's easier to use the existing evaluate_vs_heuristic logic
                 # but for simplicity in this script, let's just do RL vs RL for now.
                 # I'll update this once basic logic works.
                 pass

            # For now, only RL vs RL
            if name1 != "Heuristic-Hard" and name2 != "Heuristic-Hard":
                fns = [None, None]
                fns[p1_slot] = get_policy(name1, models[name1])
                fns[p2_slot] = get_policy(name2, models[name2])
                
                match_res = sim.rollout(fns[0], fns[1])
                winner = match_res["winner"]
                
                if winner == p1_slot:
                    m1_wins += 1
                    results[name1]["wins"] += 1
                    results[name2]["losses"] += 1
                elif winner == p2_slot:
                    m2_wins += 1
                    results[name2]["wins"] += 1
                    results[name1]["losses"] += 1
                else:
                    draws += 1
                    results[name1]["draws"] += 1
                    results[name2]["draws"] += 1
        
        print(f"  Result: {name1} {m1_wins} - {m2_wins} {name2} ({draws} draws)")

    # Print standings
    print("\n" + "="*30)
    print("FINAL TOURNAMENT STANDINGS")
    print("="*30)
    sorted_standings = sorted(results.items(), key=lambda x: x[1]["wins"], reverse=True)
    for name, stats in sorted_standings:
        if stats["wins"] + stats["losses"] + stats["draws"] > 0:
            print(f"{name:<20}: {stats['wins']}W - {stats['losses']}L - {stats['draws']}D")

def main():
    parser = argparse.ArgumentParser(description="Qwixx RL Tournament")
    parser.add_argument("models", nargs="+", help="Paths to model checkpoints")
    parser.add_argument("--games", type=int, default=100, help="Games per matchup")
    args = parser.parse_args()
    
    run_tournament(args.models, args.games)

if __name__ == "__main__":
    main()
