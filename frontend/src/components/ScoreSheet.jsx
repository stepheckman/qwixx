import React from 'react';
import { Paper, Typography, Box, IconButton } from '@mui/material';
import LockIcon from '@mui/icons-material/Lock';

const ScoreSheet = ({ player, onMark, isCurrentPlayer, validMoveSet, lockedColors, isGameOver }) => {
    const name = player.name;
    const scoresheet = {
        total_score: player.scoresheet.total_score,
        penalties: player.scoresheet.penalties,
        marked_numbers: player.scoresheet.marked_numbers,
    };

    const colors = [
        { name: 'red', label: 'RED', numbers: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] },
        { name: 'yellow', label: 'YELLOW', numbers: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] },
        { name: 'green', label: 'GREEN', numbers: [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2] },
        { name: 'blue', label: 'BLUE', numbers: [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2] },
    ];

    const getColorCode = (colorName) => {
        switch (colorName) {
            case 'red': return '#ef5350';
            case 'yellow': return '#ffca28';
            case 'green': return '#66bb6a';
            case 'blue': return '#42a5f5';
            default: return '#fff';
        }
    };

    const isRowLocked = (colorName) => (lockedColors || []).includes(colorName);

    return (
        <Paper sx={{ p: 2, mb: 3, opacity: isCurrentPlayer ? 1 : 0.7 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h5" color={isCurrentPlayer ? 'primary' : 'textSecondary'}>
                    {name} {isCurrentPlayer && !isGameOver && "(Moving)"}
                </Typography>
                <Box display="flex" gap={2}>
                    <Typography variant="subtitle1">Score: {scoresheet.total_score}</Typography>
                    <Typography variant="subtitle1" color="error">Penalties: {scoresheet.penalties}</Typography>
                </Box>
            </Box>

            {colors.map((color) => {
                const locked = isRowLocked(color.name);
                return (
                    <Box
                        key={color.name}
                        sx={{
                            display: 'flex',
                            alignItems: 'center',
                            bgcolor: getColorCode(color.name),
                            borderRadius: 1,
                            mb: 1,
                            p: 0.5,
                            overflowX: 'auto',
                            opacity: locked ? 0.5 : 1,
                        }}
                    >
                        <Box sx={{ minWidth: 80, px: 1, fontWeight: 'bold', color: '#000' }}>
                            {color.label}
                        </Box>
                        <Box display="flex" flexGrow={1} gap={0.4}>
                            {color.numbers.map((num) => {
                                const isMarked = scoresheet.marked_numbers[color.name]?.includes(num);
                                const isValidMove = validMoveSet.has(`${player.id}:${color.name}:${num}`);
                                const disabled = isGameOver || locked || isMarked || !isValidMove;
                                return (
                                    <IconButton
                                        key={num}
                                        size="small"
                                        onClick={() => onMark(player.id, color.name, num)}
                                        disabled={disabled}
                                        sx={{
                                            flex: 1,
                                            minWidth: 36,
                                            height: 36,
                                            bgcolor: isMarked
                                                ? '#222'
                                                : isValidMove && !isGameOver
                                                    ? 'rgba(255,255,255,0.7)'
                                                    : 'rgba(255,255,255,0.2)',
                                            color: isMarked ? '#fff' : '#000',
                                            '&.Mui-disabled': isMarked ? {
                                                color: '#fff',
                                            } : {},
                                            '&:hover': {
                                                bgcolor: 'rgba(0,0,0,0.3)',
                                            },
                                            fontSize: isMarked ? '1.2rem' : '0.875rem',
                                            fontWeight: 'bold',
                                            border: isMarked
                                                ? '2px solid #fff'
                                                : isValidMove && !isMarked && !isGameOver
                                                    ? '2px solid rgba(0,0,0,0.4)'
                                                    : '2px solid transparent',
                                        }}
                                    >
                                        {isMarked ? 'X' : num}
                                    </IconButton>
                                );
                            })}
                        </Box>
                        <Box sx={{ ml: 1, mr: 1, display: 'flex', alignItems: 'center', minWidth: 28 }}>
                            {locked && <LockIcon sx={{ color: '#000', fontSize: 20 }} />}
                        </Box>
                    </Box>
                );
            })}
        </Paper>
    );
};

export default ScoreSheet;
