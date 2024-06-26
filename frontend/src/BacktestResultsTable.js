import React, { useState, useEffect } from 'react';
import axios from 'axios';
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
    <div className="max-w-4xl mx-auto mt-10 p-6 bg-white shadow-md rounded-md">
      <h2 className="text-xl font-semibold mb-4">Backtest Results</h2>
      <table className="min-w-full bg-white">
        <thead>
          <tr>
            <th className="py-2 px-4 border-b border-gray-200">Name</th>
            <th className="py-2 px-4 border-b border-gray-200">Symbol</th>
            <th className="py-2 px-4 border-b border-gray-200">Start Date</th>
            <th className="py-2 px-4 border-b border-gray-200">End Date</th>
            <th className="py-2 px-4 border-b border-gray-200">Initial Cash</th>
            <th className="py-2 px-4 border-b border-gray-200">Fee</th>
          </tr>
        </thead>
        <tbody>
          {backtests.map((backtest) => (
            <tr key={backtest.id} onClick={() => handleRowClick(backtest)} className="cursor-pointer">
              <td className="py-2 px-4 border-b border-gray-200">{backtest.name}</td>
              <td className="py-2 px-4 border-b border-gray-200">{backtest.symbol}</td>
              <td className="py-2 px-4 border-b border-gray-200">{backtest.start_date}</td>
              <td className="py-2 px-4 border-b border-gray-200">{backtest.end_date}</td>
              <td className="py-2 px-4 border-b border-gray-200">{backtest.inital_cash}</td>
              <td className="py-2 px-4 border-b border-gray-200">{backtest.fee}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {selectedBacktest && (
        <BacktestResultModal backtest={selectedBacktest} onClose={handleCloseModal} token={token} />
      )}
    </div>
  );
};

export default BacktestResultsTable;
