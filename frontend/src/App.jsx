import React from 'react';
import { ThemeProvider, CssBaseline, Box } from '@mui/material';
import theme from './theme';
import GameDashboard from './pages/GameDashboard';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{
        minHeight: '100vh',
        bgcolor: 'background.default',
        py: 4
      }}>
        <GameDashboard />
      </Box>
    </ThemeProvider>
  );
}

export default App;
