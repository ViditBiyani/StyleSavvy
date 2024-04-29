import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './Login.css';

function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleLogin = async () => {
        try {
            const response = await axios.post('http://127.0.0.1:5000/login', { username, password });
            alert(response.data.message);
            navigate('/search');
        } catch (error) {
            alert(error.response.data.message);
        }
    };

    const handleSignUp = () => {
        navigate('/signup');
    };

    return (
        <div className="auth-container">
            <div className="auth-form">
                <h2>Login</h2>
                <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" />
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
                <button onClick={handleLogin}>Login</button>
                <button onClick={handleSignUp}>Sign Up</button>
            </div>
        </div>
    );
}

export default Login;
