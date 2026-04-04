import React, { useState, useEffect } from 'react';
import { Paper, Typography, Button, Box, Alert, CircularProgress } from '@mui/material';
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
            if (response.data.error) {
                setGameState(null);
            } else {
                setGameState(response.data);
            }
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

    const handleMark = async (playerId, color, number) => {
        try {
            const response = await gameApi.mark(playerId, color, number);
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
        <Box sx={{ maxWidth: 600, mx: 'auto', p: 3 }}>
            <Paper sx={{ p: 4, textAlign: 'center' }}>
                <Typography variant="h4" gutterBottom>Qwixx</Typography>
                <Button variant="contained" color="primary" onClick={handleSetup} size="large">
                    Start New Game
                </Button>
            </Paper>
        </Box>
    );

    const isGameOver = gameState.state === 'GAME_OVER';

    // Build a set of valid moves for quick lookup: "playerId:color:number"
    const validMoveSet = new Set(
        (gameState.valid_moves || []).map(m => `${m.player_id}:${m.color}:${m.number}`)
    );

    return (
        <Box sx={{ p: 3, maxWidth: 1400, mx: 'auto' }}>
            {/* Header - full width, independent of grid */}
            <Paper sx={{ p: 2, mb: 3, bgcolor: 'background.paper', borderLeft: '6px solid', borderLeftColor: isGameOver ? 'warning.main' : 'primary.main' }}>
                <Typography variant="h6">{gameState.message}</Typography>
                {!isGameOver && (
                    <Typography variant="subtitle2" color="textSecondary">
                        State: {gameState.state} | Current Player: {gameState.players[gameState.current_player_index].name}
                    </Typography>
                )}
            </Paper>

            {isGameOver && (
                <Paper sx={{ p: 3, mb: 3, bgcolor: '#1a1a2e', border: '2px solid #e94560', textAlign: 'center' }}>
                    <Typography variant="h4" sx={{ color: '#e94560', mb: 2 }}>
                        Game Over
                    </Typography>
                    {[...gameState.players]
                        .sort((a, b) => b.scoresheet.total_score - a.scoresheet.total_score)
                        .map((player, idx) => (
                            <Box key={player.id} sx={{ mb: 1 }}>
                                <Typography variant="h6" sx={{ color: idx === 0 ? '#ffd700' : '#ccc' }}>
                                    {idx === 0 ? '** ' : ''}{player.name}: {player.scoresheet.total_score} points
                                    {idx === 0 ? ' **' : ''}
                                </Typography>
                                <Typography variant="body2" sx={{ color: '#999' }}>
                                    Penalties: {player.scoresheet.penalties}
                                </Typography>
                            </Box>
                        ))}
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={handleSetup}
                        sx={{ mt: 2 }}
                        size="large"
                    >
                        Play Again
                    </Button>
                </Paper>
            )}

            {error && (
                <Box sx={{ mb: 3 }}>
                    <Alert severity="error" onClose={() => setError(null)}>{error}</Alert>
                </Box>
            )}

            {/* Game boards + dice panel side by side */}
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 240px' }, gap: 3 }}>
                <Box sx={{ minWidth: 0 }}>
                    {gameState.players.map((player) => (
                        <ScoreSheet
                            key={player.id}
                            player={player}
                            onMark={handleMark}
                            isCurrentPlayer={gameState.players[gameState.current_player_index].id === player.id}
                            validMoveSet={validMoveSet}
                            lockedColors={gameState.locked_colors}
                            isGameOver={isGameOver}
                        />
                    ))}
                </Box>

                <Box>
                <Paper sx={{ p: 2, position: 'sticky', top: 20 }}>
                    <Typography variant="h6" gutterBottom>Dice</Typography>
                    <DiceDisplay results={gameState.dice_results} />
                    <Box mt={3} display="flex" flexDirection="column" gap={2}>
                        <Button
                            variant="contained"
                            fullWidth
                            onClick={handleRoll}
                            disabled={gameState.state !== 'WAITING_FOR_ROLL'}
                        >
                            Roll Dice
                        </Button>
                        <Button
                            variant="outlined"
                            fullWidth
                            onClick={handleDone}
                            disabled={!['STAGE_1_MOVES', 'STAGE_2_MOVES'].includes(gameState.state)}
                        >
                            Done
                        </Button>
                        <Button
                            variant="outlined"
                            color="error"
                            fullWidth
                            onClick={handleSetup}
                        >
                            New Game
                        </Button>
                    </Box>
                </Paper>
            </Box>
            </Box>
        </Box>
    );
};

export default GameDashboard;
