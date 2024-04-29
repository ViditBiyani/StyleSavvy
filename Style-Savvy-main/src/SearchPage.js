import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './SearchPage.css';
import { useNavigate } from 'react-router-dom';

const SearchPage = () => {
  const [file, setFile] = useState(null);
  const [fileData, setFileData] = useState(null);
  const [inspiration, setInspiration] = useState('');
  const [gender, setGender] = useState('female'); 
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();


  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setFile(file);
      setFileData(URL.createObjectURL(file));
    }
  };

  const handleSearch = async () => {
    if (file) {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('inspiration', inspiration);
      formData.append('gender', gender);
  
      setLoading(true);
  
      try {
        const response = await axios.post('http://127.0.0.1:5000/api/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        console.log('File uploaded successfully:', response.data);
        setLoading(false);
        navigate(`/result/${response.data.id}`);
      } catch (error) {
        console.error('Error uploading file:', error);
        setLoading(false);
      }
    }
  };
  return (
    <div className="search-page">
      <header className="search-header">
        <h1>StyleSavvy</h1>
        <div className="search-nav">
          <Link to="/search">Search</Link>
          <Link to="/past-results">Past Results</Link>
          <Link to="/">Sign Out</Link>
        </div>
      </header>
      <main className="search-main">
        <div className="file-upload-container">
          {fileData && <img src={fileData} alt="Preview" className="preview-image" />}
          <input type="file" id="file-upload" accept="image/*" onChange={handleFileChange} />
          <label htmlFor="file-upload" className="upload-button">
            <i className="fas fa-cloud-upload-alt"></i> Browse File
          </label>
          <p>Choose a file</p>
          <input type="text" placeholder="Enter inspiration" value={inspiration} onChange={(e) => setInspiration(e.target.value)} />
          <select value={gender} onChange={(e) => setGender(e.target.value)}>
            <option value="female">Female</option>
            <option value="male">Male</option>
          </select>
          <button onClick={handleSearch} disabled={loading}>{loading ? 'Loading...' : 'Search'}</button>
          {loading && <div className="loading-spinner"></div>}
        </div>
      </main>
    </div>
  );
};

export default SearchPage;
