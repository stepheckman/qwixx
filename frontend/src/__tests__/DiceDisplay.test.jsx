import { render, screen } from '@testing-library/react';
import DiceDisplay from '../components/DiceDisplay';

describe('DiceDisplay', () => {
  it('shows a prompt before any roll results', () => {
    render(<DiceDisplay results={null} />);

    expect(screen.getByText('Roll to start')).toBeInTheDocument();
  });

  it('renders die values and white sum when results exist', () => {
    const results = {
      white1: 1,
      white2: 2,
      red: 3,
      yellow: 4,
      green: 5,
      blue: 6,
    };

    render(<DiceDisplay results={results} state="STAGE_1_MOVES" />);

    // Individual dice and white sum (1, 2, 3)
    expect(screen.getAllByText('1').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('2').length).toBeGreaterThanOrEqual(1);

    // white sum is 3 (1+2), red die is also 3
    expect(screen.getAllByText('3').length).toBeGreaterThanOrEqual(2);

    // W1 (1) + Red (3) = 4. Yellow die is also 4.
    expect(screen.getAllByText('4').length).toBeGreaterThanOrEqual(2);

    // W1 (1) + Blue (6) = 7. Blue die is 6.
    expect(screen.getAllByText('7').length).toBeGreaterThanOrEqual(1);

    // W2 (2) + Blue (6) = 8
    expect(screen.getAllByText('8').length).toBeGreaterThanOrEqual(1);

    // Check White Sum label
    expect(screen.getByText('WHITE SUM')).toBeInTheDocument();
  });
});
