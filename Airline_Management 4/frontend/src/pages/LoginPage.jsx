import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';
import LoadingSpinner from '../components/LoadingSpinner';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e?.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.post('/auth/login', { email, password });
      if (response.data.success) {
        const { user, access_token } = response.data.data;
        login(user, access_token);
        
        // Redirect based on role
        if (user.role_id === 1 || user?.role?.name === 'admin') {
          navigate('/admin');
        } else {
          navigate('/flights');
        }
      }
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const quickLogin = (eTemplate, pTemplate) => {
    setEmail(eTemplate);
    setPassword(pTemplate);
  };

  return (
    <div className="auth-container animate-fade-in">
      <div className="glass-card auth-card flex-col">
        <div className="text-center mb-8">
          <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>✈️</div>
          <h2 className="text-2xl font-bold text-white">Welcome Back</h2>
          <p style={{ color: '#94a3b8', marginTop: '0.5rem' }}>Sign in to continue your journey</p>
        </div>

        {error && <div className="error-banner">{error}</div>}

        <form onSubmit={handleLogin} className="flex-col gap-4">
          <div style={{ position: 'relative' }}>
            <i className="fas fa-envelope" style={{ position: 'absolute', top: '16px', left: '16px', color: '#64748b' }}></i>
            <input 
              type="email" 
              className="input-field" 
              placeholder="Email Address" 
              style={{ paddingLeft: '40px' }} 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required 
            />
          </div>

          <div style={{ position: 'relative' }}>
            <i className="fas fa-lock" style={{ position: 'absolute', top: '16px', left: '16px', color: '#64748b' }}></i>
            <input 
              type={showPassword ? "text" : "password"} 
              className="input-field" 
              placeholder="Password" 
              style={{ paddingLeft: '40px', paddingRight: '40px' }} 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
            />
            <button 
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              style={{ position: 'absolute', top: '12px', right: '12px', background: 'none', border: 'none', color: '#64748b', cursor: 'pointer', padding: '4px' }}
            >
              <i className={showPassword ? "fas fa-eye-slash" : "fas fa-eye"}></i>
            </button>
          </div>

          <button type="submit" className="btn-primary" style={{ marginTop: '1rem' }} disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="text-center mt-6">
          <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>
            Don't have an account? <Link to="/register" style={{ color: '#3b82f6', fontWeight: 600 }}>Register here</Link>
          </p>
        </div>

        <div style={{ marginTop: '2.5rem', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '1.5rem' }}>
          <p style={{ color: '#64748b', fontSize: '0.75rem', textAlign: 'center', marginBottom: '1rem', textTransform: 'uppercase', letterSpacing: '1px' }}>Quick Login For Testing</p>
          <div className="flex gap-4 justify-center">
            <button onClick={() => quickLogin('passenger@airline.com', 'Pass@123')} style={{ background: 'rgba(59, 130, 246, 0.1)', border: '1px solid #3b82f6', color: '#3b82f6', padding: '6px 12px', borderRadius: '50px', fontSize: '0.75rem', cursor: 'pointer' }}>
              Passenger Login
            </button>
            <button onClick={() => quickLogin('admin@airline.com', 'Admin@123')} style={{ background: 'rgba(139, 92, 246, 0.1)', border: '1px solid #8b5cf6', color: '#8b5cf6', padding: '6px 12px', borderRadius: '50px', fontSize: '0.75rem', cursor: 'pointer' }}>
              Admin Login
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
