# Qwixx RL Training Plan v2

## Executive Summary
The goal of this plan is to evolve the existing Qwixx RL framework from a functional prototype into a high-performance AI that consistently outperforms the hard heuristic AI and provides a challenging experience for human players.

## Current State Analysis
- **Strengths**: Robust PPO implementation, fast simulator, and clear integration into the `AIPlayer` class.
- **Weaknesses**: Sparse rewards (currently just +0.1 per mark), potential state-encoding discrepancies between training and inference, and lack of vectorized training for speed.

## Proposed Improvements & Phases

### Phase 1: Architectural Alignment & Infrastructure
*   **Unified State Encoding**: Refactor `AIPlayer._encode_game_state_for_rl` to use `app.training.state_encoder.encode_state` directly. This ensures the model sees exactly the same feature space during inference as it did during training.
*   **TensorBoard Integration**: Add `torch.utils.tensorboard.SummaryWriter` to `PPOTrainer` to track:
    *   Cumulative reward per episode.
    *   Policy and Value loss.
    *   Entropy (to monitor exploration).
    *   Win rate against the frozen opponent and heuristic AI.
*   **Justfile Integration**: Add `just train-rl` and `just eval-rl` commands to the root `justfile`.

### Phase 2: Advanced Reward Shaping
*   **Score Differential Reward**: Instead of just `+0.1` per mark, add a reward component based on the change in score difference: `(MyScore_t - OpponentScore_t) - (MyScore_{t-1} - OpponentScore_{t-1})`.
*   **Flexibility Penalty**: Penalize "big jumps" in a row. If marking a number skips $N$ available numbers, apply a penalty proportional to $N$. This teaches the agent to preserve future options.
*   **Row Completion Bonus**: Exponentially increase the reward for marks as a row approaches 5 marks (towards locking).
*   **Penalty Avoidance**: Increase the negative reward for taking a penalty if it's the 3rd or 4th penalty (approaching game over).

### Phase 3: State Representation 2.0
*   **Dead Number Bitmask**: Add a 44-bit vector (4 colors x 11 numbers) indicating which slots are physically impossible to mark based on current progress.
*   **Game Progress Feature**: Add a feature for `turn_count / max_turns` to help the agent distinguish between early-game and end-game strategies.
*   **Lock Status**: Ensure the 123-feature vector explicitly includes whether each color is currently locked by *any* player.

### Phase 4: Training Efficiency (Scale)
*   **Vectorized Environments**: Implement a `BatchedSimulator` or use `multiprocessing` to collect trajectories from multiple games in parallel. This is the single biggest bottleneck for scaling to 1M+ episodes.
*   **Mixed Precision Training**: Use `torch.cuda.amp` (if GPU available) to speed up updates.
*   **Curriculum Learning**: Start training against a random agent, then move to "Medium" AI, then "Hard" AI, and finally pure self-play.

### Phase 5: Deployment & Integration
*   **Model Exporting**: Add a script to export the best model to a versioned folder `backend/app/training/models/v2/...`.
*   **Game AI Integration**: Ensure the "RL" difficulty is functional in the React dashboard by calling the backend API which runs the model.
*   **Inference Optimization**: Cache the model in `AIPlayer` to avoid reloading on every move.
*   **Note**: All training, evaluation, and monitoring (TensorBoard) are CLI-driven and independent of the web frontend.

## Implementation Roadmap

### Milestone 1: The "Clean" Baseline (Estimated: 2 days)
- [ ] Sync state encoding between `AIPlayer` and `trainer`.
- [ ] Add TensorBoard logging.
- [ ] Run a 50k episode baseline with current rewards and log the results.

### Milestone 2: Reward & State Tuning (Estimated: 3 days)
- [ ] Implement Score Differential and Flexibility Penalty.
- [ ] Add "Dead Number" features to `state_encoder`.
- [ ] Compare win rates against Milestone 1 baseline.

### Milestone 3: Scaling Up (Estimated: 2 days)
- [ ] Implement vectorized game collection.
- [ ] Run a long-form training run (200k-500k episodes).
- [ ] Final evaluation against "Hard" AI (Target: 70%+ win rate).

## Open Questions
- **Action Selection**: Should we use "Greedy" (highest prob) or "Stochastic" (sampling) during production inference? Sampling might feel more "human" but greedy is typically stronger.
- **Compute**: Is there a specific machine (GPU vs CPU) this is intended to run on? Vectorization strategy depends on this.

## Success Criteria
- RL Agent defeats "Hard" Heuristic AI in >65% of games over 1000 trials.
- Training pipeline produces clear TensorBoard graphs showing convergence.
- Zero discrepancies between training and inference state encoding.
