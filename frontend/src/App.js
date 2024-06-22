// App.js

import React, { useState, useEffect } from 'react';
import Login from './Login';
import BacktestForm from './BacktestForm';

function App() {
  const [token, setToken] = useState('');

  // Function to check if user is authenticated
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
    }
  }, [token]);

  // Function to handle logout (optional)
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
              <button
                onClick={handleLogout}
                className="bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-md"
              >
                Logout
              </button>
            </div>
          </nav>
          <div className="container mx-auto mt-4">
            <BacktestForm token={token} />
          </div>
        </>
      ) : (
        <Login setToken={setToken} />
      )}
    </div>
  );
}

export default App;
