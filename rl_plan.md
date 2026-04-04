# Qwixx RL Training Completion Plan

## Current State Summary

The project has a **well-developed RL training framework** already in place:

**Existing Components (in `backend/app/training/`):**
- `config.py` - Training hyperparameters and paths
- `model.py` - Actor-Critic neural network (`QwixxNet`) with policy and value heads
- `state_encoder.py` - Game state encoding (123 features) and action masking
- `simulator.py` - Fast headless game simulator for self-play
- `trainer.py` - Full PPO trainer with GAE, self-play, opponent freezing, and heuristic evaluation
- `play.py` - CLI for train/evaluate/watch commands
- `models/` - Empty directory ready for saved models

**Integration Points:**
- `backend/app/core/ai_player.py` - Has `difficulty="rl"` option and `_make_rl_decision()` method (lines 187-224)
- `backend/requirements.txt` - Already includes `torch>=2.0.0`

## What's Already Working

1. PPO algorithm with clipped objective, value loss, entropy bonus
2. Self-play training with frozen opponent periodically updated
3. GAE (Generalized Advantage Estimation) for advantage computation
4. Reward shaping (mark=+0.1, lock=+0.5, penalty=-0.2, win=+1.0, lose=-1.0)
5. Evaluation against heuristic AI with win rate tracking
6. Model checkpointing (best and periodic)
7. RL difficulty option in AIPlayer (with fallback to hard if model not found)

## What Still Needs to be Built

### Phase 1: Training Infrastructure Polish

| Task | Priority | Description |
|------|----------|-------------|
| 1.1 | Medium | Add training progress visualization/logging (tensorboard or simple file logging) |
| 1.2 | Low | Add training curriculum (gradually increase opponent strength) |
| 1.3 | Low | Experiment with different network architectures (larger hidden layers, LSTM for sequence) |

### Phase 2: Reward Function Improvements

| Task | Priority | Description |
|------|----------|-------------|
| 2.1 | High | Add intermediate rewards based on score differential vs opponent |
| 2.2 | High | Add reward for efficient row completion (fewer marks = better) |
| 2.3 | Medium | Tune reward shaping weights based on actual training results |
| 2.4 | Medium | Consider penalty for making opponent's moves better (blocking) |

### Phase 3: State Representation Improvements

| Task | Priority | Description |
|------|----------|-------------|
| 3.1 | Medium | Add historical context (what numbers are "dead" based on marks) |
| 3.2 | Low | Add features for probability of rolling specific numbers |
| 3.3 | Low | Consider one-hot encoding for dice values instead of normalized |

### Phase 4: Training Scale & Efficiency

| Task | Priority | Description |
|------|----------|-------------|
| 4.1 | High | Run actual training runs to generate baseline models |
| 4.2 | Medium | Add vectorized/batched environment support for faster training |
| 4.3 | Medium | Add support for GPU training optimizations |
| 4.4 | Low | Implement population-based training (multiple agents evolving) |

### Phase 5: Integration & Deployment

| Task | Priority | Description |
|------|----------|-------------|
| 5.1 | High | Ensure `difficulty="rl"` works end-to-end in actual game API |
| 5.2 | High | Test RL agent in web frontend vs human players |
| 5.3 | Medium | Add API endpoint to trigger training / check training status |
| 5.4 | Low | Add model versioning and A/B testing between RL versions |

### Phase 6: Analysis & Iteration

| Task | Priority | Description |
|------|----------|-------------|
| 6.1 | Medium | Build analysis tools to understand what the RL agent learned |
| 6.2 | Medium | Compare RL strategies against heuristic strategies |
| 6.3 | Low | Generate "strategy report" showing preferred moves in different states |
| 6.4 | Low | Fine-tune against specific human play patterns |

## Quick Wins to Start Immediately

1. **Run a short training run** (5K-10K episodes) to validate the pipeline works end-to-end
2. **Fix the duplicate AIPlayer files** - `backend/app/game/ai_player.py` appears older than `backend/app/core/ai_player.py`
3. **Add a simple training progress dashboard** - even just a text file with win rates over time
4. **Test RL difficulty in web app** - ensure the trained model can be selected in the frontend

## Recommended Implementation Order

### Week 1: Validation & Baseline
1. Run training for 10K-50K episodes
2. Save baseline model
3. Test RL agent in web game
4. Document initial win rate vs heuristic

### Week 2: Reward Tuning
1. Implement score-differential reward shaping
2. Re-train and compare results
3. Tune hyperparameters based on training stability

### Week 3: Scale & Polish
1. Run longer training (100K+ episodes)
2. Add training visualization
3. Final integration testing

## Training Commands

```bash
# Start training (from backend/ directory)
cd backend
python -m app.training.play train --episodes 50000 --eval-interval 1000

# Evaluate existing model
python -m app.training.play evaluate --games 500

# Watch a game between RL and heuristic AI
python -m app.training.play watch

# Resume from checkpoint
python -m app.training.play train --resume app/training/models/checkpoint_10000.pt --episodes 50000
```

## Open Questions to Resolve

1. What win rate against the heuristic AI is considered "good enough"? (Target: 60%+)
2. Should we train multiple specialized agents (one for each color strategy)?
3. Should RL agent be able to play as either player (position 0 or 1)?
4. How important is interpretability vs raw performance?
5. Should we implement MCTS (Monte Carlo Tree Search) hybrid approach?

## Success Criteria

- [ ] RL agent consistently beats hard heuristic AI (>55% win rate)
- [ ] RL agent can be selected as opponent in web frontend
- [ ] Training pipeline can run unattended and save checkpoints
- [ ] Basic visualization of training progress available
- [ ] RL agent demonstrates non-obvious strategies that humans can learn from

## Files to Modify (in priority order)

1. `backend/app/training/trainer.py` - Add better logging, curriculum
2. `backend/app/training/simulator.py` - Improve reward shaping
3. `backend/app/training/play.py` - Add progress tracking/visualization
4. `backend/app/core/ai_player.py` - Ensure RL integration is robust
5. `backend/app/game/ai_player.py` - Consider deprecating or syncing with core
6. `frontend/` - Add RL option to AI difficulty selector if not present

## Notes

- The training code is already production-quality and well-structured
- The main gap is **running actual training** and **refining based on results**
- PPO is a solid algorithm choice for this discrete action space game
- Self-play approach is appropriate for 2-player zero-sum games like Qwixx
