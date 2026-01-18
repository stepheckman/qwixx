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

const DiceDisplay = ({ results }) => {
    if (!results) return <Typography color="textSecondary">Roll to start</Typography>;

    return (
        <Grid container spacing={2} justifyContent="center">
            <Grid item>
                <Box display="flex" gap={1}>
                    <Die value={results.white1} color="white" label="W1" />
                    <Die value={results.white2} color="white" label="W2" />
                </Box>
            </Grid>
            <Grid item xs={12}>
                <Box display="flex" gap={1} justifyContent="center" flexWrap="wrap">
                    <Die value={results.red} color="red" label="R" />
                    <Die value={results.yellow} color="yellow" label="Y" />
                    <Die value={results.green} color="green" label="G" />
                    <Die value={results.blue} color="blue" label="B" />
                </Box>
            </Grid>
        </Grid>
    );
};

export default DiceDisplay;
