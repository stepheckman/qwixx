import React, { useState } from 'react';
import { Paper, Typography, Button, Box, ToggleButtonGroup, ToggleButton, Collapse } from '@mui/material';

const AI_STRATEGIES = [
    { label: 'Easy', value: 'easy' },
    { label: 'Medium', value: 'medium' },
    { label: 'Alpha-Qwixx', value: 'rl' },
];

const GameSetup = ({ onStartGame }) => {
    const [numPlayers, setNumPlayers] = useState(1);
    const [aiStrategy, setAiStrategy] = useState('medium');

    const handleStart = () => {
        onStartGame(numPlayers, numPlayers === 1 ? aiStrategy : null);
    };

    return (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h4" gutterBottom>Qwixx</Typography>
            <Typography variant="subtitle1" color="textSecondary" sx={{ mb: 4 }}>
                Set up your game
            </Typography>

            <Box sx={{ mb: 3 }}>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                    Number of Players
                </Typography>
                <ToggleButtonGroup
                    value={numPlayers}
                    exclusive
                    onChange={(e, val) => val !== null && setNumPlayers(val)}
                    size="large"
                >
                    <ToggleButton value={1}>1 Player</ToggleButton>
                    <ToggleButton value={2}>2 Players</ToggleButton>
                </ToggleButtonGroup>
            </Box>

            <Collapse in={numPlayers === 1}>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                        AI Difficulty
                    </Typography>
                    <ToggleButtonGroup
                        value={aiStrategy}
                        exclusive
                        onChange={(e, val) => val !== null && setAiStrategy(val)}
                        size="large"
                    >
                        {AI_STRATEGIES.map(({ label, value }) => (
                            <ToggleButton key={value} value={value}>{label}</ToggleButton>
                        ))}
                    </ToggleButtonGroup>
                </Box>
            </Collapse>

            <Button
                variant="contained"
                color="primary"
                size="large"
                onClick={handleStart}
                sx={{ mt: 1 }}
            >
                Start Game
            </Button>
        </Paper>
    );
};

export default GameSetup;
