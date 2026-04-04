"""
CLI for training, evaluating, and watching the RL Qwixx agent.

Usage:
    python -m app.training.play train [--episodes N] [--eval-interval N]
    python -m app.training.play evaluate [--model PATH] [--games N]
    python -m app.training.play watch [--model PATH]
"""

import argparse
import sys
import os

# Ensure backend is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def cmd_train(args):
    from app.training.config import TrainingConfig
    from app.training.trainer import PPOTrainer

    config = TrainingConfig()
    if args.lr:
        config.lr = args.lr
    if args.batch_size:
        config.episodes_per_batch = args.batch_size

    trainer = PPOTrainer(config)

    if args.resume:
        print(f"Resuming from {args.resume}")
        trainer.load_model(args.resume)

    trainer.train(
        total_episodes=args.episodes,
        eval_interval=args.eval_interval,
    )


def cmd_evaluate(args):
    from app.training.config import TrainingConfig
    from app.training.trainer import PPOTrainer

    config = TrainingConfig()
    trainer = PPOTrainer(config)

    model_path = args.model or config.best_model_path
    if os.path.exists(model_path):
        trainer.load_model(model_path)
        print(f"Loaded model from {model_path}")
    else:
        print(f"No model found at {model_path}, evaluating random policy")

    print(f"\nEvaluating against Hard AI over {args.games} games...")
    stats = trainer.evaluate_vs_heuristic(args.games)
    print(f"\nResults:")
    print(f"  Win rate: {stats['win_rate']:.1%}")
    print(f"  Wins: {stats['wins']}, Losses: {stats['losses']}, Draws: {stats['draws']}")
    print(f"  Average score: {stats['avg_score']:.1f}")


def cmd_watch(args):
    """Watch a single game between RL agent and heuristic AI."""
    from app.training.config import TrainingConfig
    from app.training.trainer import PPOTrainer
    from app.training.simulator import QwixxSimulator, action_to_color_number

    config = TrainingConfig()
    trainer = PPOTrainer(config)

    model_path = args.model or config.best_model_path
    if os.path.exists(model_path):
        trainer.load_model(model_path)
        print(f"Loaded model from {model_path}")
    else:
        print(f"No model found at {model_path}, watching random policy")

    sim = QwixxSimulator()
    sim.reset()

    from app.core.ai_player import AIPlayer
    from app.training.trainer import _HeuristicGameProxy, color_number_to_action

    heuristic_player = AIPlayer("Heuristic", 1, difficulty="hard")

    def rl_policy(s, pid, valid, stage):
        action = trainer.make_policy_fn(trainer.policy)(s, pid, valid, stage)
        move = action_to_color_number(action)
        move_str = f"{move[0].value} {move[1]}" if move else "skip"
        print(f"  [RL P{pid}] Stage {stage}: {move_str}")
        return action

    def heuristic_policy(s, pid, valid, stage):
        available_moves = []
        for a in valid:
            if a != 44:
                result = action_to_color_number(a)
                if result:
                    available_moves.append(result)

        if not available_moves:
            print(f"  [AI P{pid}] Stage {stage}: skip (no moves)")
            return 44

        heuristic_player.scoresheet = s.players[pid].scoresheet
        game_proxy = _HeuristicGameProxy(s, pid)
        move = heuristic_player._make_hard_decision(game_proxy, available_moves)

        if move is None:
            print(f"  [AI P{pid}] Stage {stage}: skip")
            return 44

        color, number = move
        print(f"  [AI P{pid}] Stage {stage}: {color.value} {number}")
        return color_number_to_action(color, number)

    # RL is player 0, Heuristic is player 1
    print("\n=== Qwixx: RL Agent (P0) vs Hard AI (P1) ===\n")
    result = sim.rollout(rl_policy, heuristic_policy)

    scores = result["scores"]
    winner = result["winner"]
    print(f"\n=== Game Over (Turn {result['turn_count']}) ===")
    print(f"  RL Agent score: {scores[0]}")
    print(f"  Hard AI score:  {scores[1]}")
    if winner == 0:
        print("  Winner: RL Agent!")
    elif winner == 1:
        print("  Winner: Hard AI")
    else:
        print("  Draw!")


def main():
    parser = argparse.ArgumentParser(description="Qwixx RL Training CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Train
    train_parser = subparsers.add_parser("train", help="Train the RL agent via self-play")
    train_parser.add_argument("--episodes", type=int, default=50000, help="Total training episodes")
    train_parser.add_argument("--eval-interval", type=int, default=1000, help="Evaluate every N episodes")
    train_parser.add_argument("--resume", type=str, default=None, help="Resume from checkpoint")
    train_parser.add_argument("--lr", type=float, default=None, help="Learning rate")
    train_parser.add_argument("--batch-size", type=int, default=None, help="Episodes per batch")

    # Evaluate
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate model vs heuristic AI")
    eval_parser.add_argument("--model", type=str, default=None, help="Model path")
    eval_parser.add_argument("--games", type=int, default=500, help="Number of games")

    # Watch
    watch_parser = subparsers.add_parser("watch", help="Watch a single game")
    watch_parser.add_argument("--model", type=str, default=None, help="Model path")

    args = parser.parse_args()

    if args.command == "train":
        cmd_train(args)
    elif args.command == "evaluate":
        cmd_evaluate(args)
    elif args.command == "watch":
        cmd_watch(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
