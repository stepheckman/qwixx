"""
Actor-Critic neural network for Qwixx RL agent.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple

from .config import TrainingConfig


class QwixxNet(nn.Module):
    """
    Actor-Critic network with shared backbone.
    - Policy head: outputs action logits (masked for valid actions)
    - Value head: outputs state value estimate
    """

    def __init__(self, config: TrainingConfig = None):
        super().__init__()
        if config is None:
            config = TrainingConfig()

        self.state_size = config.state_size
        self.action_size = config.action_size

        # Shared backbone
        self.shared = nn.Sequential(
            nn.Linear(config.state_size, config.hidden_size),
            nn.ReLU(),
            nn.Linear(config.hidden_size, config.hidden_size_2),
            nn.ReLU(),
        )

        # Policy head
        self.policy_head = nn.Sequential(
            nn.Linear(config.hidden_size_2, 64),
            nn.ReLU(),
            nn.Linear(64, config.action_size),
        )

        # Value head
        self.value_head = nn.Sequential(
            nn.Linear(config.hidden_size_2, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )

    def forward(
        self, state: torch.Tensor, action_mask: torch.Tensor = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass.

        Args:
            state: batch of state vectors [B, state_size]
            action_mask: batch of valid action masks [B, action_size], 1=valid, 0=invalid

        Returns:
            (action_logits, state_value) - logits are masked, value is scalar
        """
        features = self.shared(state)

        # Policy
        logits = self.policy_head(features)
        if action_mask is not None:
            # Set invalid actions to -inf so softmax gives them 0 probability
            logits = logits.masked_fill(action_mask == 0, float("-inf"))

        # Value
        value = self.value_head(features).squeeze(-1)

        return logits, value

    def get_action_and_value(
        self, state: torch.Tensor, action_mask: torch.Tensor
    ) -> Tuple[int, float, float, float]:
        """
        Sample an action and return action, log_prob, entropy, value.
        For single state (no batch dim).
        """
        with torch.no_grad():
            logits, value = self.forward(
                state.unsqueeze(0), action_mask.unsqueeze(0)
            )
            logits = logits.squeeze(0)
            value = value.squeeze(0)

            # Handle case where all actions are masked (shouldn't happen with skip)
            if torch.all(logits == float("-inf")):
                return 44, 0.0, 0.0, value.item()  # force skip

            probs = F.softmax(logits, dim=-1)
            dist = torch.distributions.Categorical(probs)
            action = dist.sample()

            return action.item(), dist.log_prob(action).item(), dist.entropy().item(), value.item()

    def evaluate_actions(
        self,
        states: torch.Tensor,
        actions: torch.Tensor,
        action_masks: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Evaluate actions for PPO update.

        Returns:
            (log_probs, entropy, values)
        """
        logits, values = self.forward(states, action_masks)

        # Clamp logits to avoid numerical issues
        probs = F.softmax(logits, dim=-1)
        # Add tiny epsilon to prevent log(0)
        probs = probs.clamp(min=1e-8)
        dist = torch.distributions.Categorical(probs)

        log_probs = dist.log_prob(actions)
        entropy = dist.entropy()

        return log_probs, entropy, values
