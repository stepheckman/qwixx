"""
Training hyperparameters and configuration.
"""

from dataclasses import dataclass


@dataclass
class TrainingConfig:
    # Network architecture
    state_size: int = 172
    action_size: int = 45  # 4 colors × 11 numbers + 1 skip
    hidden_size: int = 256
    hidden_size_2: int = 128

    # PPO hyperparameters
    lr: float = 3e-4
    gamma: float = 0.99  # Discount factor
    gae_lambda: float = 0.95  # GAE lambda
    clip_epsilon: float = 0.2  # PPO clipping
    value_loss_coef: float = 0.5
    entropy_coef: float = 0.01  # Entropy bonus for exploration
    max_grad_norm: float = 0.5

    # Training loop
    episodes_per_batch: int = 64
    ppo_epochs: int = 4
    mini_batch_size: int = 32
    total_episodes: int = 50000
    eval_interval: int = 1000
    eval_games: int = 100
    save_interval: int = 5000

    # Self-play
    opponent_update_interval: int = 2000  # Freeze opponent copy every N episodes

    # Reward shaping
    win_reward: float = 1.0
    lose_reward: float = -1.0
    mark_reward: float = 0.1
    penalty_reward: float = -0.2
    lock_reward: float = 0.5

    # Paths
    model_dir: str = "app/training/models"
    best_model_path: str = "app/training/models/best_model.pt"
    run_name: str = "ppo_qwixx_v2"
