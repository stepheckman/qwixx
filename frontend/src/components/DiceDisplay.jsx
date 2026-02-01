import React from 'react';
import { Box, Paper, Typography, Grid } from '@mui/material';

const Die = ({ value, color, label }) => {
    const getColors = (c) => {
        switch (c) {
            case 'red': return { bg: '#ef5350', text: '#fff' };
            case 'yellow': return { bg: '#ffca28', text: '#000' };
            case 'green': return { bg: '#66bb6a', text: '#fff' };
            case 'blue': return { bg: '#42a5f5', text: '#fff' };
            case 'white': return { bg: '#ffffff', text: '#000' };
            default: return { bg: '#ccc', text: '#000' };
        }
    };

    const { bg, text } = getColors(color);

    return (
        <Box textAlign="center">
            <Paper
                elevation={4}
                sx={{
                    width: 50,
                    height: 50,
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    bgcolor: bg,
                    color: text,
                    fontSize: '1.5rem',
                    fontWeight: 'bold',
                    borderRadius: 2,
                    mb: 0.5,
                    border: '2px solid rgba(0,0,0,0.1)'
                }}
            >
                {value || '?'}
            </Paper>
            <Typography variant="caption" color="textSecondary">{label}</Typography>
        </Box>
    );
};

const DiceDisplay = ({ results, state, part = 'all', isActivePlayerAi }) => {
    if (!results) return <Typography color="textSecondary">Roll to start</Typography>;

    const whiteSum = (results.white1 || 0) + (results.white2 || 0);

    const colors = [
        { name: 'Red', key: 'red', bg: '#ef5350' },
        { name: 'Yellow', key: 'yellow', bg: '#ffca28' },
        { name: 'Green', key: 'green', bg: '#66bb6a' },
        { name: 'Blue', key: 'blue', bg: '#42a5f5' }
    ];

    const renderDiceValues = () => (
        <Box>
            <Grid container spacing={1} justifyContent="center" alignItems="center">
                <Grid item>
                    <Box display="flex" gap={1}>
                        <Die value={results.white1} color="white" label="W1" />
                        <Die value={results.white2} color="white" label="W2" />
                    </Box>
                </Grid>
            </Grid>

            {/* Colored Dice Row */}
            <Box mt={1}>
                <Box display="flex" gap={1} justifyContent="center" flexWrap="wrap">
                    <Die value={results.red} color="red" label="R" />
                    <Die value={results.yellow} color="yellow" label="Y" />
                    <Die value={results.green} color="green" label="G" />
                    <Die value={results.blue} color="blue" label="B" />
                </Box>
            </Box>
        </Box>
    );

    const renderPlayableNumbers = () => (
        <Box>
            {/* White Sum Box above table - ensure it's centered */}
            <Box mb={2} display="flex" justifyContent="center" width="100%">
                <Box textAlign="center">
                    <Paper
                        elevation={4}
                        sx={{
                            width: 50,
                            height: 50,
                            display: 'flex',
                            justifyContent: 'center',
                            alignItems: 'center',
                            bgcolor: '#ffffff',
                            border: '3px solid #1976d2',
                            borderRadius: 2,
                            mb: 0.5,
                            fontSize: '1.5rem',
                            fontWeight: 'bold',
                            color: '#000',
                            boxShadow: '0 0 10px rgba(25, 118, 210, 0.3)',
                            mx: 'auto', // ensure margin auto for centering
                            opacity: state === 'STAGE_1_MOVES' ? 1 : 0.4,
                            filter: state === 'STAGE_1_MOVES' ? 'none' : 'grayscale(1)',
                            transition: 'all 0.3s ease'
                        }}
                    >
                        {whiteSum}
                    </Paper>
                    <Typography variant="caption" color="primary" sx={{ fontWeight: 'bold' }}>WHITE SUM</Typography>
                </Box>
            </Box>

            <Box mt={1}>
                <Typography variant="caption" color="textSecondary" align="center" display="block" gutterBottom sx={{ fontSize: '0.7rem', opacity: 0.8 }}>
                    White + Colored Combinations
                </Typography>
                <Box sx={{ overflowX: 'auto', pb: 1 }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'center' }}>
                        <thead>
                            <tr>
                                <th style={{ padding: '2px' }}><Typography variant="caption">W1+</Typography></th>
                                <th style={{ padding: '2px' }}><Typography variant="caption">W2+</Typography></th>
                            </tr>
                        </thead>
                        <tbody>
                            {colors.map((c) => {
                                // Dimmed if:
                                // 1. It's the AI's turn (they are never playable for the human)
                                // 2. It's anyone's Stage 1 (they are not yet playable)
                                const isDimmedByStage = state === 'STAGE_1_MOVES';
                                const isDimmedByAi = isActivePlayerAi;

                                return (
                                    <tr
                                        key={c.key}
                                        style={{
                                            opacity: isDimmedByAi ? 0.2 : (isDimmedByStage ? 0.4 : 1),
                                            filter: isDimmedByAi ? 'grayscale(1)' : (isDimmedByStage ? 'grayscale(0.5)' : 'none'),
                                            transition: 'all 0.3s ease'
                                        }}
                                    >
                                        <td style={{ padding: '2px' }}>
                                            <Paper elevation={1} sx={{ p: 0.5, bgcolor: c.bg, color: c.key === 'yellow' ? '#000' : '#fff', fontWeight: 'bold', fontSize: '0.875rem' }}>
                                                {(results.white1 || 0) + (results[c.key] || 0)}
                                            </Paper>
                                        </td>
                                        <td style={{ padding: '2px' }}>
                                            <Paper elevation={1} sx={{ p: 0.5, bgcolor: c.bg, color: c.key === 'yellow' ? '#000' : '#fff', fontWeight: 'bold', fontSize: '0.875rem' }}>
                                                {(results.white2 || 0) + (results[c.key] || 0)}
                                            </Paper>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </Box>
            </Box>
        </Box>
    );

    if (part === 'values') return renderDiceValues();
    if (part === 'numbers') return renderPlayableNumbers();

    return (
        <Box>
            {renderDiceValues()}
            <Box mt={2}>
                {renderPlayableNumbers()}
            </Box>
        </Box>
    );
};

export default DiceDisplay;
