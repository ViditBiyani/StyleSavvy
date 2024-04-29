import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Signup() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate(); 

    const handleSignup = async () => {
        try {
            const response = await axios.post('http://127.0.0.1:5000/signup', { username, password });
            alert(response.data.message);
            navigate('/Login');
        } catch (error) {
            alert(error.response.data.message);
        }
    };
    const handleLogin = () => {
        navigate('/Login');
    };
    
    return (
        <div className="auth-container">
            <div className="auth-form">
                <h2>Signup</h2>
                <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" />
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
                <button onClick={handleSignup}>Signup</button>
                <button onClick={handleLogin}>Back to Login</button>
            </div>
        </div>
    );
}


export default Signup;
