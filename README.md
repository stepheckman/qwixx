# Qwixx - Python Implementation

A Python implementation of the popular dice game Qwixx using Pygame for the graphical user interface.

## About Qwixx

Qwixx is a fast-paced dice game where players try to mark off numbers in four colored rows on their scoresheet. The game combines strategy with luck as players must decide which numbers to mark and when to take risks.

### Game Rules

- **Players**: 2-4 players (currently supports 2 players)
- **Dice**: 6 dice total - 2 white dice and 4 colored dice (red, yellow, green, blue)
- **Objective**: Score the most points by marking numbers in colored rows

#### How to Play

1. **Turn Structure**: Players take turns being the "active player"
2. **Rolling Dice**: The active player rolls all 6 dice
3. **Marking Numbers**: 
   - **All players** can mark the sum of the two white dice in any colored row
   - **Active player only** can also mark the sum of one white die + one colored die in the matching colored row
4. **Row Rules**:
   - Red and Yellow rows: numbers 2-12 (left to right)
   - Green and Blue rows: numbers 12-2 (left to right)
   - Numbers must be marked from left to right (no skipping back)
5. **Locking Rows**: A row can be locked when:
   - At least 5 numbers are marked in that row
   - The rightmost number (12 for red/yellow, 2 for green/blue) is marked
6. **Penalties**: If a player cannot or chooses not to mark any number, they get a penalty (-5 points)
7. **Game End**: The game ends when either:
   - Two colored rows are locked, OR
   - Any player reaches 4 penalties

#### Scoring

- Points are awarded based on the number of marks in each row:
  - 1 mark = 1 point
  - 2 marks = 3 points  
  - 3 marks = 6 points
  - 4 marks = 10 points
  - 5 marks = 15 points
  - And so on... (formula: n × (n + 1) ÷ 2)
- Each penalty = -5 points
- Player with the highest total score wins!

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package installer)

### Setup

1. Clone or download this repository
2. Navigate to the project directory:
   ```bash
   cd qwixx_with_roo
   ```

3. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install pygame
   ```

## Running the Game

To start the game, run:

```bash
python main.py
```

Or if using the virtual environment:

```bash
.venv/bin/python main.py
```

## How to Play the Digital Version

1. **Start the Game**: Run the main.py file to open the game window
2. **Roll Dice**: Click the "Roll Dice" button to roll all six dice
3. **Mark Numbers**: Click on available numbers in the colored rows to mark them
4. **Pass Turn**: Click "Pass Turn" if you cannot or don't want to mark any numbers (results in a penalty)
5. **Game Progress**: The game automatically manages turns and tracks scores
6. **Visual Feedback**: 
   - Available numbers are highlighted when you hover over them
   - Marked numbers appear in the row's color
   - The active player's name is shown in red
   - Current dice results and white dice sum are displayed

## Project Structure

```
qwixx_with_roo/
├── main.py                 # Main entry point
├── src/
│   ├── __init__.py
│   ├── die.py             # Die and DieColor classes
│   ├── dice_roller.py     # DiceRoller class for managing all dice
│   ├── scoresheet.py      # Scoresheet and ColorRow classes
│   ├── player.py          # Player class
│   ├── game_state.py      # GameState enumeration
│   ├── game.py            # Main Game class with game logic
│   └── gui.py             # Pygame GUI implementation
├── pyproject.toml         # Project configuration
├── README.md              # This file
└── .gitignore            # Git ignore rules
```

## Features

### Implemented Features

✅ **Core Game Mechanics**
- Complete Qwixx rule implementation
- Dice rolling with 6 dice (2 white + 4 colored)
- Scoresheet management with proper validation
- Turn-based gameplay
- Penalty system
- Row locking mechanism
- Automatic game end detection
- Score calculation

✅ **Pygame GUI**
- Visual scoresheets for all players
- Interactive number selection
- Dice result display
- Roll dice and pass turn buttons
- Visual feedback for valid/invalid moves
- Player turn indication
- Real-time score tracking

✅ **Game Logic**
- Proper move validation (left-to-right marking)
- White dice sum available to all players
- White + colored combinations for active player only
- Row locking rules (5+ marks + rightmost number)
- Game end conditions (2 locked rows or 4 penalties)

### Potential Enhancements

The following features could be added in future versions:

- Support for 3-4 players
- Sound effects and music
- Improved UI/UX with better graphics
- Start screen and game over screen
- Save/load game functionality
- AI opponents
- Online multiplayer
- Game statistics and history
- Different difficulty levels
- Customizable rules

## Technical Details

- **Language**: Python 3.13+
- **GUI Framework**: Pygame 2.6+
- **Architecture**: Object-oriented design with separate classes for game logic and GUI
- **Design Patterns**: Model-View separation, State pattern for game states

## Contributing

This project was created as a learning exercise. Feel free to fork and enhance it with additional features!

## License

This project is for educational purposes. Qwixx is a trademark of Nürnberger-Spielkarten-Verlag GmbH.