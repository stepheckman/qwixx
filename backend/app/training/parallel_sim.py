import torch.multiprocessing as mp
import numpy as np
from typing import List, Dict, Callable, Optional
import torch
import traceback

from .simulator import QwixxSimulator, color_number_to_action
from .state_encoder import encode_simulator_state, get_action_mask
from .model import QwixxNet
from .config import TrainingConfig

def _rollout_worker(
    model_state_dict: Dict,
    config: TrainingConfig,
    num_episodes: int,
    opponent_state_dict: Optional[Dict] = None,
    seed: Optional[int] = None
):
    """
    Worker function to run a batch of rollouts in a subprocess.
    """
    # Crucial: limit threads in subprocesses to avoid deadlocks
    torch.set_num_threads(1)
    
    if seed is not None:
        import random
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)

    device = torch.device("cpu") # Subprocesses always use CPU for simulation
    
    # Initialize local models
    policy = QwixxNet(config).to(device)
    policy.load_state_dict(model_state_dict)
    policy.eval()
    
    opponent = QwixxNet(config).to(device)
    if opponent_state_dict:
        opponent.load_state_dict(opponent_state_dict)
    else:
        opponent.load_state_dict(model_state_dict)
    opponent.eval()
    
    sim = QwixxSimulator()
    all_results = []
    
    try:
        for _ in range(num_episodes):
            # Create policy functions
            def make_policy(model):
                def policy_fn(s, pid, valid, stage):
                    state = encode_simulator_state(s, pid, stage)
                    mask = get_action_mask(valid)
                    state_t = torch.FloatTensor(state).to(device)
                    mask_t = torch.FloatTensor(mask).to(device)
                    
                    action, log_prob, entropy, value = model.get_action_and_value(state_t, mask_t)
                    
                    return action, log_prob, value, state, mask

                return policy_fn

            # Special rollout that returns experiences
            result = _rollout_with_experiences(sim, make_policy(policy), make_policy(opponent), config)
            all_results.append(result)
    except Exception as e:
        print(f"ERROR in worker rollout: {e}")
        traceback.print_exc()
        
    return all_results

def _rollout_with_experiences(sim, policy_fn, opponent_fn, config):
    """
    Modified rollout that collects PPO-ready experiences.
    """
    sim.reset()
    
    # Randomly assign slots
    current_slot = np.random.randint(0, 2)
    opponent_slot = 1 - current_slot
    
    fns = [None, None]
    fns[current_slot] = policy_fn
    fns[opponent_slot] = opponent_fn
    
    experiences = []
    
    # We follow the same logic as simulator.rollout but manually
    while not sim.done:
        rolling_player = sim.current_player_idx
        other_player = 1 - rolling_player
        
        for p in sim.players:
            p.start_new_turn()
            
        sim.dice_results = sim.dice_roller.roll_all()
        rolling_made_any_move = False
        
        # Stage 1
        for pid in [rolling_player, other_player]:
            valid = sim.get_valid_actions_stage1(pid)
            if len(valid) > 1:
                prev_score_diff = sim.get_score_diff(pid)
                
                # Get action from model
                # Note: fns[pid] now returns (action, log_prob, value, state, mask)
                action, log_prob, value, state, mask = fns[pid](sim, pid, valid, 1)
                
                if np.isnan(state).any():
                    print(f"DEBUG: NaN in state! pid={pid}, stage=1")
                    sim.done = True
                    break
                
                if action not in valid:
                    action = 44
                
                info = sim.apply_action(pid, action, is_stage1=True)
                new_score_diff = sim.get_score_diff(pid)
                
                if pid == current_slot:
                    reward = 0.0
                    reward += 0.05 if info["marked"] else 0.0
                    reward += (new_score_diff - prev_score_diff) * 0.05
                    reward -= info["jump_penalty"]
                    if info["locked"]: reward += 0.5
                    
                    experiences.append({
                        "state": state,
                        "action": action,
                        "action_mask": mask,
                        "log_prob": log_prob,
                        "reward": reward,
                        "value": value,
                        "done": False
                    })
                
                if pid == rolling_player and info["marked"]:
                    rolling_made_any_move = True
            
            if sim.check_game_over(): break
        if sim.done: break
        
        # Stage 2
        valid = sim.get_valid_actions_stage2(rolling_player)
        if len(valid) > 1:
            prev_score_diff = sim.get_score_diff(rolling_player)
            action, log_prob, value, state, mask = fns[rolling_player](sim, rolling_player, valid, 2)
            
            if np.isnan(state).any():
                print(f"DEBUG: NaN in state! pid={rolling_player}, stage=2")
                sim.done = True
                break
            
            if action not in valid:
                action = 44
            
            info = sim.apply_action(rolling_player, action, is_stage1=False)
            new_score_diff = sim.get_score_diff(rolling_player)
            
            if rolling_player == current_slot:
                reward = 0.0
                reward += 0.05 if info["marked"] else 0.0
                reward += (new_score_diff - prev_score_diff) * 0.05
                reward -= info["jump_penalty"]
                if info["locked"]: reward += 0.5
                
                experiences.append({
                    "state": state,
                    "action": action,
                    "action_mask": mask,
                    "log_prob": log_prob,
                    "reward": reward,
                    "value": value,
                    "done": False
                })
            
            if info["marked"]:
                rolling_made_any_move = True
        
        if sim.check_game_over(): break
        
        # Penalty
        if not rolling_made_any_move:
            sim.players[rolling_player].scoresheet.add_penalty()
            if rolling_player == current_slot:
                # Penalty uses the 'skip' action (index 44)
                penalty_mask = np.zeros(config.action_size, dtype=np.float32)
                penalty_mask[44] = 1.0
                
                experiences.append({
                    "state": experiences[-1]["state"] if experiences else np.zeros(config.state_size, dtype=np.float32),
                    "action": 44,
                    "action_mask": penalty_mask,
                    "log_prob": 0.0,
                    "reward": -0.25,
                    "value": experiences[-1]["value"] if experiences else 0.0,
                    "done": False
                })
        
        if sim.check_game_over(): break
        sim.current_player_idx = 1 - sim.current_player_idx
        sim.turn_count += 1
        
    # Terminal rewards
    winner = sim.get_winner()
    scores = sim.get_scores()
    
    if winner is not None:
        terminal_reward = 1.0 if winner == current_slot else -1.0
        if experiences:
            experiences[-1]["reward"] += terminal_reward
            experiences[-1]["done"] = True
            
    return {
        "experiences": experiences,
        "winner": winner,
        "scores": scores,
        "current_slot": current_slot
    }

class ParallelSimulator:
    """
    Orchestrates multiple worker processes to collect experience in parallel.
    """
    def __init__(self, config: TrainingConfig, num_workers: int = 4):
        self.config = config
        self.num_workers = num_workers
        
        # Use spawn or forkserver for safety on Unix
        try:
            mp.set_start_method('spawn', force=True)
        except RuntimeError:
            pass # already set
            
        self.pool = mp.Pool(processes=num_workers)

    def collect_batch(self, policy: QwixxNet, opponent: QwixxNet, episodes_per_batch: int) -> Dict:
        # Prepare arguments for workers
        episodes_per_worker = episodes_per_batch // self.num_workers
        
        # Extract state dicts (copy to avoid mutation issues during pickling)
        policy_state = {k: v.cpu().detach() for k, v in policy.state_dict().items()}
        opponent_state = {k: v.cpu().detach() for k, v in opponent.state_dict().items()}
        
        worker_args = []
        for i in range(self.num_workers):
            num = episodes_per_worker + (1 if i < episodes_per_batch % self.num_workers else 0)
            worker_args.append((
                policy_state,
                self.config,
                num,
                opponent_state,
                np.random.randint(0, 1000000)
            ))
            
        # Run in parallel
        batch_results = self.pool.starmap(_rollout_worker, worker_args)
        
        # Flatten and aggregate
        all_experiences = []
        wins = 0
        losses = 0
        draws = 0
        total_scores = []
        
        for worker_res in batch_results:
            for res in worker_res:
                all_experiences.extend(res["experiences"])
                winner = res["winner"]
                current_slot = res["current_slot"]
                scores = res["scores"]
                
                total_scores.append(scores[current_slot])
                if winner == current_slot:
                    wins += 1
                elif winner is not None:
                    losses += 1
                else:
                    draws += 1
                    
        return {
            "experiences": all_experiences,
            "stats": {
                "wins": wins,
                "losses": losses,
                "draws": draws,
                "win_rate": wins / max(1, wins + losses + draws),
                "avg_score": np.mean(total_scores) if total_scores else 0,
                "num_experiences": len(all_experiences),
            }
        }

    def close(self):
        self.pool.close()
        self.pool.join()
