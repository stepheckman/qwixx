import React from 'react';
import { Paper, Typography, Grid, Box, IconButton, Tooltip } from '@mui/material';
import LockIcon from '@mui/icons-material/Lock';
import LockOpenIcon from '@mui/icons-material/LockOpen';

const ScoreSheet = ({ player, onMark, isCurrentPlayer }) => {
    const { scoresheet, name } = player;

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

    return (
        <Paper sx={{ p: 2, mb: 3, opacity: isCurrentPlayer ? 1 : 0.7 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h5" color={isCurrentPlayer ? 'primary' : 'textSecondary'}>
                    {name} {isCurrentPlayer && "(Moving)"}
                </Typography>
                <Box display="flex" gap={2}>
                    <Typography variant="subtitle1">Score: {scoresheet.total_score}</Typography>
                    <Typography variant="subtitle1" color="error">Penalties: {scoresheet.penalties}</Typography>
                </Box>
            </Box>

            {colors.map((color) => {
                const markedIndices = color.numbers
                    .map((num, idx) => scoresheet.marked_numbers[color.name]?.includes(num) ? idx : -1)
                    .filter(idx => idx !== -1);

                const furthestMarkIndex = markedIndices.length > 0 ? Math.max(...markedIndices) : -1;

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
                            overflowX: 'auto'
                        }}
                    >
                        <Box sx={{ minWidth: 80, px: 1, fontWeight: 'bold', color: '#000' }}>
                            {color.label}
                        </Box>
                        <Box display="flex" flexGrow={1} justifyContent="space-around">
                            {color.numbers.map((num, idx) => {
                                const isMarked = scoresheet.marked_numbers[color.name]?.includes(num);
                                const isUnplayable = idx < furthestMarkIndex && !isMarked;

                                return (
                                    <IconButton
                                        key={num}
                                        size="small"
                                        onClick={() => onMark(color.name, num)}
                                        disabled={!isCurrentPlayer || isMarked || isUnplayable}
                                        sx={{
                                            width: 36,
                                            height: 36,
                                            bgcolor: isMarked ? 'rgba(0,0,0,0.5)' :
                                                isUnplayable ? 'rgba(0,0,0,0.1)' : 'rgba(255,255,255,0.2)',
                                            color: isMarked ? '#fff' :
                                                isUnplayable ? 'rgba(0,0,0,0.3)' : '#000',
                                            textDecoration: isUnplayable ? 'line-through' : 'none',
                                            opacity: isUnplayable ? 0.3 : 1,
                                            '&:hover': {
                                                bgcolor: isUnplayable ? 'transparent' : 'rgba(0,0,0,0.3)',
                                            },
                                            fontSize: '0.875rem',
                                            fontWeight: 'bold',
                                            m: 0.2,
                                            position: 'relative',
                                            // Add a custom strike-through for better visibility
                                            '&::after': isUnplayable ? {
                                                content: '""',
                                                position: 'absolute',
                                                width: '100%',
                                                height: '2px',
                                                bgcolor: 'rgba(0,0,0,0.4)',
                                                transform: 'rotate(-45deg)',
                                                top: '50%',
                                                left: 0
                                            } : {}
                                        }}
                                    >
                                        {isMarked ? 'X' : num}
                                    </IconButton>
                                );
                            })}
                        </Box>
                        <Box sx={{ ml: 1, mr: 1, display: 'flex', alignItems: 'center' }}>
                            {/* Row Lock Indicator could go here */}
                        </Box>
                    </Box>
                );
            })}
        </Paper>
    );
};

export default ScoreSheet;
