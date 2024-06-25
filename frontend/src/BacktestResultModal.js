import React, { useState, useEffect } from 'react';
import axios from 'axios';

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
    <div className="fixed inset-0 z-50 overflow-auto bg-smoke-light flex">
      <div className="relative p-8 bg-white w-full max-w-md m-auto flex-col flex rounded-lg shadow-lg">
        <h3 className="text-xl font-semibold mb-4">{backtest.name} Details</h3>
        <button
          onClick={onClose}
          className="absolute top-0 right-0 p-2 text-gray-500 hover:text-gray-700"
        >
          &times;
        </button>
        <table className="min-w-full bg-white">
          <thead>
            <tr>
              <th className="py-2 px-4 border-b border-gray-200">Total Return</th>
              <th className="py-2 px-4 border-b border-gray-200">Number of Trades</th>
              <th className="py-2 px-4 border-b border-gray-200">Winning Trades</th>
              <th className="py-2 px-4 border-b border-gray-200">Losing Trades</th>
              <th className="py-2 px-4 border-b border-gray-200">Max Drawdown</th>
              <th className="py-2 px-4 border-b border-gray-200">Sharpe Ratio</th>
            </tr>
          </thead>
          <tbody>
            {results.map((result) => (
              <tr key={result.id}>
                <td className="py-2 px-4 border-b border-gray-200">{result.total_return}</td>
                <td className="py-2 px-4 border-b border-gray-200">{result.number_of_trades}</td>
                <td className="py-2 px-4 border-b border-gray-200">{result.winning_trades}</td>
                <td className="py-2 px-4 border-b border-gray-200">{result.losing_trades}</td>
                <td className="py-2 px-4 border-b border-gray-200">{result.max_drawdown}</td>
                <td className="py-2 px-4 border-b border-gray-200">{result.sharpe_ratio}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default BacktestResultModal;
