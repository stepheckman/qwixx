"""
PPO self-play trainer for Qwixx AI.
"""

import os
import copy
import random
import numpy as np
import torch
import torch.nn.functional as F
from typing import List, Dict, Optional

from .config import TrainingConfig
from .model import QwixxNet
from .simulator import QwixxSimulator, action_to_color_number, color_number_to_action, COLORS
from .state_encoder import encode_simulator_state, get_action_mask, STATE_SIZE, ACTION_SIZE
from .parallel_sim import ParallelSimulator
from torch.utils.tensorboard import SummaryWriter


class Experience:
    """Single timestep of experience."""
    __slots__ = ["state", "action", "action_mask", "log_prob", "reward", "value", "done"]

    def __init__(self, state, action, action_mask, log_prob, reward, value, done):
        self.state = state
        self.action = action
        self.action_mask = action_mask
        self.log_prob = log_prob
        self.reward = reward
        self.value = value
        self.done = done


class PPOTrainer:
    """
    PPO self-play training loop.

    Two copies of the network play against each other. The "current" policy
    collects experience and gets updated. The "opponent" policy is periodically
    frozen from the current policy to prevent co-adaptation.
    """

    def __init__(self, config: TrainingConfig = None):
        self.config = config or TrainingConfig()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Current policy (being trained)
        self.policy = QwixxNet(self.config).to(self.device)
        self.optimizer = torch.optim.Adam(self.policy.parameters(), lr=self.config.lr)

        # Frozen opponent (periodically updated from current policy)
        self.opponent = QwixxNet(self.config).to(self.device)
        self.opponent.load_state_dict(self.policy.state_dict())
        self.opponent.eval()

        self.simulator = QwixxSimulator()
        self.episode_count = 0
        self.best_win_rate = 0.0

        # Parallel simulator (Milestone 3)
        self.parallel_sim = None
        if self.config.use_parallel:
            self.parallel_sim = ParallelSimulator(self.config, num_workers=self.config.num_workers)
            print(f"Parallel training enabled with {self.config.num_workers} workers.")

        # TensorBoard logger
        log_dir = os.path.join("logs/runs", self.config.run_name)
        self.writer = SummaryWriter(log_dir)
        print(f"TensorBoard logging to {log_dir}")
        print(f"Device: {self.device}")

    def close(self):
        """Clean up parallel simulator processes."""
        if self.parallel_sim:
            self.parallel_sim.close()

    def make_policy_fn(self, model: QwixxNet, collect_exp: Optional[List] = None):
        """Create a policy function for the simulator."""

        def policy_fn(sim, player_id, valid_actions, stage):
            state = encode_simulator_state(sim, player_id, stage)
            mask = get_action_mask(valid_actions)

            state_t = torch.FloatTensor(state).to(self.device)
            mask_t = torch.FloatTensor(mask).to(self.device)

            action, log_prob, entropy, value = model.get_action_and_value(state_t, mask_t)

            if collect_exp is not None:
                collect_exp.append(Experience(
                    state=state,
                    action=action,
                    action_mask=mask,
                    log_prob=log_prob,
                    reward=0.0,  # filled in later
                    value=value,
                    done=False,
                ))

            return action

        return policy_fn

    def collect_batch(self) -> Dict:
        """
        Collect a batch of self-play games.
        Supports both sequential and parallel collection.
        """
        if self.config.use_parallel and self.parallel_sim:
            return self._collect_batch_parallel()
        else:
            return self._collect_batch_sequential()

    def _collect_batch_parallel(self) -> Dict:
        """Collect batch using multiprocessing."""
        print(f"Collecting {self.config.episodes_per_batch} episodes using {self.config.num_workers} workers...", flush=True)
        res = self.parallel_sim.collect_batch(
            self.policy, self.opponent, self.config.episodes_per_batch
        )
        
        # Convert dicts to Experience objects
        experiences = []
        for e_dict in res["experiences"]:
            experiences.append(Experience(
                state=e_dict["state"],
                action=e_dict["action"],
                action_mask=e_dict["action_mask"],
                log_prob=e_dict["log_prob"],
                reward=e_dict["reward"],
                value=e_dict["value"],
                done=e_dict["done"]
            ))
            
        return {
            "experiences": experiences,
            "stats": res["stats"]
        }

    def _collect_batch_sequential(self) -> Dict:
        """Original sequential experience collection."""
        all_experiences: List[Experience] = []
        wins = 0
        losses = 0
        draws = 0
        total_scores = []

        for _ in range(self.config.episodes_per_batch):
            # Randomly assign which player slot the current policy gets
            current_slot = random.randint(0, 1)
            opponent_slot = 1 - current_slot

            current_exp = []
            opponent_exp = []

            policy_fn_current = self.make_policy_fn(self.policy, current_exp)
            policy_fn_opponent = self.make_policy_fn(self.opponent, opponent_exp)

            fns = [None, None]
            fns[current_slot] = policy_fn_current
            fns[opponent_slot] = policy_fn_opponent

            result = self.simulator.rollout(fns[0], fns[1], collect_trajectories=True)

            winner = result["winner"]
            scores = result["scores"]
            total_scores.append(scores[current_slot])

            # Assign terminal rewards to current policy's experiences
            if winner is not None:
                terminal_reward = self.config.win_reward if winner == current_slot else self.config.lose_reward
                if winner == current_slot:
                    wins += 1
                else:
                    losses += 1
            else:
                terminal_reward = 0.0
                draws += 1

            # Add shaping rewards from trajectories
            traj = result["trajectories"]
            if traj:
                current_traj = traj[current_slot]
                for i, step in enumerate(current_traj):
                    if i < len(current_exp):
                        current_exp[i].reward += step["reward"]

            # Add terminal reward to last experience
            if current_exp:
                current_exp[-1].reward += terminal_reward
                current_exp[-1].done = True

            all_experiences.extend(current_exp)

        stats = {
            "wins": wins,
            "losses": losses,
            "draws": draws,
            "win_rate": wins / max(1, wins + losses + draws),
            "avg_score": np.mean(total_scores) if total_scores else 0,
            "num_experiences": len(all_experiences),
        }

        return {"experiences": all_experiences, "stats": stats}

    def compute_advantages(self, experiences: List[Experience]) -> tuple:
        """
        Compute GAE advantages and returns.
        """
        n = len(experiences)
        if n == 0:
            return np.array([]), np.array([])

        rewards = np.array([e.reward for e in experiences])
        values = np.array([e.value for e in experiences])
        dones = np.array([e.done for e in experiences])

        advantages = np.zeros(n, dtype=np.float32)
        returns = np.zeros(n, dtype=np.float32)

        gae = 0.0
        next_value = 0.0

        for t in reversed(range(n)):
            if dones[t]:
                next_value = 0.0
                gae = 0.0

            delta = rewards[t] + self.config.gamma * next_value * (1 - dones[t]) - values[t]
            gae = delta + self.config.gamma * self.config.gae_lambda * (1 - dones[t]) * gae
            advantages[t] = gae
            returns[t] = advantages[t] + values[t]
            next_value = values[t]

        return advantages, returns

    def ppo_update(self, experiences: List[Experience], advantages: np.ndarray, returns: np.ndarray):
        """Run PPO update epochs on collected experience."""
        n = len(experiences)
        if n == 0:
            return {}

        # Convert to tensors
        states = torch.FloatTensor(np.array([e.state for e in experiences])).to(self.device)
        actions = torch.LongTensor(np.array([e.action for e in experiences])).to(self.device)
        action_masks = torch.FloatTensor(np.array([e.action_mask for e in experiences])).to(self.device)
        old_log_probs = torch.FloatTensor(np.array([e.log_prob for e in experiences])).to(self.device)
        advantages_t = torch.FloatTensor(advantages).to(self.device)
        returns_t = torch.FloatTensor(returns).to(self.device)

        # Normalize advantages
        if len(advantages_t) > 1:
            advantages_t = (advantages_t - advantages_t.mean()) / (advantages_t.std() + 1e-8)

        # Check for NaNs in inputs or weights
        has_nan_weights = any(torch.isnan(p).any() for p in self.policy.parameters())
        if torch.isnan(states).any() or torch.isnan(actions).any() or torch.isnan(old_log_probs).any() or has_nan_weights:
            print("WARNING: NaN detected in PPO batch or weights! Skipping update.")
            if has_nan_weights: print("  -> Policy weights contain NaN!")
            return {}

        total_policy_loss = 0.0
        total_value_loss = 0.0
        total_entropy = 0.0
        update_count = 0

        for _ in range(self.config.ppo_epochs):
            # Mini-batch iteration
            indices = np.arange(n)
            np.random.shuffle(indices)

            for start in range(0, n, self.config.mini_batch_size):
                end = min(start + self.config.mini_batch_size, n)
                mb_idx = indices[start:end]

                mb_states = states[mb_idx]
                mb_actions = actions[mb_idx]
                mb_masks = action_masks[mb_idx]
                mb_old_log_probs = old_log_probs[mb_idx]
                mb_advantages = advantages_t[mb_idx]
                mb_returns = returns_t[mb_idx]

                # Evaluate actions with current policy
                new_log_probs, entropy, values = self.policy.evaluate_actions(
                    mb_states, mb_actions, mb_masks
                )

                # PPO clipped objective
                ratio = torch.exp(new_log_probs - mb_old_log_probs)
                surr1 = ratio * mb_advantages
                surr2 = torch.clamp(ratio, 1 - self.config.clip_epsilon, 1 + self.config.clip_epsilon) * mb_advantages
                policy_loss = -torch.min(surr1, surr2).mean()

                # Value loss
                value_loss = F.mse_loss(values, mb_returns)

                # Entropy bonus
                entropy_loss = -entropy.mean()

                # Total loss
                loss = (
                    policy_loss
                    + self.config.value_loss_coef * value_loss
                    + self.config.entropy_coef * entropy_loss
                )

                self.optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.policy.parameters(), self.config.max_grad_norm)
                self.optimizer.step()

                total_policy_loss += policy_loss.item()
                total_value_loss += value_loss.item()
                total_entropy += entropy.mean().item()
                update_count += 1

        self.writer.add_scalar("Loss/Policy", total_policy_loss / max(1, update_count), self.episode_count)
        self.writer.add_scalar("Loss/Value", total_value_loss / max(1, update_count), self.episode_count)
        self.writer.add_scalar("Loss/Entropy", total_entropy / max(1, update_count), self.episode_count)

        return {
            "policy_loss": total_policy_loss / max(1, update_count),
            "value_loss": total_value_loss / max(1, update_count),
            "entropy": total_entropy / max(1, update_count),
        }

    def evaluate_vs_heuristic(self, num_games: int = 100) -> Dict:
        """
        Evaluate current policy against the heuristic AI.
        Uses the existing AIPlayer hard mode logic.
        """
        from app.core.ai_player import AIPlayer

        wins = 0
        losses = 0
        draws = 0
        scores = []

        for i in range(num_games):
            self.simulator.reset()

            # RL plays slot 0, heuristic plays slot 1 (alternate to be fair)
            rl_slot = i % 2
            heuristic_slot = 1 - rl_slot

            # Create heuristic policy
            heuristic_player = AIPlayer("Heuristic", heuristic_slot, difficulty="hard")

            def heuristic_policy(sim, player_id, valid_actions, stage):
                """Wrap heuristic AI to work with simulator interface."""
                # Build available moves list for the heuristic
                from app.training.simulator import action_to_color_number
                available_moves = []
                for a in valid_actions:
                    if a != 44:
                        result = action_to_color_number(a)
                        if result:
                            available_moves.append(result)

                if not available_moves:
                    return 44  # skip

                # Update heuristic player's scoresheet to match simulator
                heuristic_player.scoresheet = sim.players[player_id].scoresheet

                # Create a minimal game-like object for the heuristic
                game_proxy = _HeuristicGameProxy(sim, player_id)
                move = heuristic_player._make_hard_decision(game_proxy, available_moves)

                if move is None:
                    return 44

                color, number = move
                return color_number_to_action(color, number)

            rl_policy = self.make_policy_fn(self.policy)

            fns = [None, None]
            fns[rl_slot] = rl_policy
            fns[heuristic_slot] = heuristic_policy

            result = self.simulator.rollout(fns[0], fns[1])
            winner = result["winner"]
            game_scores = result["scores"]
            scores.append(game_scores[rl_slot])

            if winner == rl_slot:
                wins += 1
            elif winner == heuristic_slot:
                losses += 1
            else:
                draws += 1

        return {
            "wins": wins,
            "losses": losses,
            "draws": draws,
            "win_rate": wins / max(1, num_games),
            "avg_score": np.mean(scores) if scores else 0,
        }

    def save_model(self, path: str):
        """Save model weights."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save({
            "model_state_dict": self.policy.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "episode_count": self.episode_count,
            "best_win_rate": self.best_win_rate,
            "config": self.config,
        }, path)

    def load_model(self, path: str):
        """Load model weights."""
        checkpoint = torch.load(path, map_location=self.device, weights_only=False)
        self.policy.load_state_dict(checkpoint["model_state_dict"])
        if "optimizer_state_dict" in checkpoint:
            self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        if "episode_count" in checkpoint:
            self.episode_count = checkpoint["episode_count"]
        if "best_win_rate" in checkpoint:
            self.best_win_rate = checkpoint["best_win_rate"]

    def _get_entropy_coef(self, progress: float) -> float:
        """Anneal entropy coefficient from entropy_coef to entropy_coef_min over training."""
        start = self.config.entropy_coef
        end = self.config.entropy_coef_min
        return end + (start - end) * (1.0 - progress)

    def _update_lr(self, progress: float):
        """Cosine annealing learning rate schedule."""
        import math
        lr_max = self.config.lr
        lr_min = self.config.lr_min
        lr = lr_min + 0.5 * (lr_max - lr_min) * (1 + math.cos(math.pi * progress))
        for param_group in self.optimizer.param_groups:
            param_group['lr'] = lr
        return lr

    def train(self, total_episodes: int = None, eval_interval: int = None, callback=None):
        """
        Main training loop.

        Args:
            total_episodes: Override config total episodes
            eval_interval: Override config eval interval
            callback: Optional function called each batch with stats
        """
        total = total_episodes or self.config.total_episodes
        eval_every = eval_interval or self.config.eval_interval

        print(f"Starting PPO training for {total} episodes on {self.device}")
        print(f"Batch size: {self.config.episodes_per_batch}, Eval every: {eval_every}")
        print(f"LR: {self.config.lr} → {self.config.lr_min} (cosine)")
        print(f"Entropy: {self.config.entropy_coef} → {self.config.entropy_coef_min} (linear)")
        if self.episode_count > 0:
            print(f"Resuming from episode {self.episode_count}")
        print()

        while self.episode_count < total:
            # Compute training progress (0→1) for schedules
            progress = min(1.0, self.episode_count / total)

            # Update schedules
            current_lr = self._update_lr(progress)
            current_entropy = self._get_entropy_coef(progress)
            self.config.entropy_coef = current_entropy

            # Collect experience
            batch = self.collect_batch()
            experiences = batch["experiences"]
            stats = batch["stats"]

            # Compute advantages
            advantages, returns = self.compute_advantages(experiences)

            # PPO update
            loss_stats = self.ppo_update(experiences, advantages, returns)

            self.episode_count += self.config.episodes_per_batch

            # Log progress
            print(
                f"Episode {self.episode_count:>6d}/{total} | "
                f"Win: {stats['win_rate']:.1%} | "
                f"Score: {stats['avg_score']:>6.1f} | "
                f"PL: {loss_stats.get('policy_loss', 0):.4f} | "
                f"VL: {loss_stats.get('value_loss', 0):.4f} | "
                f"Ent: {loss_stats.get('entropy', 0):.4f} | "
                f"LR: {current_lr:.1e}"
            )

            # TensorBoard metrics
            self.writer.add_scalar("Game/WinRate_Batch", stats['win_rate'], self.episode_count)
            self.writer.add_scalar("Game/AvgScore_Batch", stats['avg_score'], self.episode_count)
            self.writer.add_scalar("Game/NumExperiences", stats['num_experiences'], self.episode_count)
            self.writer.add_scalar("Schedule/LR", current_lr, self.episode_count)
            self.writer.add_scalar("Schedule/EntropyCoef", current_entropy, self.episode_count)

            # Update frozen opponent periodically
            if self.episode_count % self.config.opponent_update_interval < self.config.episodes_per_batch:
                self.opponent.load_state_dict(self.policy.state_dict())
                print("  → Updated frozen opponent")

            # Evaluate against heuristic
            if self.episode_count % eval_every < self.config.episodes_per_batch:
                eval_stats = self.evaluate_vs_heuristic(self.config.eval_games)
                print(
                    f"  ★ Eval vs Hard AI: {eval_stats['win_rate']:.1%} win rate "
                    f"({eval_stats['wins']}W/{eval_stats['losses']}L/{eval_stats['draws']}D) "
                    f"avg score: {eval_stats['avg_score']:.1f}"
                )

                # Save best model
                if eval_stats["win_rate"] > self.best_win_rate:
                    self.best_win_rate = eval_stats["win_rate"]
                    self.save_model(self.config.best_model_path)
                    print(f"  ✓ New best model saved (win rate: {self.best_win_rate:.1%})")

                self.writer.add_scalar("Eval/WinRate", eval_stats['win_rate'], self.episode_count)
                self.writer.add_scalar("Eval/AvgScore", eval_stats['avg_score'], self.episode_count)

            # Periodic save
            if self.episode_count % self.config.save_interval < self.config.episodes_per_batch:
                path = os.path.join(self.config.model_dir, f"checkpoint_{self.episode_count}.pt")
                self.save_model(path)

            if callback:
                callback({**stats, **loss_stats, "episode": self.episode_count})

        print(f"\nTraining complete. Best win rate: {self.best_win_rate:.1%}")
        self.save_model(os.path.join(self.config.model_dir, "final_model.pt"))


class _HeuristicGameProxy:
    """Minimal proxy that makes a simulator look like a Game for heuristic AI."""

    def __init__(self, sim: QwixxSimulator, player_id: int):
        self.sim = sim
        self._player_id = player_id

    def get_players(self):
        return [_HeuristicPlayerProxy(p) for p in self.sim.players]

    def get_current_player(self):
        return _HeuristicPlayerProxy(self.sim.players[self.sim.current_player_idx])

    def get_locked_colors(self):
        return self.sim.locked_colors

    def get_dice_results(self):
        return self.sim.dice_results


class _HeuristicPlayerProxy:
    """Minimal proxy that makes a SimPlayer look like a Player for heuristic AI."""

    def __init__(self, sim_player: 'SimPlayer'):
        self.sim_player = sim_player
        self.scoresheet = sim_player.scoresheet

    def get_scoresheet(self):
        return self.sim_player.scoresheet

    def get_name(self):
        return f"Player {self.sim_player.player_id}"

    def __eq__(self, other):
        if isinstance(other, _HeuristicPlayerProxy):
            return self.sim_player.player_id == other.sim_player.player_id
        return False

    def __ne__(self, other):
        return not self.__eq__(other)
