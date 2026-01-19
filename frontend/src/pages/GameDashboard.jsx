import React, { useState, useEffect } from 'react';
import { Container, Grid, Paper, Typography, Button, Box, Alert, CircularProgress } from '@mui/material';
import { gameApi } from '../api/client';
import ScoreSheet from '../components/ScoreSheet';
import DiceDisplay from '../components/DiceDisplay';

const GameDashboard = () => {
    const [gameState, setGameState] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchGameState = async () => {
        try {
            const response = await gameApi.getState();
            setGameState(response.data);
            setError(null);
        } catch (err) {
            setError('Failed to fetch game state');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchGameState();
    }, []);

    const handleSetup = async () => {
        setLoading(true);
        try {
            const response = await gameApi.setup(1, 'medium');
            setGameState(response.data);
        } catch (err) {
            setError('Failed to setup game');
        } finally {
            setLoading(false);
        }
    };

    const handleRoll = async () => {
        try {
            const response = await gameApi.roll();
            setGameState(response.data);
        } catch (err) {
            setError('Failed to roll dice');
        }
    };

    const handleMark = async (color, number) => {
        try {
            const response = await gameApi.mark(color, number);
            setGameState(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Invalid move');
        }
    };

    const handleDone = async () => {
        try {
            const response = await gameApi.done();
            setGameState(response.data);
        } catch (err) {
            setError('Failed to finish turn');
        }
    };

    if (loading) return (
        <Box display="flex" justifyContent="center" alignItems="center" height="80vh">
            <CircularProgress />
        </Box>
    );

    if (!gameState) return (
        <Container maxWidth="md">
            <Paper sx={{ p: 4, textAlign: 'center' }}>
                <Typography variant="h4" gutterBottom>Qwixx</Typography>
                <Button variant="contained" color="primary" onClick={handleSetup} size="large">
                    Start New Game
                </Button>
            </Paper>
        </Container>
    );

    return (
        <Container maxWidth="lg">
            <Grid container spacing={3}>
                {error && (
                    <Grid item xs={12}>
                        <Alert severity="error" onClose={() => setError(null)}>{error}</Alert>
                    </Grid>
                )}

                <Grid item xs={12} md={8}>
                    {gameState.players.map((player) => (
                        <ScoreSheet
                            key={player.id}
                            player={player}
                            onMark={handleMark}
                            isCurrentPlayer={gameState.players[gameState.current_player_index].id === player.id}
                        />
                    ))}
                </Grid>

                <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 2, position: 'sticky', top: 20 }}>
                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                            <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                                {gameState.state.includes('STAGE_1') ? 'Stage 1' :
                                    gameState.state.includes('STAGE_2') ? 'Stage 2' : 'Dice'}
                            </Typography>
                            <Box display="flex" gap={1}>
                                <Button
                                    variant="contained"
                                    size="small"
                                    onClick={handleRoll}
                                    disabled={gameState.state !== 'WAITING_FOR_ROLL'}
                                    sx={{ minWidth: 'unset', px: 2 }}
                                >
                                    Roll
                                </Button>
                                <Button
                                    variant="outlined"
                                    size="small"
                                    onClick={handleDone}
                                    disabled={!['STAGE_1_MOVES', 'STAGE_2_MOVES'].includes(gameState.state)}
                                    sx={{ minWidth: 'unset', px: 2 }}
                                >
                                    Done
                                </Button>
                            </Box>
                        </Box>

                        <DiceDisplay results={gameState.dice_results} state={gameState.state} />
                    </Paper>
                </Grid>
            </Grid>
        </Container>
    );
};

export default GameDashboard;
