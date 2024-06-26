// App.js

import React, { useState, useEffect } from 'react';
import Login from './Login';
import BacktestForm from './BacktestForm';
import BacktestResultsTable from './BacktestResultsTable';

function App() {
  const [token, setToken] = useState('');
  const [currentView, setCurrentView] = useState('form'); // New state to track the current view

  // Function to check if user is authenticated
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
    }
  }, []);

  // Function to handle logout
  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken('');
  };

  return (
    <div className="min-h-screen flex flex-col">
      {token ? (
        <>
          <nav className="bg-gray-800 p-4">
            <div className="container mx-auto flex justify-between items-center">
              <h1 className="text-white text-xl">Backtest Application</h1>
              <div>
                <button
                  onClick={() => setCurrentView('form')}
                  className={`${
                    currentView === 'form' ? 'bg-blue-700' : 'bg-blue-600'
                  } hover:bg-blue-700 text-white py-2 px-4 rounded-md mr-2`}
                >
                  Backtest Form
                </button>
                <button
                  onClick={() => setCurrentView('results')}
                  className={`${
                    currentView === 'results' ? 'bg-blue-700' : 'bg-blue-600'
                  } hover:bg-blue-700 text-white py-2 px-4 rounded-md mr-2`}
                >
                  Results Table
                </button>
                <button
                  onClick={handleLogout}
                  className="bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-md"
                >
                  Logout
                </button>
              </div>
            </div>
          </nav>
          <div className="container mx-auto mt-4">
            {currentView === 'form' ? (
              <BacktestForm token={token} />
            ) : (
              <BacktestResultsTable token={token} />
            )}
          </div>
        </>
      ) : (
        <Login setToken={setToken} />
      )}
    </div>
  );
}

export default App;
