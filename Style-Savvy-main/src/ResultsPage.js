import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import './ResultsPage.css';
import { Link } from 'react-router-dom';

const ResultsPage = () => {
  const [itemDetails, setItemDetails] = useState(null);
  const [ratedItems, setRatedItems] = useState(new Set());
  const { id } = useParams();

  useEffect(() => {
    const fetchItemDetailsAndRatings = async () => {
      try {
        const detailsResponse = await axios.get(`http://127.0.0.1:5000/api/details/${id}`);
        setItemDetails(detailsResponse.data);
        
        const ratingsResponse = await axios.get(`http://127.0.0.1:5000/api/user-ratings`);
        setRatedItems(new Set(ratingsResponse.data)); 
      } catch (error) {
        console.error('Failed to fetch item details or ratings:', error);
      }
    };

    fetchItemDetailsAndRatings();
  }, [id]);

  const handleRating = async (itemUrl, rating) => {
    try {
      const response = await axios.post(`http://127.0.0.1:5000/api/rate`, {
        itemUrl,
        rating
      });
      if (response.status === 200) {
        setRatedItems(prev => new Set(prev.add(itemUrl)));
      }
    } catch (error) {
      console.error('Failed to post rating:', error);
    }
  };

  if (!itemDetails) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="results-page-container">
      <header className="search-header">
        <h1>StyleSavvy</h1>
        <div className="search-nav">
          <Link to="/search">Search</Link>
          <Link to="/past-results">Past Results</Link>
          <Link to="/">Sign Out</Link>
        </div>
      </header>
      <div className="left-section">
        <h2>You Uploaded:</h2>
        <img src={`http://127.0.0.1:5000/images/${itemDetails.filename}`} alt="Uploaded Item" className="uploaded-item-image" />
      </div>
      <div className="right-section">
        <h2>We Detected:</h2>
        <div className="detected-items">
          <p>Detected Items: {itemDetails.inpic}</p>
        </div>
        <h3>We Recommend:</h3>
        <div className="recommendations-container">
          {itemDetails.items.map((item, index) => (
            <div key={index} className="recommendation-item">
              <a href={item.url} target="_blank" rel="noopener noreferrer">
                <img src={item.image} alt={item.name} style={{ width: "100px" }} />
                {item.name}
              </a>
              {!ratedItems.has(item.url) && (
                <div className="rating-buttons">
                  <button onClick={() => handleRating(item.url, 'like')} className="thumb-up">👍</button>
                  <button onClick={() => handleRating(item.url, 'dislike')} className="thumb-down">👎</button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;
