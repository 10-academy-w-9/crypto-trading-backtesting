// src/App.js

import React from 'react';
import './App.css';
import Login from './Login';
import BacktestForm from './BacktestForm';

function App() {
  return (
    <div className="App">
      {/* <header className="App-header">
        <h1>Welcome to Backtest App</h1>
      </header> */}
      <main>
        <BacktestForm />
      </main>
    </div>
  );
}

export default App;
