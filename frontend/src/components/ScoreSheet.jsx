import React from 'react';
import { Paper, Typography, Grid, Box, IconButton, Tooltip } from '@mui/material';
import LockIcon from '@mui/icons-material/Lock';
import LockOpenIcon from '@mui/icons-material/LockOpen';
import { Button } from '@mui/material';

const ScoreSheet = ({ player, onMark, onDone, isCurrentPlayer, gameState }) => {
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
        <Paper sx={{ p: 2, mb: 3, opacity: isCurrentPlayer ? 1 : 0.9 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h5" color={isCurrentPlayer ? 'primary' : 'textSecondary'}>
                    {name} {isCurrentPlayer && "(Moving)"}
                </Typography>
                <Box display="flex" alignItems="center" gap={2}>
                    {!player.is_ai && (
                        <Button
                            variant="contained"
                            size="small"
                            onClick={onDone}
                            disabled={!['STAGE_1_MOVES', 'STAGE_2_MOVES'].includes(gameState)}
                            sx={{ height: 32 }}
                        >
                            Skip Stage
                        </Button>
                    )}
                    <Box display="flex" gap={2}>
                        <Typography variant="subtitle1">Score: {scoresheet.total_score}</Typography>
                        <Typography variant="subtitle1" color="error">Penalties: {scoresheet.penalties}</Typography>
                    </Box>
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
                                        disabled={
                                            player.is_ai ||
                                            (gameState === 'STAGE_1_MOVES' ? false : !isCurrentPlayer) ||
                                            isMarked ||
                                            isUnplayable
                                        }
                                        sx={{
                                            width: 36,
                                            height: 36,
                                            bgcolor: isMarked ? 'rgba(0,0,0,0.8)' :
                                                isUnplayable ? 'rgba(0,0,0,0.2)' : 'rgba(255,255,255,0.2)',
                                            color: isMarked ? '#fff' :
                                                isUnplayable ? 'rgba(0,0,0,0.5)' : '#000',
                                            textDecoration: isUnplayable ? 'line-through' : 'none',
                                            opacity: 1, // Control visibility via rgba instead of overall element opacity
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
                                                bgcolor: 'rgba(0,0,0,0.6)',
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
                            <Box
                                sx={{
                                    width: 24,
                                    height: 24,
                                    borderRadius: '50%',
                                    bgcolor: 'rgba(255,255,255,0.3)',
                                    display: 'flex',
                                    justifyContent: 'center',
                                    alignItems: 'center',
                                    fontSize: '0.75rem',
                                    fontWeight: 'bold',
                                    color: '#000',
                                    border: '1px solid rgba(0,0,0,0.2)'
                                }}
                                title="Checked boxes count"
                            >
                                {markedIndices.length}
                            </Box>
                        </Box>
                    </Box>
                );
            })}
        </Paper>
    );
};

export default ScoreSheet;
