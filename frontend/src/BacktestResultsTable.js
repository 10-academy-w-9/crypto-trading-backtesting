import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Typography, Box } from '@mui/material';
import BacktestResultModal from './BacktestResultModal';

const API_BASE_URL = 'http://localhost:5000';

const BacktestResultsTable = ({ token }) => {
  const [backtests, setBacktests] = useState([]);
  const [selectedBacktest, setSelectedBacktest] = useState(null);

  useEffect(() => {
    const fetchBacktests = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/backtests`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setBacktests(response.data.backtests);
      } catch (error) {
        console.error('Error fetching backtests:', error);
      }
    };

    fetchBacktests();
  }, [token]);

  const handleRowClick = (backtest) => {
    setSelectedBacktest(backtest);
  };

  const handleCloseModal = () => {
    setSelectedBacktest(null);
  };

  return (
    <Box sx={{ maxWidth: '80%', mx: 'auto', mt: 10, p: 3, bgcolor: 'background.paper', boxShadow: 3, borderRadius: 2 }}>
      <Typography variant="h6" component="h2" gutterBottom>
        Backtest Results
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Symbol</TableCell>
              <TableCell>Start Date</TableCell>
              <TableCell>End Date</TableCell>
              <TableCell>Initial Cash</TableCell>
              <TableCell>Fee</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {backtests.map((backtest) => (
              <TableRow 
                key={backtest.id} 
                onClick={() => handleRowClick(backtest)} 
                sx={{ cursor: 'pointer', '&:hover': { backgroundColor: '#f5f5f5' } }}
              >
                <TableCell>{backtest.name}</TableCell>
                <TableCell>{backtest.symbol}</TableCell>
                <TableCell>{backtest.start_date}</TableCell>
                <TableCell>{backtest.end_date}</TableCell>
                <TableCell>{backtest.inital_cash}</TableCell>
                <TableCell>{backtest.fee}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      {selectedBacktest && (
        <BacktestResultModal backtest={selectedBacktest} onClose={handleCloseModal} token={token} />
      )}
    </Box>
  );
};

export default BacktestResultsTable;
