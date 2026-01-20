import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '/api';

const client = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const gameApi = {
    setup: (numPlayers, aiStrategy) => client.post('/game/setup', { num_players: numPlayers, ai_strategy: aiStrategy }),
    getState: () => client.get('/game/state'),
    roll: () => client.post('/game/roll'),
    mark: (playerId, color, number) => client.post('/game/mark', { player_id: playerId, color, number }),
    done: (playerId) => client.post('/game/done', { player_id: playerId }),
};

export default client;
