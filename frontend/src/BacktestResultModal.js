import React, { useState, useEffect } from 'react';
import { FaCheckCircle, FaTimesCircle } from 'react-icons/fa';
import axios from 'axios';
import { Modal, Box, Typography, IconButton, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';

const API_BASE_URL = 'http://localhost:5000';

const BacktestResultModal = ({ backtest, onClose, token }) => {
  const [results, setResults] = useState([]);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/backtests/${backtest.id}/results`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setResults(response.data.results);
      } catch (error) {
        console.error('Error fetching results:', error);
      }
    };

    fetchResults();
  }, [backtest.id, token]);

  return (
    <Modal open={true} onClose={onClose}>
      <Box
        sx={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: '80%',
          bgcolor: 'background.paper',
          border: '2px solid #000',
          boxShadow: 24,
          p: 4,
          borderRadius: 2,
        }}
      >
        <Typography variant="h5" component="h2" gutterBottom>
          {backtest.name} Details
          <IconButton
            aria-label="close"
            onClick={onClose}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8,
              color: (theme) => theme.palette.grey[500],
            }}
          >
            <CloseIcon />
          </IconButton>
        </Typography>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><b>Strategy</b></TableCell>
                <TableCell>Total Return</TableCell>
                <TableCell>Number of Trades</TableCell>
                <TableCell>Winning Trades</TableCell>
                <TableCell>Losing Trades</TableCell>
                <TableCell>Max Drawdown</TableCell>
                <TableCell>Sharpe Ratio</TableCell>
                <TableCell><b>Is Best</b></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {results.map((result) => (
                <TableRow key={result.id}>
                  <TableCell><b>{result.strategy}</b></TableCell>
                  <TableCell>{result.total_return}</TableCell>
                  <TableCell>{result.number_of_trades}</TableCell>
                  <TableCell>{result.winning_trades}</TableCell>
                  <TableCell>{result.losing_trades}</TableCell>
                  <TableCell>{result.max_drawdown}</TableCell>
                  <TableCell>{result.sharpe_ratio}</TableCell>
                  <TableCell>
                    {result.is_best ? (
                      <Box display="flex" alignItems="center" color="success.main">
                        <FaCheckCircle />
                        <Typography ml={1}>Best</Typography>
                      </Box>
                    ) : (
                      <Box display="flex" alignItems="center" color="error.main">
                        <FaTimesCircle />
                        <Typography ml={1}>Not the Best</Typography>
                      </Box>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Modal>
  );
};

export default BacktestResultModal;
