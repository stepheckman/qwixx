import React, { useState, useEffect } from 'react';
import { Container, Grid, Paper, Typography, Button, Box, Alert, CircularProgress, Dialog, DialogTitle, DialogContent, DialogActions } from '@mui/material';
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

    const [setupOptions, setSetupOptions] = useState({
        numPlayers: 1,
        aiStrategy: 'easy'
    });

    const handleSetup = async () => {
        setLoading(true);
        try {
            const response = await gameApi.setup(setupOptions.numPlayers, setupOptions.aiStrategy);
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

    const handleMark = async (playerId, color, number) => {
        try {
            const response = await gameApi.mark(playerId, color, number);
            setGameState(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Invalid move');
        }
    };

    const handleDone = async (playerId) => {
        try {
            const response = await gameApi.done(playerId);
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
            <Paper sx={{
                p: 4,
                textAlign: 'center',
                mt: 8,
                background: 'linear-gradient(135deg, #1a237e 0%, #0d47a1 100%)',
                color: 'white',
                borderRadius: 4,
                boxShadow: 10
            }}>
                <Typography variant="h2" gutterBottom sx={{ fontWeight: 'bold', mb: 4 }}>Qwixx</Typography>

                <Box sx={{ mb: 4, textAlign: 'left', maxWidth: 400, mx: 'auto' }}>
                    <Typography variant="h6" gutterBottom>Number of Players</Typography>
                    <Grid container spacing={2} sx={{ mb: 3 }}>
                        <Grid item xs={6}>
                            <Button
                                fullWidth
                                variant={setupOptions.numPlayers === 1 ? "contained" : "outlined"}
                                onClick={() => setSetupOptions({ ...setupOptions, numPlayers: 1 })}
                                sx={{
                                    color: 'white',
                                    borderColor: 'white',
                                    bgcolor: setupOptions.numPlayers === 1 ? '#42a5f5' : 'transparent',
                                    '&:hover': {
                                        bgcolor: setupOptions.numPlayers === 1 ? '#1e88e5' : 'rgba(255,255,255,0.1)',
                                        borderColor: 'white'
                                    }
                                }}
                            >
                                1 Player
                            </Button>
                        </Grid>
                        <Grid item xs={6}>
                            <Button
                                fullWidth
                                variant={setupOptions.numPlayers === 2 ? "contained" : "outlined"}
                                onClick={() => setSetupOptions({ ...setupOptions, numPlayers: 2 })}
                                sx={{
                                    color: 'white',
                                    borderColor: 'white',
                                    bgcolor: setupOptions.numPlayers === 2 ? '#ffca28' : 'transparent',
                                    '&:hover': {
                                        bgcolor: setupOptions.numPlayers === 2 ? '#ffb300' : 'rgba(255,255,255,0.1)',
                                        borderColor: 'white'
                                    }
                                }}
                            >
                                2 Players
                            </Button>
                        </Grid>
                    </Grid>

                    {setupOptions.numPlayers === 1 && (
                        <>
                            <Typography variant="h6" gutterBottom>AI Difficulty</Typography>
                            <Grid container spacing={2}>
                                <Grid item xs={6}>
                                    <Button
                                        fullWidth
                                        variant={setupOptions.aiStrategy === 'easy' ? "contained" : "outlined"}
                                        onClick={() => setSetupOptions({ ...setupOptions, aiStrategy: 'easy' })}
                                        sx={{
                                            color: 'white',
                                            borderColor: 'white',
                                            bgcolor: setupOptions.aiStrategy === 'easy' ? '#66bb6a' : 'transparent',
                                            '&:hover': {
                                                bgcolor: setupOptions.aiStrategy === 'easy' ? '#43a047' : 'rgba(255,255,255,0.1)',
                                                borderColor: 'white'
                                            }
                                        }}
                                    >
                                        Easy
                                    </Button>
                                </Grid>
                                <Grid item xs={6}>
                                    <Button
                                        fullWidth
                                        variant={setupOptions.aiStrategy === 'hard' ? "contained" : "outlined"}
                                        onClick={() => setSetupOptions({ ...setupOptions, aiStrategy: 'hard' })}
                                        sx={{
                                            color: 'white',
                                            borderColor: 'white',
                                            bgcolor: setupOptions.aiStrategy === 'hard' ? '#ef5350' : 'transparent',
                                            '&:hover': {
                                                bgcolor: setupOptions.aiStrategy === 'hard' ? '#e53935' : 'rgba(255,255,255,0.1)',
                                                borderColor: 'white'
                                            }
                                        }}
                                    >
                                        Hard
                                    </Button>
                                </Grid>
                            </Grid>
                        </>
                    )}
                </Box>

                <Button
                    variant="contained"
                    onClick={handleSetup}
                    size="large"
                    sx={{
                        px: 6,
                        py: 1.5,
                        fontSize: '1.2rem',
                        fontWeight: 'bold',
                        borderRadius: 2,
                        bgcolor: '#ef5350',
                        color: 'white',
                        '&:hover': {
                            bgcolor: '#d32f2f'
                        }
                    }}
                >
                    Start Game
                </Button>
            </Paper>
        </Container>
    );

    return (
        <Container maxWidth="lg">
            {/* Header / Message Area */}
            <Box sx={{ mb: 3 }}>
                {error && (
                    <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>{error}</Alert>
                )}

                {gameState.message && (
                    <Paper
                        elevation={0}
                        sx={{
                            p: 2,
                            textAlign: 'center',
                            background: 'rgba(255, 255, 255, 0.05)',
                            backdropFilter: 'blur(10px)',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: 2,
                            color: 'white'
                        }}
                    >
                        <Typography variant="h5" sx={{ fontWeight: 500 }}>
                            {gameState.message}
                        </Typography>
                    </Paper>
                )}
            </Box>

            <Grid container spacing={3}>


                {/* Main Content - Scoresheets */}
                <Grid item xs={12} md={8}>
                    {gameState.players.map((player) => (
                        <ScoreSheet
                            key={player.id}
                            player={player}
                            onMark={(color, num) => handleMark(player.id, color, num)}
                            onDone={() => handleDone(player.id)}
                            isCurrentPlayer={gameState.players[gameState.current_player_index].id === player.id}
                            gameState={gameState.state}
                        />
                    ))}
                </Grid>

                {/* Sidebar - Dice and Actions */}
                <Grid item xs={12} md={4}>
                    <Box sx={{ position: 'sticky', top: 20 }}>
                        {/* Dice Values Box */}
                        <Paper sx={{ p: 2, mb: 2 }}>
                            <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
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
                                </Box>
                            </Box>

                            <DiceDisplay
                                results={gameState.dice_results}
                                state={gameState.state}
                                part="values"
                                isActivePlayerAi={gameState.players[gameState.current_player_index].is_ai}
                            />
                        </Paper>

                        {/* Playable Numbers Box */}
                        <Paper sx={{ p: 2, mb: 2 }}>
                            <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2, textAlign: 'center' }}>
                                Playable Numbers
                            </Typography>
                            <DiceDisplay
                                results={gameState.dice_results}
                                state={gameState.state}
                                part="numbers"
                                isActivePlayerAi={gameState.players[gameState.current_player_index].is_ai}
                            />
                        </Paper>

                        <Button
                            variant="contained"
                            fullWidth
                            onClick={() => setGameState(null)}
                            sx={{
                                py: 1.5,
                                fontWeight: 'bold',
                                bgcolor: 'rgba(255,255,255,0.05)',
                                color: 'text.secondary',
                                border: '1px dashed rgba(255,255,255,0.2)',
                                '&:hover': {
                                    bgcolor: 'rgba(255,255,255,0.1)',
                                    color: 'primary.main',
                                    borderColor: 'primary.main'
                                }
                            }}
                        >
                            + New Game
                        </Button>
                    </Box>
                </Grid>
            </Grid>

            {/* Game Over Dialog */}
            <Dialog
                open={gameState.state === 'GAME_OVER'}
                maxWidth="sm"
                fullWidth
                PaperProps={{
                    sx: {
                        borderRadius: 4,
                        background: 'linear-gradient(135deg, #1a237e 0%, #0d47a1 100%)',
                        color: 'white',
                        p: 2
                    }
                }}
            >
                <DialogTitle sx={{ textAlign: 'center', fontSize: '2.5rem', fontWeight: 'bold' }}>
                    Game Over!
                </DialogTitle>
                <DialogContent>
                    <Typography variant="h5" align="center" gutterBottom sx={{ mb: 4 }}>
                        {gameState.message}
                    </Typography>

                    <Box sx={{ bgcolor: 'rgba(255,255,255,0.1)', borderRadius: 2, p: 3 }}>
                        <Typography variant="h6" gutterBottom sx={{ borderBottom: '1px solid rgba(255,255,255,0.3)', pb: 1, mb: 2 }}>
                            Final Scores
                        </Typography>
                        {gameState.players.map((player) => (
                            <Box key={player.id} display="flex" justifyContent="space-between" mb={1}>
                                <Typography variant="body1" sx={{ fontWeight: player.is_active ? 'bold' : 'normal' }}>
                                    {player.name} {player.is_ai ? '(AI)' : ''}
                                </Typography>
                                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                                    {player.scoresheet.total_score} pts
                                </Typography>
                            </Box>
                        ))}
                    </Box>
                </DialogContent>
                <DialogActions sx={{ justifyContent: 'center', pb: 4 }}>
                    <Button
                        variant="contained"
                        onClick={() => setGameState(null)}
                        size="large"
                        sx={{
                            bgcolor: '#ef5350',
                            color: 'white',
                            px: 6,
                            fontWeight: 'bold',
                            '&:hover': { bgcolor: '#d32f2f' }
                        }}
                    >
                        Play Again
                    </Button>
                </DialogActions>
            </Dialog>
        </Container>
    );
};

export default GameDashboard;
