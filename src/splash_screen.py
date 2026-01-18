"""
Splash screen for player selection in the Qwixx game.
"""

import pygame
from typing import Optional
from .gui import Button, COLORS

class SplashScreen:
    """Splash screen for selecting number of players and AI strategy."""
    
    def __init__(self, screen: pygame.Surface):
        """
        Initialize the splash screen.
        
        Args:
            screen: The pygame screen surface
        """
        self.screen = screen
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Center the buttons on screen
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        button_width = 200
        button_height = 60
        
        # Position buttons vertically centered with some spacing
        button_y = screen_height // 2 - 40
        button_spacing = 80
        
        # Create player selection buttons
        self.one_player_button = Button(
            screen_width // 2 - button_width // 2,
            button_y,
            button_width,
            button_height,
            "1 Player",
            COLORS['green']
        )
        
        self.two_player_button = Button(
            screen_width // 2 - button_width // 2,
            button_y + button_spacing,
            button_width,
            button_height,
            "2 Players",
            COLORS['blue']
        )
        
        # AI strategy selection buttons (shown only when 1 player is selected)
        strategy_button_width = 180
        strategy_button_height = 50
        strategy_y = screen_height // 2 - 60
        strategy_spacing = 70
        
        self.easy_button = Button(
            screen_width // 2 - strategy_button_width // 2,
            strategy_y,
            strategy_button_width,
            strategy_button_height,
            "Easy AI",
            COLORS['green']
        )
        
        self.medium_button = Button(
            screen_width // 2 - strategy_button_width // 2,
            strategy_y + strategy_spacing,
            strategy_button_width,
            strategy_button_height,
            "Medium AI",
            COLORS['yellow']
        )
        
        self.hard_button = Button(
            screen_width // 2 - strategy_button_width // 2,
            strategy_y + strategy_spacing * 2,
            strategy_button_width,
            strategy_button_height,
            "Hard AI",
            COLORS['red']
        )
        
        # Back button for AI strategy selection screen
        self.back_button = Button(
            50,
            screen_height - 100,
            100,
            40,
            "Back",
            COLORS['gray']
        )
        
        self.selected_players: Optional[int] = None
        self.selected_ai_strategy: Optional[str] = None
        self.show_ai_selection: bool = False
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events for the splash screen.
        
        Args:
            event: The pygame event to handle
            
        Returns:
            True if a selection was made, False otherwise
        """
        if not self.show_ai_selection:
            # Player count selection screen
            if self.one_player_button.handle_event(event):
                self.selected_players = 1
                self.show_ai_selection = True
                return False  # Don't complete selection yet, need AI strategy
            
            if self.two_player_button.handle_event(event):
                self.selected_players = 2
                self.selected_ai_strategy = None  # No AI needed for 2 players
                return True  # Complete selection
            
            # Handle hover effects
            if event.type == pygame.MOUSEMOTION:
                self.one_player_button.handle_event(event)
                self.two_player_button.handle_event(event)
        
        else:
            # AI strategy selection screen
            if self.easy_button.handle_event(event):
                self.selected_ai_strategy = "easy"
                return True  # Complete selection
            
            if self.medium_button.handle_event(event):
                self.selected_ai_strategy = "medium"
                return True  # Complete selection
            
            if self.hard_button.handle_event(event):
                self.selected_ai_strategy = "hard"
                return True  # Complete selection
            
            if self.back_button.handle_event(event):
                self.show_ai_selection = False
                self.selected_players = None
                return False
            
            # Handle hover effects
            if event.type == pygame.MOUSEMOTION:
                self.easy_button.handle_event(event)
                self.medium_button.handle_event(event)
                self.hard_button.handle_event(event)
                self.back_button.handle_event(event)
        
        return False
    
    def draw(self) -> None:
        """Draw the splash screen."""
        # Clear screen with a nice background
        self.screen.fill(COLORS['background'])
        
        # Draw title
        title_text = self.font_large.render("QWIXX", True, COLORS['black'])
        title_rect = title_text.get_rect(center=(self.screen.get_width() // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        if not self.show_ai_selection:
            # Player count selection screen
            # Draw subtitle
            subtitle_text = self.font_medium.render("Choose Number of Players", True, COLORS['dark_gray'])
            subtitle_rect = subtitle_text.get_rect(center=(self.screen.get_width() // 2, 200))
            self.screen.blit(subtitle_text, subtitle_rect)
            
            # Draw description for single player
            desc1_text = self.font_small.render("1 Player: You vs AI", True, COLORS['gray'])
            desc1_rect = desc1_text.get_rect(center=(self.screen.get_width() // 2, 320))
            self.screen.blit(desc1_text, desc1_rect)
            
            # Draw description for two players
            desc2_text = self.font_small.render("2 Players: Local multiplayer", True, COLORS['gray'])
            desc2_rect = desc2_text.get_rect(center=(self.screen.get_width() // 2, 400))
            self.screen.blit(desc2_text, desc2_rect)
            
            # Draw buttons
            self.one_player_button.draw(self.screen)
            self.two_player_button.draw(self.screen)
        
        else:
            # AI strategy selection screen
            # Draw subtitle
            subtitle_text = self.font_medium.render("Choose AI Difficulty", True, COLORS['dark_gray'])
            subtitle_rect = subtitle_text.get_rect(center=(self.screen.get_width() // 2, 200))
            self.screen.blit(subtitle_text, subtitle_rect)
            
            # Draw strategy descriptions
            easy_desc = self.font_small.render("Easy: Makes random moves, sometimes skips turns", True, COLORS['gray'])
            easy_rect = easy_desc.get_rect(center=(self.screen.get_width() // 2, 280))
            self.screen.blit(easy_desc, easy_rect)
            
            medium_desc = self.font_small.render("Medium: Uses basic strategy, good for beginners", True, COLORS['gray'])
            medium_rect = medium_desc.get_rect(center=(self.screen.get_width() // 2, 360))
            self.screen.blit(medium_desc, medium_rect)
            
            hard_desc = self.font_small.render("Hard: Advanced strategy with look-ahead, challenging", True, COLORS['gray'])
            hard_rect = hard_desc.get_rect(center=(self.screen.get_width() // 2, 440))
            self.screen.blit(hard_desc, hard_rect)
            
            # Draw strategy buttons
            self.easy_button.draw(self.screen)
            self.medium_button.draw(self.screen)
            self.hard_button.draw(self.screen)
            self.back_button.draw(self.screen)
    
    def get_selected_players(self) -> Optional[int]:
        """Get the number of players selected."""
        return self.selected_players
    
    def get_selected_ai_strategy(self) -> Optional[str]:
        """Get the selected AI strategy."""
        return self.selected_ai_strategy