import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './PastResultsPage.css';

const PastResultsPage = () => {
  const [pastResults, setPastResults] = useState([]);

  useEffect(() => {
    const fetchPastResults = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/api/past-results');
        setPastResults(response.data);
      } catch (error) {
        console.error('Error fetching past results:', error);
      }
    };

    fetchPastResults();
  }, []);

  return (
    <div className="search-page">
      <header className="search-header">
      <h1>Past Results</h1>
        <div className="search-nav">
          <Link to="/search">Search</Link>
          <Link to="/past-results">Past Results</Link>
          <Link to="/">Sign Out</Link>
        </div>
      </header>
      <main>
        <div className="results-grid">
          {pastResults.map((result, index) => (
            <Link key={index} to={`/result/${result[0]}`}>
              <div className="result-item">
                <img src={`http://127.0.0.1:5000/images/${result[1]}`} alt="Completed scan" />
                <p className="scan-time">Scan Time: {result[14]}</p>
              </div>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
};

export default PastResultsPage;
