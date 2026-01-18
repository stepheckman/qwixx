import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import ScoreSheet from '../components/ScoreSheet';

describe('ScoreSheet', () => {
  const basePlayer = {
    id: 1,
    name: 'Ada',
    scoresheet: {
      total_score: 12,
      penalties: 1,
      marked_numbers: {
        red: [2],
        yellow: [],
        green: [],
        blue: [],
      },
    },
  };

  it('renders player info and a marked number', () => {
    render(<ScoreSheet player={basePlayer} onMark={() => {}} isCurrentPlayer={false} />);

    expect(screen.getByText('Ada')).toBeInTheDocument();
    expect(screen.getByText('Score: 12')).toBeInTheDocument();
    expect(screen.getByText('Penalties: 1')).toBeInTheDocument();

    const markedButton = screen.getByRole('button', { name: 'X' });
    expect(markedButton).toBeDisabled();
  });

  it('calls onMark when the current player selects a number', async () => {
    const onMark = vi.fn();
    const user = userEvent.setup();

    render(<ScoreSheet player={basePlayer} onMark={onMark} isCurrentPlayer />);

    const numberButtons = screen.getAllByRole('button', { name: '3' });
    await user.click(numberButtons[0]);

    expect(onMark).toHaveBeenCalledWith('red', 3);
  });
});
