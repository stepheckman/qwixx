"""
GUI module for the Qwixx game using Pygame.
"""

import pygame
from typing import Dict, List, Optional, Tuple
from .die import DieColor
from .game_state import GameState

# Color constants - Modern, professional color scheme
COLORS = {
    'white': (255, 255, 255),
    'black': (33, 37, 41),
    'red': (220, 53, 69),
    'yellow': (255, 193, 7),
    'green': (40, 167, 69),
    'blue': (0, 123, 255),
    'gray': (108, 117, 125),
    'light_gray': (248, 249, 250),
    'medium_gray': (173, 181, 189),
    'dark_gray': (52, 58, 64),
    'background': (248, 249, 250),
    'card_background': (255, 255, 255),
    'border': (222, 226, 230),
    'shadow': (0, 0, 0, 20),
    'success': (40, 167, 69),
    'warning': (255, 193, 7),
    'danger': (220, 53, 69),
    'info': (23, 162, 184)
}

class Button:
    """Modern button class with improved styling."""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 button_type: str = 'primary', font_size: int = 20):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.button_type = button_type
        self.font = pygame.font.Font(None, font_size)
        self.is_hovered = False
        self.is_enabled = True
        self.is_pressed = False
        
        # Define button styles
        self.styles = {
            'primary': {
                'bg': COLORS['blue'],
                'hover_bg': (0, 86, 179),
                'text': COLORS['white'],
                'border': COLORS['blue']
            },
            'success': {
                'bg': COLORS['success'],
                'hover_bg': (32, 134, 55),
                'text': COLORS['white'],
                'border': COLORS['success']
            },
            'secondary': {
                'bg': COLORS['medium_gray'],
                'hover_bg': (134, 142, 150),
                'text': COLORS['white'],
                'border': COLORS['medium_gray']
            }
        }
    
    def set_enabled(self, enabled: bool) -> None:
        """Set whether the button is enabled or disabled."""
        self.is_enabled = enabled
        if not enabled:
            self.is_hovered = False
            self.is_pressed = False
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events for the button."""
        if not self.is_enabled:
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_pressed = False
        elif event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        return False
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the button with modern styling."""
        style = self.styles.get(self.button_type, self.styles['primary'])
        
        if not self.is_enabled:
            # Disabled state
            bg_color = COLORS['medium_gray']
            text_color = COLORS['gray']
            border_color = COLORS['medium_gray']
        elif self.is_pressed:
            # Pressed state
            bg_color = tuple(max(0, c - 30) for c in style['hover_bg'])
            text_color = style['text']
            border_color = style['border']
        elif self.is_hovered:
            # Hover state
            bg_color = style['hover_bg']
            text_color = style['text']
            border_color = style['border']
        else:
            # Normal state
            bg_color = style['bg']
            text_color = style['text']
            border_color = style['border']
        
        # Draw shadow for depth
        if self.is_enabled and not self.is_pressed:
            shadow_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2,
                                    self.rect.width, self.rect.height)
            shadow_surface = pygame.Surface((self.rect.width, self.rect.height))
            shadow_surface.set_alpha(30)
            shadow_surface.fill((0, 0, 0))
            screen.blit(shadow_surface, shadow_rect)
        
        # Draw button background
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=6)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=6)
        
        # Draw text
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class PenaltyBox:
    """Represents a penalty box showing -5 points with modern styling."""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.is_filled = False
        self.font = pygame.font.Font(None, 18)
    
    def set_filled(self, filled: bool) -> None:
        """Set whether this penalty box is filled."""
        self.is_filled = filled
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the penalty box with modern styling."""
        if self.is_filled:
            # Filled penalty box - danger style
            bg_color = COLORS['danger']
            text_color = COLORS['white']
            border_color = COLORS['danger']
        else:
            # Empty penalty box
            bg_color = COLORS['card_background']
            text_color = COLORS['gray']
            border_color = COLORS['border']
        
        # Draw shadow for depth
        shadow_rect = pygame.Rect(self.rect.x + 1, self.rect.y + 1,
                                self.rect.width, self.rect.height)
        shadow_surface = pygame.Surface((self.rect.width, self.rect.height))
        shadow_surface.set_alpha(20)
        shadow_surface.fill((0, 0, 0))
        screen.blit(shadow_surface, shadow_rect)
        
        # Draw penalty box
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=4)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=4)
        
        # Draw -5 text
        text_surface = self.font.render("-5", True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class NumberBox:
    """Represents a clickable number box in a scoresheet row with modern styling."""
    
    def __init__(self, x: int, y: int, width: int, height: int, number: int, color: DieColor):
        self.rect = pygame.Rect(x, y, width, height)
        self.number = number
        self.color = color
        self.is_marked = False
        self.is_available = True
        self.is_highlighted = False
        self.is_white_sum_available = False  # Available via white dice sum
        self.is_colored_sum_available = False  # Available via white + colored sum
        self.font = pygame.font.Font(None, 24)
        self.font_bold = pygame.font.Font(None, 26)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events for the number box."""
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_available:
            if self.rect.collidepoint(event.pos):
                return True
        elif event.type == pygame.MOUSEMOTION:
            self.is_highlighted = self.rect.collidepoint(event.pos) and self.is_available
        return False
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the number box with modern styling."""
        # Get base color for this die color
        base_color = COLORS[self.color.value]
        
        # Determine styling based on state
        if self.is_marked:
            # Fully marked - solid color with white text
            bg_color = base_color
            text_color = COLORS['white']
            border_color = base_color
            border_width = 2
            font = self.font_bold
            # Add subtle shadow for marked boxes
            shadow_offset = 2
        elif self.is_highlighted and self.is_available:
            # Hovered - lighter background with hover effect
            bg_color = tuple(min(255, int(c * 0.3 + 255 * 0.7)) for c in base_color)
            text_color = COLORS['black']
            border_color = base_color
            border_width = 3
            font = self.font_bold
            shadow_offset = 1
        elif self.is_white_sum_available:
            # Available via white sum - subtle highlight
            bg_color = tuple(min(255, int(c * 0.4 + 255 * 0.6)) for c in base_color)
            text_color = COLORS['black']
            border_color = COLORS['info']
            border_width = 3
            font = self.font_bold
            shadow_offset = 1
        elif self.is_colored_sum_available:
            # Available via colored sum - stronger highlight
            bg_color = tuple(min(255, int(c * 0.5 + 255 * 0.5)) for c in base_color)
            text_color = COLORS['black']
            border_color = base_color
            border_width = 4
            font = self.font_bold
            shadow_offset = 2
        else:
            # Default state - very light background
            bg_color = tuple(min(255, int(c * 0.15 + 255 * 0.85)) for c in base_color)
            text_color = COLORS['dark_gray']
            border_color = COLORS['border']
            border_width = 1
            font = self.font
            shadow_offset = 0
        
        # Draw shadow for depth (if applicable)
        if shadow_offset > 0:
            shadow_rect = pygame.Rect(self.rect.x + shadow_offset, self.rect.y + shadow_offset,
                                    self.rect.width, self.rect.height)
            shadow_surface = pygame.Surface((self.rect.width, self.rect.height))
            shadow_surface.set_alpha(30)
            shadow_surface.fill((0, 0, 0))
            screen.blit(shadow_surface, shadow_rect)
        
        # Draw number box with rounded corners
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=4)
        pygame.draw.rect(screen, border_color, self.rect, border_width, border_radius=4)
        
        # Draw number
        text_surface = font.render(str(self.number), True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class GameGUI:
    """Main GUI class for the Qwixx game with modern design."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Modern typography
        self.font_title = pygame.font.Font(None, 48)
        self.font_large = pygame.font.Font(None, 32)
        self.font_medium = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 18)
        
        # Layout constants
        self.HEADER_HEIGHT = 120
        self.SIDEBAR_WIDTH = 300
        self.CARD_MARGIN = 20
        self.BOX_SIZE = 35
        self.BOX_SPACING = 2
        
        # UI elements with better positioning
        button_y = 20
        self.roll_button = Button(self.CARD_MARGIN, button_y, 140, 45, "Roll Dice", 'primary', 22)
        self.done_button = Button(self.CARD_MARGIN + 160, button_y, 120, 45, "Done", 'success', 22)
        
        # Number boxes for scoresheets
        self.number_boxes: Dict[int, Dict[DieColor, List[NumberBox]]] = {}
        # Penalty boxes for each player
        self.penalty_boxes: Dict[int, List[PenaltyBox]] = {}
        self.setup_number_boxes()
        self.setup_penalty_boxes()
    
    def setup_number_boxes(self) -> None:
        """Set up the number boxes for all players' scoresheets."""
        # We'll create boxes for 2 players for now
        for player_id in range(2):
            self.number_boxes[player_id] = {}
            
            # Starting positions for each player's scoresheet
            start_x = 50 + (player_id * 600)
            start_y = 150
            
            # Create boxes for each color row
            colors = [DieColor.RED, DieColor.YELLOW, DieColor.GREEN, DieColor.BLUE]
            for row_idx, color in enumerate(colors):
                self.number_boxes[player_id][color] = []
                
                # Determine numbers for this row
                if color in [DieColor.RED, DieColor.YELLOW]:
                    numbers = list(range(2, 13))  # 2-12
                else:
                    numbers = list(range(12, 1, -1))  # 12-2
                
                # Create number boxes
                for col_idx, number in enumerate(numbers):
                    x = start_x + (col_idx * 30)
                    y = start_y + (row_idx * 40)
                    box = NumberBox(x, y, 28, 35, number, color)
                    self.number_boxes[player_id][color].append(box)
    
    def setup_penalty_boxes(self) -> None:
        """Set up penalty boxes for all players."""
        for player_id in range(2):
            self.penalty_boxes[player_id] = []
            
            # Starting positions for each player's penalty boxes
            start_x = 50 + (player_id * 600)
            start_y = 320  # Below the scoresheet
            
            # Create 4 penalty boxes
            for i in range(4):
                x = start_x + (i * 35)
                y = start_y
                penalty_box = PenaltyBox(x, y, 30, 25)
                self.penalty_boxes[player_id].append(penalty_box)
    
    def handle_event(self, event: pygame.event.Event, game) -> None:
        """Handle pygame events."""
        # Handle button clicks
        if self.roll_button.handle_event(event):
            game.roll_dice()
        
        if self.done_button.handle_event(event):
            # Handle Done button for stage-based system
            game.player_done_making_moves()
        
        # Handle number box clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            for player_id, player_boxes in self.number_boxes.items():
                player = game.get_players()[player_id]
                for color, boxes in player_boxes.items():
                    for box in boxes:
                        if box.handle_event(event):
                            # Try to mark this number
                            if game.try_mark_number(player, color, box.number):
                                box.is_marked = True
                                # Update availability of other boxes
                                self.update_number_box_availability(game)
        
        # Handle hover effects
        if event.type == pygame.MOUSEMOTION:
            for player_boxes in self.number_boxes.values():
                for color_boxes in player_boxes.values():
                    for box in color_boxes:
                        box.handle_event(event)
            
            self.roll_button.handle_event(event)
            self.done_button.handle_event(event)
    
    def update_number_box_availability(self, game) -> None:
        """Update which number boxes are available for clicking."""
        for player_id, player in enumerate(game.get_players()):
            if player_id not in self.number_boxes:
                continue
            
            scoresheet = player.get_scoresheet()
            current_player = game.get_current_player()
            dice_results = game.get_dice_results()
            
            for color, boxes in self.number_boxes[player_id].items():
                # Update marked status
                for box in boxes:
                    box.is_marked = box.number in scoresheet.rows[color].marked
                    box.is_white_sum_available = False
                    box.is_colored_sum_available = False
                    box.is_available = False
                    
                    # Check if this number can be marked based on current game state
                    game_state = game.get_state()
                    if game_state in [GameState.STAGE_1_MOVES, GameState.STAGE_2_MOVES, GameState.WAITING_FOR_MOVES] and dice_results:
                        if color not in game.get_locked_colors():
                            white_sum = dice_results['white1'] + dice_results['white2']
                            
                            # Stage 1: Only white sum moves for all players
                            if game_state == GameState.STAGE_1_MOVES:
                                if box.number == white_sum and scoresheet.can_mark_number(color, box.number):
                                    if player.can_use_white_sum():
                                        box.is_white_sum_available = True
                                        box.is_available = True
                            
                            # Stage 2: Only white + colored combinations for rolling player
                            elif game_state == GameState.STAGE_2_MOVES:
                                if player == current_player:  # Only rolling player can move in Stage 2
                                    white_colored_sums = game.dice_roller.get_white_plus_colored_sums()
                                    if color in white_colored_sums:
                                        for sum_value in white_colored_sums[color]:
                                            if box.number == sum_value and scoresheet.can_mark_number(color, box.number):
                                                if player.can_use_colored_combination():
                                                    box.is_colored_sum_available = True
                                                    box.is_available = True
                            
                            # Legacy state: original combined logic
                            elif game_state == GameState.WAITING_FOR_MOVES:
                                # Check white sum availability (all players, but respect turn restrictions)
                                if box.number == white_sum and scoresheet.can_mark_number(color, box.number):
                                    if player.can_use_white_sum():
                                        box.is_white_sum_available = True
                                        box.is_available = True
                                
                                # Check white + colored sum availability (active player only, respect turn restrictions)
                                if player == current_player:
                                    white_colored_sums = game.dice_roller.get_white_plus_colored_sums()
                                    if color in white_colored_sums:
                                        for sum_value in white_colored_sums[color]:
                                            if box.number == sum_value and scoresheet.can_mark_number(color, box.number):
                                                if player.can_use_colored_combination():
                                                    box.is_colored_sum_available = True
                                                    box.is_available = True
    
    def update_button_states(self, game) -> None:
        """Update button enabled/disabled states based on game state."""
        game_state = game.get_state()
        current_player = game.get_current_player()
        
        # Roll Dice button should only be enabled when waiting for roll
        self.roll_button.set_enabled(game_state == GameState.WAITING_FOR_ROLL)
        
        # Done button should be enabled during move phases, but disabled when waiting for roll
        if game_state == GameState.WAITING_FOR_ROLL:
            self.done_button.set_enabled(False)
        elif game_state in [GameState.STAGE_1_MOVES, GameState.STAGE_2_MOVES, GameState.WAITING_FOR_MOVES]:
            self.done_button.set_enabled(True)
        else:
            # Game over or other states
            self.done_button.set_enabled(False)
    
    def draw(self, game) -> None:
        """Draw the entire game interface."""
        # Clear screen
        self.screen.fill(COLORS['background'])
        
        # Update number box availability and button states
        self.update_number_box_availability(game)
        self.update_button_states(game)
        
        # Draw title
        title_text = self.font_large.render("QWIXX", True, COLORS['black'])
        self.screen.blit(title_text, (10, 10))
        
        # Draw buttons
        self.roll_button.draw(self.screen)
        self.done_button.draw(self.screen)
        
        # Draw game message with special formatting for game over
        message = game.get_message()
        if game.get_state().name == "GAME_OVER" and "wins" in message:
            # Special formatting for winner announcement
            message_text = self.font_large.render(message, True, COLORS['red'])
            # Center the winner message
            text_rect = message_text.get_rect()
            text_rect.centerx = self.screen.get_width() // 2
            text_rect.y = 60
            # Draw background for winner message
            bg_rect = pygame.Rect(text_rect.x - 10, text_rect.y - 5, text_rect.width + 20, text_rect.height + 10)
            pygame.draw.rect(self.screen, COLORS['yellow'], bg_rect)
            pygame.draw.rect(self.screen, COLORS['black'], bg_rect, 3)
            self.screen.blit(message_text, text_rect)
        else:
            # Normal message formatting
            message_text = self.font_medium.render(message, True, COLORS['black'])
            self.screen.blit(message_text, (450, 60))
        
        # Draw stage information
        self.draw_stage_info(game)
        
        # Draw dice results
        if game.get_dice_results():
            self.draw_dice_results(game.get_dice_results(), game)
        
        # Draw scoresheets
        self.draw_scoresheets(game)
        
        # Draw final scores if game is over
        if game.get_state().name == "GAME_OVER":
            self.draw_final_scores(game)
    
    def draw_stage_info(self, game) -> None:
        """Draw current stage information."""
        start_x = 450
        start_y = 85
        
        game_state = game.get_state()
        if game_state == GameState.STAGE_1_MOVES:
            stage_text = "STAGE 1: All players can mark white dice sum"
            stage_color = COLORS['blue']
        elif game_state == GameState.STAGE_2_MOVES:
            current_player = game.get_current_player()
            stage_text = f"STAGE 2: {current_player.get_name()} can mark white + colored combinations"
            stage_color = COLORS['red']
        else:
            return  # No stage info to display
        
        stage_surface = self.font_medium.render(stage_text, True, stage_color)
        self.screen.blit(stage_surface, (start_x, start_y))
    
    def draw_dice_results(self, dice_results: Dict[str, int], game) -> None:
        """Draw the current dice results vertically."""
        start_x = 450
        start_y = 115  # Moved down to make room for stage info
        
        # Draw white dice
        white_text = f"White: {dice_results['white1']}, {dice_results['white2']}"
        white_surface = self.font_medium.render(white_text, True, COLORS['black'])
        self.screen.blit(white_surface, (start_x, start_y))
        
        # Draw white dice sum
        white_sum = dice_results['white1'] + dice_results['white2']
        sum_text = f"Sum: {white_sum}"
        sum_surface = self.font_medium.render(sum_text, True, COLORS['black'])
        self.screen.blit(sum_surface, (start_x, start_y + 25))
        
        # Always show colored dice combinations (for Stage 2 preview)
        game_state = game.get_state()
        # Draw colored dice vertically - show possible sums instead of die values
        colors = ['red', 'yellow', 'green', 'blue']
        for i, color in enumerate(colors):
            y_pos = start_y + 60 + (i * 30)
            
            # Calculate possible sums with white dice
            white1_sum = dice_results['white1'] + dice_results[color]
            white2_sum = dice_results['white2'] + dice_results[color]
            
            # Draw color label and possible sums
            color_text = f"{color.capitalize()}:"
            color_surface = self.font_medium.render(color_text, True, COLORS[color])
            self.screen.blit(color_surface, (start_x, y_pos))
            
            # Draw the two possible sums prominently
            # Dim them in Stage 1 to show they're for Stage 2
            text_color = COLORS['gray'] if game_state == GameState.STAGE_1_MOVES else COLORS['black']
            sums_text = f"{white1_sum}, {white2_sum}"
            sums_surface = self.font_medium.render(sums_text, True, text_color)
            self.screen.blit(sums_surface, (start_x + 80, y_pos))
    
    def draw_scoresheets(self, game) -> None:
        """Draw all players' scoresheets."""
        for player_id, player in enumerate(game.get_players()):
            self.draw_player_scoresheet(player, player_id)
    
    def draw_player_scoresheet(self, player, player_id: int) -> None:
        """Draw a single player's scoresheet."""
        start_x = 50 + (player_id * 600)
        start_y = 130
        
        # Draw player name with cleaner turn indication
        if player.is_active_player():
            # Draw a subtle border around the active player's area
            border_rect = pygame.Rect(start_x - 15, start_y - 40, 380, 250)
            pygame.draw.rect(self.screen, COLORS['red'], border_rect, 4)
            
            # Draw "ACTIVE PLAYER" indicator above the name
            turn_text = self.font_small.render("ACTIVE PLAYER", True, COLORS['red'])
            self.screen.blit(turn_text, (start_x, start_y - 40))
            
            name_color = COLORS['red']
            name_text = self.font_medium.render(player.get_name(), True, name_color)
        else:
            name_color = COLORS['black']
            name_text = self.font_medium.render(player.get_name(), True, name_color)
        
        self.screen.blit(name_text, (start_x, start_y - 25))
        
        # Draw scoresheet rows
        colors = [DieColor.RED, DieColor.YELLOW, DieColor.GREEN, DieColor.BLUE]
        for row_idx, color in enumerate(colors):
            y = start_y + (row_idx * 40)
            
            # Draw number boxes (they now have colored backgrounds)
            if player_id in self.number_boxes and color in self.number_boxes[player_id]:
                for box in self.number_boxes[player_id][color]:
                    box.draw(self.screen)
        
        # Draw penalty boxes with better positioning
        penalty_y = start_y + (len(colors) * 40) + 10
        penalty_label = self.font_medium.render("Penalties:", True, COLORS['black'])
        # Move the penalty label further left to prevent cutoff
        penalty_label_x = start_x - 90 if player_id == 0 else start_x - 80
        self.screen.blit(penalty_label, (penalty_label_x, penalty_y + 5))
        
        # Update and draw penalty boxes
        if player_id in self.penalty_boxes:
            penalties = player.get_scoresheet().penalties
            for i, penalty_box in enumerate(self.penalty_boxes[player_id]):
                penalty_box.set_filled(i < penalties)
                penalty_box.draw(self.screen)
        
        # Draw total score
        score_text = self.font_medium.render(f"Total Score: {player.get_total_score()}", True, COLORS['black'])
        self.screen.blit(score_text, (start_x, penalty_y + 35))
    
    def draw_final_scores(self, game) -> None:
        """Draw final scores when game is over."""
        start_y = 400
        
        # Draw "Final Scores" header
        header_text = self.font_large.render("FINAL SCORES", True, COLORS['black'])
        header_rect = header_text.get_rect()
        header_rect.centerx = self.screen.get_width() // 2
        header_rect.y = start_y
        self.screen.blit(header_text, header_rect)
        
        # Sort players by score (highest first)
        sorted_players = sorted(game.get_players(), key=lambda p: p.get_total_score(), reverse=True)
        
        # Draw each player's final score
        for i, player in enumerate(sorted_players):
            y_pos = start_y + 40 + (i * 30)
            
            # Highlight the winner
            if i == 0:
                score_text = f"🏆 {player.get_name()}: {player.get_total_score()} points (WINNER!)"
                color = COLORS['red']
                font = self.font_medium
            else:
                score_text = f"{i + 1}. {player.get_name()}: {player.get_total_score()} points"
                color = COLORS['black']
                font = self.font_medium
            
            text_surface = font.render(score_text, True, color)
            text_rect = text_surface.get_rect()
            text_rect.centerx = self.screen.get_width() // 2
            text_rect.y = y_pos
            self.screen.blit(text_surface, text_rect)