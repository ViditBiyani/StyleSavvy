// App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import SearchPage from './SearchPage';
import ResultsPage from './ResultsPage';
import PastResultsPage from './PastResultsPage';
import Signup from './Signup';
import Login from './Login';
import './App.css';

const App = () => {
  return (
    <Router>
      <nav>
        <ul>

        </ul>
      </nav>
      <Routes>
      <Route path="/" element={<Navigate replace to="/Login" />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/result/:id" element={<ResultsPage />} />
        <Route path="/past-results" element={<PastResultsPage />} />
        <Route path="/Signup" element={<Signup />} />
        <Route path="/Login" element={<Login />} />
      </Routes>
    </Router>
  );
};

export default App;
