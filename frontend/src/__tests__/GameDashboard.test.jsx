import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import GameDashboard from '../pages/GameDashboard';
import { gameApi } from '../api/client';

vi.mock('../api/client', () => ({
  gameApi: {
    getState: vi.fn(),
    setup: vi.fn(),
    roll: vi.fn(),
    mark: vi.fn(),
    done: vi.fn(),
  },
}));

describe('GameDashboard', () => {
  it('allows starting a new game when no state exists', async () => {
    const user = userEvent.setup();
    const newGameState = {
      message: 'Ready',
      state: 'WAITING_FOR_ROLL',
      current_player_index: 0,
      dice_results: {
        white1: 1,
        white2: 2,
        red: 3,
        yellow: 4,
        green: 5,
        blue: 6,
      },
      players: [
        {
          id: 1,
          name: 'Player 1',
          scoresheet: {
            total_score: 0,
            penalties: 0,
            marked_numbers: {
              red: [],
              yellow: [],
              green: [],
              blue: [],
            },
          },
        },
      ],
    };

    gameApi.getState.mockResolvedValue({ data: null });
    gameApi.setup.mockResolvedValue({ data: newGameState });

    render(<GameDashboard />);

    const startButton = await screen.findByRole('button', { name: /start new game/i });
    await user.click(startButton);

    expect(gameApi.setup).toHaveBeenCalledWith(1, 'medium');
    expect(await screen.findByText('Ready')).toBeInTheDocument();
  });
});
