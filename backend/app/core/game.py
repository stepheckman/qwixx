"""
Main Game class for the Qwixx game.
"""

from typing import List, Optional, Dict

from .player import Player
from .ai_player import AIPlayer
from .dice_roller import DiceRoller
from .die import DieColor
from .game_state import GameState
from .logger import (
    get_game_logger,
    log_game_event,
    log_dice_roll,
    log_game_state_change,
    log_player_decision,
    setup_logging,
)


class Game:
    """Main game controller for Qwixx."""

    def __init__(self, num_players: int = 2, ai_strategy: str = "medium"):
        """
        Initialize the game.

        Args:
            num_players: Number of human players (1 or 2)
            ai_strategy: AI difficulty strategy ("easy", "medium", "hard")
        """
        self.dice_roller = DiceRoller()
        self.players: List[Player] = []
        self.current_player_index = 0
        self.state = GameState.SETUP
        self.dice_results: Optional[Dict[str, int]] = None
        self.locked_colors: set = set()  # Track which colors are locked globally
        self.message = "Welcome to Qwixx!"
        self.players_finished_moves: set = (
            set()
        )  # Track which players have finished their moves
        self.active_player_made_move = False  # Track if active player made any move
        self.stage_1_players_finished: set = (
            set()
        )  # Track players finished with stage 1
        self.stage_2_rolling_player_finished = (
            False  # Track if rolling player finished stage 2
        )
        self.rolling_player_made_stage_1_move = (
            False  # Track if rolling player made move in stage 1
        )
        self.rolling_player_made_stage_2_move = (
            False  # Track if rolling player made move in stage 2
        )
        self.num_players = num_players
        self.ai_strategy = (
            ai_strategy if ai_strategy else "medium"
        )  # Default to medium if None

        # Initialize logging
        self.logger = get_game_logger()
        setup_logging()

        # Initialize players
        self.setup_players()

    def setup_players(self) -> None:
        """Set up the players for the game."""
        self.players = []

        if self.num_players == 1:
            # Single player mode: Human player 1 vs AI player 2
            self.players = [
                Player("Player 1", 0),
                AIPlayer("AI Player", 1, difficulty=self.ai_strategy),
            ]
            self.logger.info(
                f"Game setup: 1 human player vs AI ({self.ai_strategy} difficulty)"
            )
        else:
            # Two player mode: Both human players
            self.players = [Player("Player 1", 0), Player("Player 2", 1)]
            self.logger.info("Game setup: 2 human players")

        if self.players:
            self.players[0].set_active(True)
            self.players[0].start_new_turn()  # Initialize turn tracking

        old_state = self.state.name
        self.state = GameState.WAITING_FOR_ROLL
        log_game_state_change(old_state, self.state.name, "Players initialized")

        self.message = f"{self.get_current_player().get_name()}'s turn. Click 'Roll Dice' to start."

        # Log player setup
        player_info = [
            f"{p.get_name()} ({'AI' if hasattr(p, 'is_ai') and p.is_ai else 'Human'})"
            for p in self.players
        ]
        log_game_event(
            "PLAYERS_SETUP", f"Players: {', '.join(player_info)}", players=player_info
        )

    def get_current_player(self) -> Player:
        """Get the currently active player."""
        return self.players[self.current_player_index]

    def next_player(self) -> None:
        """Move to the next player's turn."""
        # Set current player as inactive
        old_player = self.players[self.current_player_index]
        old_player.set_active(False)

        # Move to next player
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

        # Set new player as active and reset all players' turn tracking
        new_player = self.players[self.current_player_index]
        new_player.set_active(True)

        self.logger.info(
            f"Turn changed: {old_player.get_name()} -> {new_player.get_name()}"
        )
        log_game_event(
            "TURN_CHANGE",
            f"Turn changed from {old_player.get_name()} to {new_player.get_name()}",
            previous_player=old_player.get_name(),
            current_player=new_player.get_name(),
            turn_number=self.current_player_index + 1,
        )

        # Reset turn tracking for all players
        for player in self.players:
            player.start_new_turn()

        # Reset turn state
        self.players_finished_moves.clear()
        self.active_player_made_move = False
        self.stage_1_players_finished.clear()
        self.stage_2_rolling_player_finished = False
        self.rolling_player_made_stage_1_move = False
        self.rolling_player_made_stage_2_move = False

        old_state = self.state.name
        self.state = GameState.WAITING_FOR_ROLL
        log_game_state_change(
            old_state, self.state.name, f"{new_player.get_name()}'s turn"
        )

        self.dice_results = None
        self.message = f"{new_player.get_name()}'s turn. Click 'Roll Dice' to start."

    def roll_dice(self) -> None:
        """Roll all dice and update game state."""
        if self.state != GameState.WAITING_FOR_ROLL:
            return

        self.dice_results = self.dice_roller.roll_all()
        current_player = self.get_current_player()

        # Log dice roll
        self.logger.info(
            f"{current_player.get_name()} rolled dice: {self.dice_results}"
        )
        log_dice_roll(self.dice_results)

        old_state = self.state.name
        self.state = GameState.DICE_ROLLED
        log_game_state_change(
            old_state, self.state.name, f"{current_player.get_name()} rolled dice"
        )

        # Check if any moves are possible in Stage 1 (white dice sum only)
        if self.has_stage_1_moves():
            old_state = self.state.name
            self.state = GameState.STAGE_1_MOVES
            log_game_state_change(old_state, self.state.name, "Stage 1 moves available")

            self.stage_1_players_finished.clear()
            self.rolling_player_made_stage_1_move = False
            white_sum = self.dice_results["white1"] + self.dice_results["white2"]
            self.message = (
                f"Stage 1: All players can mark using white dice sum ({white_sum})."
            )

            self.logger.info(f"Stage 1 started - white dice sum: {white_sum}")
        else:
            # No Stage 1 moves possible, check Stage 2
            if self.has_stage_2_moves():
                old_state = self.state.name
                self.state = GameState.STAGE_2_MOVES
                log_game_state_change(
                    old_state, self.state.name, "Stage 2 moves available"
                )

                self.stage_2_rolling_player_finished = False
                self.rolling_player_made_stage_2_move = False
                self.message = f"Stage 2: {current_player.get_name()} can mark using white + colored combinations."

                self.logger.info(f"Stage 2 started for {current_player.get_name()}")
            else:
                # No moves possible in either stage, rolling player gets penalty
                self.logger.warning(
                    f"No valid moves available for {current_player.get_name()}, applying penalty"
                )
                log_game_event(
                    "PENALTY_APPLIED",
                    f"{current_player.get_name()} received penalty - no valid moves",
                    player=current_player.get_name(),
                    reason="no_valid_moves",
                    penalty_count=current_player.get_scoresheet().penalties + 1,
                )

                current_player.get_scoresheet().add_penalty()
                self.message = f"No valid moves available. {current_player.get_name()} receives a penalty."
                self.check_game_over()
                if self.state != GameState.GAME_OVER:
                    self.next_player()

    def has_possible_moves(self) -> bool:
        """Check if any player has possible moves with current dice."""
        if not self.dice_results:
            return False

        white_sum = self.dice_results["white1"] + self.dice_results["white2"]

        # Check if any player can mark the white sum
        for player in self.players:
            for color in [DieColor.RED, DieColor.YELLOW, DieColor.GREEN, DieColor.BLUE]:
                if color not in self.locked_colors:
                    if player.get_scoresheet().can_mark_number(color, white_sum):
                        return True

        # Check if active player can mark white + colored combinations
        current_player = self.get_current_player()
        white_colored_sums = self.dice_roller.get_white_plus_colored_sums()

        for color, sums in white_colored_sums.items():
            if color not in self.locked_colors:
                for sum_value in sums:
                    if current_player.get_scoresheet().can_mark_number(
                        color, sum_value
                    ):
                        return True

        return False

    def has_stage_1_moves(self) -> bool:
        """Check if any player has possible moves in Stage 1 (white dice sum only)."""
        if not self.dice_results:
            return False

        white_sum = self.dice_results["white1"] + self.dice_results["white2"]

        # Check if any player can mark the white sum
        for player in self.players:
            for color in [DieColor.RED, DieColor.YELLOW, DieColor.GREEN, DieColor.BLUE]:
                if color not in self.locked_colors:
                    if player.get_scoresheet().can_mark_number(color, white_sum):
                        return True

        return False

    def has_stage_2_moves(self) -> bool:
        """Check if the rolling player has possible moves in Stage 2 (white + colored combinations)."""
        if not self.dice_results:
            return False

        # Only the rolling player can make moves in Stage 2
        current_player = self.get_current_player()
        white_colored_sums = self.dice_roller.get_white_plus_colored_sums()

        for color, sums in white_colored_sums.items():
            if color not in self.locked_colors:
                for sum_value in sums:
                    if current_player.get_scoresheet().can_mark_number(
                        color, sum_value
                    ):
                        return True

        return False

    def try_mark_number(self, player: Player, color: DieColor, number: int) -> bool:
        """
        Try to mark a number for a player.

        Args:
            player: The player trying to mark
            color: The color row to mark in
            number: The number to mark

        Returns:
            True if successfully marked, False otherwise
        """
        if color in self.locked_colors:
            self.logger.debug(
                f"{player.get_name()} tried to mark {number} in locked {color.value} row"
            )
            return False

        if not self.is_valid_move(player, color, number):
            self.logger.debug(
                f"Invalid move: {player.get_name()} tried to mark {number} in {color.value} row"
            )
            return False

        # Mark the number
        if player.get_scoresheet().mark_number(color, number):
            white_sum = 0
            if self.dice_results:
                white_sum = self.dice_results["white1"] + self.dice_results["white2"]
            move_type = "unknown"
            stage = 0

            if number == white_sum:
                player.record_white_sum_move()
                move_type = "white_sum"
                # Track stage-specific moves for rolling player
                if (
                    self.state == GameState.STAGE_1_MOVES
                    and player == self.get_current_player()
                ):
                    self.rolling_player_made_stage_1_move = True
                    stage = 1
            elif player == self.get_current_player():
                # This must be a colored combination move
                white_colored_sums = self.dice_roller.get_white_plus_colored_sums()
                if color in white_colored_sums and number in white_colored_sums[color]:
                    player.record_colored_combination_move()
                    move_type = "colored_combination"
                    # Track stage-specific moves
                    if self.state == GameState.STAGE_2_MOVES:
                        self.rolling_player_made_stage_2_move = True
                        stage = 2

            # Log the player move
            self.logger.info(
                f"{player.get_name()} marked {number} in {color.value} row ({move_type})"
            )
            log_player_decision(
                player.get_name(),
                stage
                if stage > 0
                else (1 if self.state == GameState.STAGE_1_MOVES else 2),
                "MARK",
                {
                    "color": color.value,
                    "number": number,
                    "move_type": move_type,
                    "dice_results": self.dice_results.copy()
                    if self.dice_results
                    else {},
                },
            )

            # Track if active player made a move (legacy tracking)
            if player == self.get_current_player():
                self.active_player_made_move = True

            # Check if this locks the row
            if player.get_scoresheet().can_lock_row(color):
                if player.get_scoresheet().lock_row(color):
                    self.locked_colors.add(color)
                    self.message = f"{player.get_name()} locked the {color.value} row!"

                    self.logger.info(
                        f"{player.get_name()} locked the {color.value} row!"
                    )
                    log_game_event(
                        "ROW_LOCKED",
                        f"{player.get_name()} locked the {color.value} row",
                        player=player.get_name(),
                        color=color.value,
                        locked_colors_count=len(self.locked_colors),
                        total_locked_colors=list(c.value for c in self.locked_colors),
                    )

            # After marking a number, the player is done with their moves for the current stage
            self.player_done_making_moves(player)

            return True

        return False

    def is_valid_move(self, player: Player, color: DieColor, number: int) -> bool:
        """
        Check if a move is valid for the current game state.

        Args:
            player: The player making the move
            color: The color row
            number: The number to mark

        Returns:
            True if the move is valid, False otherwise
        """
        # Check if we're in a valid state for moves
        if (
            self.state
            not in [
                GameState.STAGE_1_MOVES,
                GameState.STAGE_2_MOVES,
                GameState.WAITING_FOR_MOVES,
            ]
            or not self.dice_results
        ):
            return False

        if not player.get_scoresheet().can_mark_number(color, number):
            return False

        white_sum = self.dice_results["white1"] + self.dice_results["white2"]

        # Stage 1: Only white sum moves allowed for all players
        if self.state == GameState.STAGE_1_MOVES:
            if number == white_sum:
                return player.can_use_white_sum()
            else:
                return False

        # Stage 2: Only white + colored combination moves allowed for rolling player only
        elif self.state == GameState.STAGE_2_MOVES:
            if player != self.get_current_player():
                return False  # Only rolling player can move in Stage 2

            white_colored_sums = self.dice_roller.get_white_plus_colored_sums()
            if color in white_colored_sums and number in white_colored_sums[color]:
                return player.can_use_colored_combination()
            else:
                return False

        # Legacy state: original combined logic
        elif self.state == GameState.WAITING_FOR_MOVES:
            # Check if this is a white sum move
            if number == white_sum:
                return player.can_use_white_sum()

            # Check if this is a white + colored combination move (active player only)
            if player == self.get_current_player():
                white_colored_sums = self.dice_roller.get_white_plus_colored_sums()
                if color in white_colored_sums and number in white_colored_sums[color]:
                    return player.can_use_colored_combination()

        return False

    def player_finished_moves(self, player: Player) -> None:
        """Mark a player as finished making moves for this turn."""
        if self.state != GameState.WAITING_FOR_MOVES:
            return

        self.players_finished_moves.add(player.get_id())

        # Check if all players have finished their moves
        if len(self.players_finished_moves) >= len(self.players):
            self.end_turn()

    def end_turn(self) -> None:
        """End the current turn and move to the next player."""
        # Check if active player made any move, if not, give penalty
        if not self.active_player_made_move:
            current_player = self.get_current_player()
            current_player.get_scoresheet().add_penalty()
            self.message = (
                f"{current_player.get_name()} made no moves and receives a penalty."
            )

        self.check_game_over()
        if self.state != GameState.GAME_OVER:
            self.next_player()

    def pass_turn(self) -> None:
        """Pass the turn (active player gets penalty if they haven't marked anything)."""
        if self.state != GameState.WAITING_FOR_MOVES:
            return

        # Active player explicitly passes - they get penalty if they made no moves
        current_player = self.get_current_player()
        if not self.active_player_made_move:
            current_player.get_scoresheet().add_penalty()
            self.message = f"{current_player.get_name()} passed and receives a penalty."
        else:
            self.message = f"{current_player.get_name()} passed their turn."

        self.check_game_over()
        if self.state != GameState.GAME_OVER:
            self.next_player()

    def player_done_making_moves(self, player: Optional[Player] = None) -> None:
        """Handle when a player indicates they are done making moves."""
        if player is None:
            player = self.get_current_player()

        if self.state == GameState.STAGE_1_MOVES:
            self.stage_1_players_finished.add(player.get_id())
            self.logger.info(
                f"{player.get_name()} finished Stage 1 moves. ({len(self.stage_1_players_finished)}/{len(self.players)} done)"
            )

            # Check if all players are done with Stage 1
            if len(self.stage_1_players_finished) >= len(self.players):
                self.stage_1_done()
        elif self.state == GameState.STAGE_2_MOVES:
            # Only rolling player can be in Stage 2
            if player == self.get_current_player():
                self.stage_2_done()
        elif self.state == GameState.WAITING_FOR_MOVES:
            # Legacy handling
            self.player_finished_moves(player)
            self.message = f"{player.get_name()} is done making moves."

    def stage_1_done(self) -> None:
        """Handle when Stage 1 is complete (all players done with white dice sum moves)."""
        if self.state != GameState.STAGE_1_MOVES:
            return

        self.logger.info("Stage 1 complete for all players.")

        # Move to Stage 2 if rolling player has possible moves
        if self.has_stage_2_moves():
            self.state = GameState.STAGE_2_MOVES
            self.stage_2_rolling_player_finished = False
            current_player = self.get_current_player()
            self.message = f"Stage 2: {current_player.get_name()} can mark using white + colored combinations."
        else:
            # No Stage 2 moves, end turn with penalty check
            self.end_stage_based_turn()

    def stage_2_done(self) -> None:
        """Handle when Stage 2 is complete (rolling player done with colored combination moves)."""
        if self.state != GameState.STAGE_2_MOVES:
            return

        self.stage_2_rolling_player_finished = True
        self.end_stage_based_turn()

    def end_stage_based_turn(self) -> None:
        """End the turn after both stages are complete, applying penalty if needed."""
        # Check if rolling player made any move in either stage
        if (
            not self.rolling_player_made_stage_1_move
            and not self.rolling_player_made_stage_2_move
        ):
            current_player = self.get_current_player()
            current_player.get_scoresheet().add_penalty()
            self.message = f"{current_player.get_name()} made no moves in both stages and receives a penalty."

        self.check_game_over()
        if self.state != GameState.GAME_OVER:
            self.next_player()

    def check_game_over(self) -> None:
        """Check if the game is over."""
        # Game ends if 2 colors are locked or any player has 4 penalties
        if len(self.locked_colors) >= 2:
            self.state = GameState.GAME_OVER
            winner = self.get_winner()
            if winner:
                self.message = f"Game Over! Two colors locked. {winner.get_name()} wins with {winner.get_total_score()} points!"
            else:
                self.message = "Game Over! Two colors have been locked."
            return

        for player in self.players:
            if player.is_game_over():
                self.state = GameState.GAME_OVER
                winner = self.get_winner()
                if winner:
                    self.message = f"Game Over! {player.get_name()} reached penalty limit. {winner.get_name()} wins with {winner.get_total_score()} points!"
                else:
                    self.message = (
                        f"Game Over! {player.get_name()} has reached the penalty limit."
                    )
                return

    def get_winner(self) -> Optional[Player]:
        """Get the winner of the game."""
        if self.state != GameState.GAME_OVER:
            return None

        return max(self.players, key=lambda p: p.get_total_score())

    def handle_ai_moves(self) -> None:
        """Process all AI players' decisions automatically until it's a human's turn."""
        # Process moves in a loop to handle sequential states (e.g. Stage 1 -> Stage 2)
        max_iterations = 20
        iterations = 0

        while iterations < max_iterations:
            iterations += 1
            game_state = self.get_state()
            current_player = self.get_current_player()

            # 1. Active player is AI and needs to roll
            if game_state == GameState.WAITING_FOR_ROLL and getattr(
                current_player, "is_ai", False
            ):
                self.roll_dice()
                continue

            # 2. Stage 1: Any AI players who haven't finished
            if game_state == GameState.STAGE_1_MOVES:
                ai_processed = False
                # Use a copy of players list to avoid modification issues if any
                for player in self.players:
                    if (
                        getattr(player, "is_ai", False)
                        and player.get_id() not in self.stage_1_players_finished
                    ):
                        self._process_single_ai_stage_1(player)
                        ai_processed = True

                # In 1-player mode, if human has no Stage 1 moves, finish for them
                if self.num_players == 1:
                    human = self.players[0]
                    if human.get_id() not in self.stage_1_players_finished:
                        if not self.can_player_move_in_stage(human, 1):
                            self.player_done_making_moves(human)
                            ai_processed = True

                if ai_processed:
                    continue
                else:
                    break  # Wait for human Stage 1 moves

            # 3. Stage 2: Active player is AI and needs to move
            if game_state == GameState.STAGE_2_MOVES and getattr(
                current_player, "is_ai", False
            ):
                self._process_single_ai_stage_2(current_player)
                continue

            # In 1-player mode, if human is active and has no Stage 2 moves, finish for them
            if self.num_players == 1 and game_state == GameState.STAGE_2_MOVES:
                human = self.players[0]
                if human == current_player and not self.can_player_move_in_stage(
                    human, 2
                ):
                    self.player_done_making_moves(human)
                    continue

            # If no AI actions or automatic human actions can be taken, stop
            break

    def _process_single_ai_stage_1(self, ai_player) -> None:
        """Handle decision for a single AI player in Stage 1."""
        available_moves = ai_player.get_available_moves(self)
        if available_moves and ai_player.should_make_move_in_stage(self, 1):
            move = ai_player.make_move_decision(self, available_moves)
            if move:
                color, number = move
                self.try_mark_number(ai_player, color, number)

        # Always mark as finished even if no move was made
        self.player_done_making_moves(ai_player)

    def _process_single_ai_stage_2(self, ai_player) -> None:
        """Handle decision for a single AI player in Stage 2."""
        available_moves = ai_player.get_available_moves(self)
        if available_moves and ai_player.should_make_move_in_stage(self, 2):
            move = ai_player.make_move_decision(self, available_moves)
            if move:
                color, number = move
                self.try_mark_number(ai_player, color, number)

        # Always mark as finished
        self.player_done_making_moves(ai_player)

    def get_state(self) -> GameState:
        """Get the current game state."""
        return self.state

    def get_message(self) -> str:
        """Get the current game message."""
        return self.message

    def get_dice_results(self) -> Optional[Dict[str, int]]:
        """Get the current dice results."""
        return self.dice_results

    def get_players(self) -> List[Player]:
        """Get all players."""
        return self.players

    def get_locked_colors(self) -> set:
        """Get the set of locked colors."""
        return self.locked_colors

    def can_player_move_in_stage(self, player: Player, stage: int) -> bool:
        """Check if a player has ANY valid moves in the given stage."""
        if not self.dice_results:
            return False

        if stage == 1:
            white_sum = self.dice_results["white1"] + self.dice_results["white2"]
            for color in DieColor:
                if color not in self.locked_colors:
                    if player.get_scoresheet().can_mark_number(color, white_sum):
                        return True
        elif stage == 2:
            if player != self.get_current_player():
                return False
            white_colored_sums = self.dice_roller.get_white_plus_colored_sums()
            for color, sums in white_colored_sums.items():
                if color not in self.locked_colors:
                    for s in sums:
                        if player.get_scoresheet().can_mark_number(color, s):
                            return True
        return False
