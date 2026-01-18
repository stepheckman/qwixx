"""
AI Player class for the Qwixx game.
"""

import random
from typing import List, Tuple, Optional, Dict
from .player import Player
from .die import DieColor
from .scoresheet import Scoresheet
from .game_state import GameState
from .logger import get_ai_logger, log_player_decision, log_game_event


class AIPlayer(Player):
    """AI player that can make automated decisions in Qwixx."""

    def __init__(self, name: str, player_id: int, difficulty: str = "medium"):
        """
        Initialize an AI player.

        Args:
            name: The AI player's name
            player_id: Unique identifier for the player
            difficulty: AI difficulty level ("easy", "medium", "hard")
        """
        super().__init__(name, player_id)
        self.difficulty = difficulty
        self.is_ai = True
        self.logger = get_ai_logger()

        self.logger.info(f"AI Player {name} initialized with {difficulty} difficulty")

    def make_move_decision(
        self, game, available_moves: List[Tuple[DieColor, int]]
    ) -> Optional[Tuple[DieColor, int]]:
        """
        Make a decision about which move to make.

        Args:
            game: The current game instance
            available_moves: List of (color, number) tuples representing valid moves

        Returns:
            Tuple of (color, number) to mark, or None to skip
        """
        if not available_moves:
            self.logger.debug(f"{self.name} has no available moves")
            return None

        self.logger.debug(
            f"{self.name} considering {len(available_moves)} moves: {available_moves}"
        )

        decision = None
        if self.difficulty == "easy":
            decision = self._make_easy_decision(available_moves)
        elif self.difficulty == "medium":
            decision = self._make_medium_decision(game, available_moves)
        else:  # hard
            decision = self._make_hard_decision(game, available_moves)

        if decision:
            color, number = decision
            self.logger.info(
                f"{self.name} decided to mark {number} in {color.value} row"
            )
            log_game_event(
                "AI_DECISION",
                f"{self.name} chose to mark {number} in {color.value} row",
                ai_player=self.name,
                difficulty=self.difficulty,
                color=color.value,
                number=number,
                available_moves=[(c.value, n) for c, n in available_moves],
            )
        else:
            self.logger.info(f"{self.name} decided to skip move")
            log_game_event(
                "AI_DECISION",
                f"{self.name} chose to skip move",
                ai_player=self.name,
                difficulty=self.difficulty,
                decision="skip",
                available_moves=[(c.value, n) for c, n in available_moves],
            )

        return decision

    def _make_easy_decision(
        self, available_moves: List[Tuple[DieColor, int]]
    ) -> Optional[Tuple[DieColor, int]]:
        """Easy AI: Random selection with 70% chance to make a move."""
        if random.random() < 0.3:  # 30% chance to skip
            return None
        return random.choice(available_moves)

    def _make_medium_decision(
        self, game, available_moves: List[Tuple[DieColor, int]]
    ) -> Optional[Tuple[DieColor, int]]:
        """Medium AI: Consider basic strategy factors."""
        if not available_moves:
            return None

        # Score each move based on various factors
        scored_moves = []

        for color, number in available_moves:
            score = self._evaluate_move(game, color, number)
            scored_moves.append((score, color, number))

        # Sort by score (highest first) - only compare the score (first element)
        scored_moves.sort(key=lambda x: x[0], reverse=True)

        # 85% chance to pick the best move, 15% chance for some randomness
        if random.random() < 0.85:
            return (scored_moves[0][1], scored_moves[0][2])
        else:
            # Pick from top 3 moves or all if fewer available
            top_moves = scored_moves[: min(3, len(scored_moves))]
            _, color, number = random.choice(top_moves)
            return (color, number)

    def _make_hard_decision(
        self, game, available_moves: List[Tuple[DieColor, int]]
    ) -> Optional[Tuple[DieColor, int]]:
        """Hard AI: Advanced strategy with look-ahead."""
        if not available_moves:
            return None

        # Score each move with advanced evaluation
        scored_moves = []

        for color, number in available_moves:
            score = self._evaluate_move_advanced(game, color, number)
            scored_moves.append((score, color, number))

        # Sort by score (highest first) - only compare the score (first element)
        scored_moves.sort(key=lambda x: x[0], reverse=True)

        # 95% chance to pick the best move
        if random.random() < 0.95:
            return (scored_moves[0][1], scored_moves[0][2])
        else:
            # Small chance for suboptimal play to avoid being too predictable
            return (
                (scored_moves[0][1], scored_moves[0][2])
                if len(scored_moves) == 1
                else (scored_moves[1][1], scored_moves[1][2])
            )

    def _evaluate_move(self, game, color: DieColor, number: int) -> float:
        """
        Evaluate a move with basic strategy.

        Args:
            game: The current game instance
            color: The color row to mark
            number: The number to mark

        Returns:
            Score for this move (higher is better)
        """
        score = 0.0
        scoresheet = self.get_scoresheet()
        row = scoresheet.rows[color]

        # Base score: prefer moves that advance further in the row
        marked_count = len(row.marked)
        score += marked_count * 2  # More marks = higher score potential

        # CRITICAL: Early game positioning penalty for high numbers
        early_game_penalty = self._calculate_early_game_positioning_penalty(
            color, number, marked_count
        )
        score += early_game_penalty

        # Enhanced: Prioritize numbers closer to the ends of rows (2s and 12s)
        end_number_bonus = self._calculate_end_number_bonus(color, number)
        score += end_number_bonus

        # Bonus for getting closer to locking a row, but only if we have good positioning
        if color in [DieColor.RED, DieColor.YELLOW]:
            # For ascending rows, prefer higher numbers
            progress = (number - 2) / 10.0  # Normalize to 0-1
        else:
            # For descending rows, prefer lower numbers
            progress = (12 - number) / 10.0  # Normalize to 0-1

        # Only give progress bonus if we're not making a bad early positioning move
        if marked_count > 0 or not self._is_bad_early_positioning(color, number):
            score += progress * 3

        # Enhanced: Stronger bonus for moves that enable locking a row
        if self._can_enable_row_lock(row, number, marked_count):
            score += 8  # Increased from 5 to 8

        # Enhanced: Improved penalty avoidance logic
        penalty_risk_bonus = self._calculate_penalty_avoidance_bonus(game)
        score += penalty_risk_bonus

        # Penalty if the row is already well-advanced by others
        # (Check if other players have many marks in this color)
        other_players_marks = 0
        for player in game.get_players():
            if player != self:
                other_players_marks += len(player.get_scoresheet().rows[color].marked)

        if other_players_marks > marked_count + 2:
            score -= 2  # Slight penalty for falling behind

        return score

    def _evaluate_move_advanced(self, game, color: DieColor, number: int) -> float:
        """
        Advanced move evaluation with more sophisticated strategy.

        Args:
            game: The current game instance
            color: The color row to mark
            number: The number to mark

        Returns:
            Score for this move (higher is better)
        """
        score = self._evaluate_move(game, color, number)

        scoresheet = self.get_scoresheet()
        row = scoresheet.rows[color]

        # Advanced factors

        # 1. Enhanced opponent analysis and blocking
        opponent_blocking_bonus = self._calculate_opponent_blocking_bonus(
            game, color, number
        )
        score += opponent_blocking_bonus

        # 2. Probabilistic analysis for future dice rolls
        probability_bonus = self._calculate_probability_bonus(color, number)
        score += probability_bonus

        # 3. Dynamic strategy based on game phase
        game_phase_bonus = self._calculate_game_phase_bonus(game, color, number)
        score += game_phase_bonus

        # 4. Enhanced row locking value calculation
        row_lock_value = self._calculate_enhanced_row_lock_value(game, color, number)
        score += row_lock_value

        # 5. Consider synergy with other rows (improved)
        synergy_bonus = self._calculate_row_synergy_bonus(scoresheet, color)
        score += synergy_bonus

        # 6. End-game considerations (enhanced)
        locked_colors = len(game.get_locked_colors())
        if locked_colors >= 1:  # End game approaching
            # Prioritize rows with more potential points
            potential_score = self._calculate_potential_row_score(
                row, len(row.marked) + 1
            )
            score += potential_score * 0.7  # Increased weight

        # 7. Advanced early game positioning analysis
        advanced_positioning_bonus = self._calculate_advanced_positioning_bonus(
            game, color, number
        )
        score += advanced_positioning_bonus

        # 8. Hard mode specific penalty: Avoid marking 11 in red row as first move (legacy)
        red_11_penalty = self._calculate_red_11_penalty(color, number)
        score += red_11_penalty

        return score

    def _calculate_potential_row_score(self, row, mark_count: int) -> int:
        """Calculate potential score for a row with given number of marks."""
        if mark_count <= 0:
            return 0
        elif mark_count == 1:
            return 1
        elif mark_count == 2:
            return 3
        elif mark_count == 3:
            return 6
        elif mark_count == 4:
            return 10
        elif mark_count == 5:
            return 15
        elif mark_count >= 6:
            return 21 + (mark_count - 6) * 7  # Locked row bonus
        return 0

    def _calculate_end_number_bonus(self, color: DieColor, number: int) -> float:
        """
        Calculate bonus for the last number in each row (enables row locking).

        Args:
            color: The color row
            number: The number being evaluated

        Returns:
            Bonus score for the last number in the row
        """
        if color in [DieColor.RED, DieColor.YELLOW]:
            # For ascending rows (2-12), only 12 is the last number
            if number == 12:
                return 4.0
            elif number >= 10:
                return 2.0  # Close to end bonus
        else:
            # For descending rows (12-2), only 2 is the last number
            if number == 2:
                return 4.0
            elif number <= 4:
                return 2.0  # Close to end bonus
        return 0.0

    def _can_enable_row_lock(self, row, number: int, marked_count: int) -> bool:
        """
        Check if this move can enable locking a row.

        Args:
            row: The color row
            number: The number being marked
            marked_count: Current number of marks in the row

        Returns:
            True if this move enables row locking
        """
        # Need at least 4 marks already to potentially enable locking with this move
        if marked_count < 4:
            return False

        # Check if this number is the rightmost number (12 for red/yellow, 2 for green/blue)
        rightmost_number = row.numbers[-1]
        return number == rightmost_number

    def _calculate_penalty_avoidance_bonus(self, game) -> float:
        """
        Calculate bonus for penalty avoidance based on current penalty count.

        Args:
            game: The current game instance

        Returns:
            Bonus score for penalty avoidance
        """
        scoresheet = self.get_scoresheet()
        penalty_count = scoresheet.penalties

        # Higher bonus as penalty count increases
        if penalty_count >= 3:
            return 3.0  # Very high risk, prioritize any move
        elif penalty_count >= 2:
            return 2.0  # High risk
        elif penalty_count >= 1:
            return 1.0  # Moderate risk
        return 0.0

    def _calculate_opponent_blocking_bonus(
        self, game, color: DieColor, number: int
    ) -> float:
        """
        Calculate bonus for blocking opponents from high-value moves or row locks.

        Args:
            game: The current game instance
            color: The color row
            number: The number being evaluated

        Returns:
            Bonus score for opponent blocking
        """
        bonus = 0.0

        for player in game.get_players():
            if player != self:
                other_scoresheet = player.get_scoresheet()
                other_row = other_scoresheet.rows[color]

                # High bonus if opponent is close to locking this row
                if len(other_row.marked) >= 4:
                    rightmost_number = other_row.numbers[-1]
                    if number == rightmost_number:
                        bonus += 6.0  # Block their lock attempt
                    else:
                        bonus += 3.0  # Compete in their strong row

                # Bonus for blocking high-value positions
                elif len(other_row.marked) >= 2:
                    bonus += 1.5  # Moderate competition bonus

        return bonus

    def _calculate_probability_bonus(self, color: DieColor, number: int) -> float:
        """
        Calculate bonus based on probability of rolling this number in future turns.

        Args:
            color: The color row
            number: The number being evaluated

        Returns:
            Bonus score based on roll probability
        """
        # Dice roll probabilities for sums (2 white dice + 1 colored die scenarios)
        # More likely sums get lower bonus (easier to get later)
        # Less likely sums get higher bonus (harder to get later)

        probability_map = {
            2: 0.028,  # 1/36 (only 1+1)
            3: 0.056,  # 2/36 (1+2, 2+1)
            4: 0.083,  # 3/36 (1+3, 2+2, 3+1)
            5: 0.111,  # 4/36
            6: 0.139,  # 5/36
            7: 0.167,  # 6/36 (most common)
            8: 0.139,  # 5/36
            9: 0.111,  # 4/36
            10: 0.083,  # 3/36
            11: 0.056,  # 2/36
            12: 0.028,  # 1/36 (only 6+6)
        }

        prob = probability_map.get(number, 0.1)
        # Inverse relationship: lower probability = higher bonus
        return (0.2 - prob) * 10  # Scale to reasonable bonus range

    def _calculate_game_phase_bonus(self, game, color: DieColor, number: int) -> float:
        """
        Calculate bonus based on current game phase strategy.

        Args:
            game: The current game instance
            color: The color row
            number: The number being evaluated

        Returns:
            Bonus score based on game phase
        """
        scoresheet = self.get_scoresheet()
        # Only count colored dice rows (exclude WHITE)
        colored_dice = [DieColor.RED, DieColor.YELLOW, DieColor.GREEN, DieColor.BLUE]
        total_marks = sum(len(scoresheet.rows[c].marked) for c in colored_dice)
        locked_colors = len(game.get_locked_colors())
        row = scoresheet.rows[color]

        # Early game (0-8 total marks): Spread strategy
        if total_marks <= 8:
            if len(row.marked) == 0:
                return 2.0  # Bonus for starting new rows
            elif len(row.marked) <= 2:
                return 1.0  # Moderate bonus for early development

        # Mid game (9-16 total marks): Balanced strategy
        elif total_marks <= 16:
            if len(row.marked) >= 2:
                return 2.0  # Focus on developing existing rows
            elif len(row.marked) >= 4:
                return 3.0  # High bonus for rows close to completion

        # Late game (17+ total marks or any locked colors): Focus strategy
        else:
            if len(row.marked) >= 3:
                return 4.0  # Very high bonus for advanced rows
            elif locked_colors >= 1:
                return 5.0  # Emergency focus in endgame

        return 0.0

    def _calculate_enhanced_row_lock_value(
        self, game, color: DieColor, number: int
    ) -> float:
        """
        Calculate enhanced value for locking a row, considering points and strategic denial.

        Args:
            game: The current game instance
            color: The color row
            number: The number being evaluated

        Returns:
            Enhanced value score for row locking
        """
        scoresheet = self.get_scoresheet()
        row = scoresheet.rows[color]

        if not self._can_enable_row_lock(row, number, len(row.marked)):
            return 0.0

        # Base value: points gained from locking
        current_score = row.get_score()
        locked_score = self._calculate_potential_row_score(row, len(row.marked) + 1)
        point_value = locked_score - current_score

        # Strategic denial value: prevent opponents from using this color
        denial_value = 0.0
        for player in game.get_players():
            if player != self:
                other_row = player.get_scoresheet().rows[color]
                opponent_marks = len(other_row.marked)
                if opponent_marks >= 2:
                    # Higher denial value for more advanced opponent rows
                    denial_value += opponent_marks * 1.5

        return point_value * 2.0 + denial_value

    def _calculate_row_synergy_bonus(self, scoresheet, color: DieColor) -> float:
        """
        Calculate bonus for row synergy and balanced development.

        Args:
            scoresheet: The player's scoresheet
            color: The color row being evaluated

        Returns:
            Synergy bonus score
        """
        row = scoresheet.rows[color]
        current_marks = len(row.marked)

        # Calculate marks in other rows (exclude WHITE)
        colored_dice = [DieColor.RED, DieColor.YELLOW, DieColor.GREEN, DieColor.BLUE]
        other_marks = []
        for other_color in colored_dice:
            if other_color != color:
                other_marks.append(len(scoresheet.rows[other_color].marked))

        avg_other_marks = sum(other_marks) / len(other_marks) if other_marks else 0

        # Bonus for balanced development
        if abs(current_marks - avg_other_marks) <= 1:
            return 1.5  # Good balance
        elif current_marks < avg_other_marks - 2:
            return 2.0  # Catch up bonus
        elif current_marks > avg_other_marks + 3:
            return -1.0  # Penalty for over-development

        return 0.0

    def _calculate_early_game_positioning_penalty(
        self, color: DieColor, number: int, marked_count: int
    ) -> float:
        """
        Calculate penalty for poor early game positioning (marking high numbers early).

        Args:
            color: The color row being evaluated
            number: The number being evaluated
            marked_count: Current number of marks in this row

        Returns:
            Penalty score (negative) for bad positioning, 0 otherwise
        """
        # Only apply penalties for early moves in a row (0-2 marks)
        if marked_count > 2:
            return 0.0

        penalty = 0.0

        # For ascending rows (RED, YELLOW): penalize high numbers early
        if color in [DieColor.RED, DieColor.YELLOW]:
            if marked_count == 0:  # First move in row
                if number >= 10:
                    penalty = -20.0  # Severe penalty for 10, 11, 12 as first move
                elif number >= 8:
                    penalty = -10.0  # Strong penalty for 8, 9 as first move
                elif number >= 6:
                    penalty = -5.0  # Moderate penalty for 6, 7 as first move
            elif marked_count == 1:  # Second move in row
                if number >= 11:
                    penalty = -15.0  # Strong penalty for 11, 12 as second move
                elif number >= 9:
                    penalty = -8.0  # Moderate penalty for 9, 10 as second move
            elif marked_count == 2:  # Third move in row
                if number == 12:
                    penalty = -10.0  # Penalty for 12 as third move

        # For descending rows (GREEN, BLUE): penalize low numbers early
        else:
            if marked_count == 0:  # First move in row
                if number <= 3:
                    penalty = -20.0  # Severe penalty for 2, 3 as first move
                elif number <= 5:
                    penalty = -10.0  # Strong penalty for 4, 5 as first move
                elif number <= 7:
                    penalty = -5.0  # Moderate penalty for 6, 7 as first move
            elif marked_count == 1:  # Second move in row
                if number <= 2:
                    penalty = -15.0  # Strong penalty for 2 as second move
                elif number <= 4:
                    penalty = -8.0  # Moderate penalty for 3, 4 as second move
            elif marked_count == 2:  # Third move in row
                if number == 2:
                    penalty = -10.0  # Penalty for 2 as third move

        return penalty

    def _is_bad_early_positioning(self, color: DieColor, number: int) -> bool:
        """
        Check if this would be bad early positioning.

        Args:
            color: The color row being evaluated
            number: The number being evaluated

        Returns:
            True if this is bad early positioning
        """
        if color in [DieColor.RED, DieColor.YELLOW]:
            # For ascending rows, numbers 9+ are bad for early positioning
            return number >= 9
        else:
            # For descending rows, numbers 4 and below are bad for early positioning
            return number <= 4

    def _calculate_red_11_penalty(self, color: DieColor, number: int) -> float:
        """
        Calculate penalty for marking 11 in red row as the first move.

        Args:
            color: The color row being evaluated
            number: The number being evaluated

        Returns:
            Penalty score (negative) if this is a bad Red 11 move, 0 otherwise
        """
        # This is now handled by the more comprehensive early game positioning penalty
        # Keep this method for backward compatibility but make it less severe
        if color != DieColor.RED or number != 11:
            return 0.0

        scoresheet = self.get_scoresheet()
        red_row = scoresheet.rows[DieColor.RED]

        # Apply moderate penalty if red row is empty (first move)
        if len(red_row.marked) == 0:
            return (
                -5.0
            )  # Reduced penalty since early game positioning handles this better

        return 0.0

    def _calculate_advanced_positioning_bonus(
        self, game, color: DieColor, number: int
    ) -> float:
        """
        Calculate advanced positioning bonus considering future opportunities.

        Args:
            game: The current game instance
            color: The color row being evaluated
            number: The number being evaluated

        Returns:
            Bonus score for good positioning strategy
        """
        scoresheet = self.get_scoresheet()
        row = scoresheet.rows[color]
        marked_count = len(row.marked)

        # Calculate how many numbers this move would "block" from future scoring
        blocked_numbers = 0

        if color in [DieColor.RED, DieColor.YELLOW]:
            # For ascending rows, marking a high number blocks all lower numbers
            blocked_numbers = number - 2  # Numbers 2 through (number-1) are blocked
        else:
            # For descending rows, marking a low number blocks all higher numbers
            blocked_numbers = 12 - number  # Numbers (number+1) through 12 are blocked

        # Early in the row, heavily penalize moves that block many future opportunities
        if marked_count <= 2:
            if blocked_numbers >= 8:
                return -25.0  # Severe penalty for blocking 8+ numbers early
            elif blocked_numbers >= 6:
                return -15.0  # Strong penalty for blocking 6-7 numbers early
            elif blocked_numbers >= 4:
                return -8.0  # Moderate penalty for blocking 4-5 numbers early
            elif blocked_numbers <= 2:
                return 5.0  # Bonus for keeping many options open

        # Later in the row, blocking becomes less of an issue
        elif marked_count <= 4:
            if blocked_numbers >= 6:
                return -10.0  # Reduced penalty later in development
            elif blocked_numbers <= 2:
                return 3.0  # Smaller bonus for good positioning

        return 0.0

    def should_make_move_in_stage(self, game, stage: int) -> bool:
        """
        Decide whether to make a move in the given stage using strategic considerations.

        Args:
            game: The current game instance
            stage: 1 for white dice sum stage, 2 for colored combination stage

        Returns:
            True if AI should attempt to make a move, False to pass
        """
        scoresheet = self.get_scoresheet()
        penalty_count = scoresheet.penalties

        # Base probability based on difficulty and stage
        # Increased Stage 1 probabilities to encourage more active play
        if self.difficulty == "easy":
            base_prob = 0.75 if stage == 1 else 0.8
        elif self.difficulty == "medium":
            base_prob = 0.85 if stage == 1 else 0.9
        else:  # hard
            base_prob = 0.9 if stage == 1 else 0.95

        # Adjust probability based on penalty risk
        if penalty_count >= 3:
            base_prob = 0.95  # Almost always try to move when at high penalty risk
        elif penalty_count >= 2:
            base_prob = min(base_prob + 0.1, 0.95)  # Increase probability
        elif penalty_count >= 1:
            base_prob = min(base_prob + 0.05, 0.9)  # Slight increase

        # Adjust based on available moves quality
        available_moves = self.get_available_moves(game)
        best_score = -float("inf")
        if available_moves:
            # Evaluate the best available move
            for color, number in available_moves:
                if self.difficulty == "hard":
                    score = self._evaluate_move_advanced(game, color, number)
                else:
                    score = self._evaluate_move(game, color, number)
                best_score = max(best_score, score)

            # If the best move is very good, increase probability
            if best_score >= 10:
                base_prob = min(base_prob + 0.1, 0.98)
            elif best_score >= 5:
                base_prob = min(base_prob + 0.05, 0.95)
            elif best_score <= 0:
                # For Stage 1, be less aggressive about reducing probability
                if stage == 1:
                    base_prob = max(
                        base_prob - 0.05, 0.5
                    )  # Smaller reduction for Stage 1
                else:
                    base_prob = max(
                        base_prob - 0.1, 0.3
                    )  # Original reduction for Stage 2

        # Add small random factor to avoid predictability
        random_factor = random.uniform(-0.05, 0.05)
        final_prob = max(0.1, min(0.98, base_prob + random_factor))

        decision = random.random() < final_prob

        self.logger.debug(
            f"{self.name} stage {stage} decision: {'participate' if decision else 'skip'} "
            f"(prob={final_prob:.2f}, best_score={best_score:.1f}, penalties={penalty_count})"
        )

        log_game_event(
            "AI_STAGE_DECISION",
            f"{self.name} {'will participate' if decision else 'will skip'} in stage {stage}",
            ai_player=self.name,
            stage=stage,
            decision="participate" if decision else "skip",
            probability=final_prob,
            best_move_score=best_score,
            penalty_count=penalty_count,
            available_moves_count=len(available_moves) if available_moves else 0,
        )

        return decision

    def get_available_moves(self, game) -> List[Tuple[DieColor, int]]:
        """
        Get all available moves for this AI player in the current game state.

        Args:
            game: The current game instance

        Returns:
            List of (color, number) tuples representing valid moves
        """
        available_moves = []
        dice_results = game.get_dice_results()

        if not dice_results:
            return available_moves

        game_state = game.get_state()
        locked_colors = game.get_locked_colors()

        # Check each color row
        for color in DieColor:
            if color in locked_colors:
                continue

            # Stage 1: White dice sum moves
            if game_state == GameState.STAGE_1_MOVES:
                white_sum = dice_results["white1"] + dice_results["white2"]
                if (
                    self.get_scoresheet().can_mark_number(color, white_sum)
                    and self.can_use_white_sum()
                ):
                    available_moves.append((color, white_sum))

            # Stage 2: White + colored combination moves (only for active player)
            elif (
                game_state == GameState.STAGE_2_MOVES
                and self == game.get_current_player()
            ):
                white_colored_sums = game.dice_roller.get_white_plus_colored_sums()
                if color in white_colored_sums:
                    for sum_value in white_colored_sums[color]:
                        if (
                            self.get_scoresheet().can_mark_number(color, sum_value)
                            and self.can_use_colored_combination()
                        ):
                            available_moves.append((color, sum_value))

        return available_moves
