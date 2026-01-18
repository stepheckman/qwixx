"""
Logging configuration for the Qwixx game using loguru.
"""

import sys
from pathlib import Path
from loguru import logger

def setup_logging():
    """
    Configure loguru logging for the Qwixx game.
    
    Sets up both console and file logging with appropriate formatting.
    """
    # Remove default handler
    logger.remove()
    
    # Add console handler with colored output
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Add file handler for game logs
    logger.add(
        logs_dir / "qwixx_game.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )
    
    # Add separate file for game events (structured logging)
    logger.add(
        logs_dir / "qwixx_events.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {extra[event_type]} | {message}",
        level="INFO",
        filter=lambda record: "event_type" in record["extra"],
        rotation="5 MB",
        retention="14 days"
    )
    
    return logger

def get_game_logger():
    """Get a logger instance for game events."""
    return logger.bind(name="qwixx.game")

def get_player_logger():
    """Get a logger instance for player events."""
    return logger.bind(name="qwixx.player")

def get_ai_logger():
    """Get a logger instance for AI events."""
    return logger.bind(name="qwixx.ai")

def get_dice_logger():
    """Get a logger instance for dice events."""
    return logger.bind(name="qwixx.dice")

def log_game_event(event_type: str, message: str, **kwargs):
    """
    Log a structured game event.
    
    Args:
        event_type: Type of event (e.g., 'GAME_START', 'DICE_ROLL', 'PLAYER_MOVE')
        message: Event message
        **kwargs: Additional event data
    """
    event_logger = logger.bind(event_type=event_type, **kwargs)
    event_logger.info(message)

def log_player_decision(player_name: str, stage: int, action: str, details: dict = None):
    """
    Log a player decision with structured data.
    
    Args:
        player_name: Name of the player making the decision
        stage: Game stage (1 or 2)
        action: Action taken (e.g., 'MARK', 'PASS', 'DONE')
        details: Additional details about the decision
    """
    details = details or {}
    log_game_event(
        "PLAYER_DECISION",
        f"{player_name} in stage {stage}: {action}",
        player=player_name,
        stage=stage,
        action=action,
        **details
    )

def log_dice_roll(dice_results: dict):
    """
    Log dice roll results with structured data.
    
    Args:
        dice_results: Dictionary containing dice roll results
    """
    log_game_event(
        "DICE_ROLL",
        f"Dice rolled: {dice_results}",
        **dice_results
    )

def log_game_state_change(old_state: str, new_state: str, context: str = ""):
    """
    Log game state transitions.
    
    Args:
        old_state: Previous game state
        new_state: New game state
        context: Additional context about the state change
    """
    log_game_event(
        "STATE_CHANGE",
        f"Game state: {old_state} -> {new_state}" + (f" ({context})" if context else ""),
        old_state=old_state,
        new_state=new_state,
        context=context
    )