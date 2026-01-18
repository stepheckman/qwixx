#!/usr/bin/env python3
"""
Qwixx - A Python implementation of the dice game Qwixx using Pygame.
"""

import pygame
import sys
from src.game import Game
from src.splash_screen import SplashScreen
from src.logger import setup_logging, get_game_logger, log_game_event

def main():
    """Main entry point for the Qwixx game."""
    # Initialize logging
    setup_logging()
    game_logger = get_game_logger()
    
    game_logger.info("Starting Qwixx game application")
    log_game_event("APP_START", "Qwixx application started")
    
    # Initialize Pygame
    pygame.init()
    
    # Set up the display
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("Qwixx")
    
    # Create clock for controlling frame rate
    clock = pygame.time.Clock()
    
    # Show splash screen first
    splash = SplashScreen(screen)
    game = None
    show_splash = True
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                if show_splash:
                    # Handle splash screen events
                    if splash.handle_event(event):
                        # Player selection made, create game
                        num_players = splash.get_selected_players()
                        ai_strategy = splash.get_selected_ai_strategy()
                        
                        game_logger.info(f"Creating new game with {num_players} players, AI strategy: {ai_strategy}")
                        log_game_event(
                            "GAME_INIT",
                            f"New game created with {num_players} players",
                            num_players=num_players,
                            ai_strategy=ai_strategy
                        )
                        
                        game = Game(screen, num_players, ai_strategy)
                        show_splash = False
                else:
                    # Handle game events
                    game.handle_event(event)
        
        # Update and draw
        if show_splash:
            splash.draw()
        else:
            # Update game state
            game.update()
            
            # Draw everything
            game.draw()
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(60)
    
    # Quit
    game_logger.info("Qwixx application shutting down")
    log_game_event("APP_SHUTDOWN", "Qwixx application shutdown")
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()