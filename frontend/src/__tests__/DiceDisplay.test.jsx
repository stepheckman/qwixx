import { render, screen } from '@testing-library/react';
import DiceDisplay from '../components/DiceDisplay';

describe('DiceDisplay', () => {
  it('shows a prompt before any roll results', () => {
    render(<DiceDisplay results={null} />);

    expect(screen.getByText('Roll to start')).toBeInTheDocument();
  });

  it('renders die values when results exist', () => {
    const results = {
      white1: 1,
      white2: 2,
      red: 3,
      yellow: 4,
      green: 5,
      blue: 6,
    };

    render(<DiceDisplay results={results} />);

    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('6')).toBeInTheDocument();
  });
});
