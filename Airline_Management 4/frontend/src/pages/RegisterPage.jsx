import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api/axios';

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    passport_number: '',
    phone: '',
    date_of_birth: '',
    nationality: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [otp, setOtp] = useState('');
  const [userId, setUserId] = useState(null);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.post('/auth/register', formData);
      if (response.data.success) {
        setSuccess(true);
        setUserId(response.data.data?.user_id || response.data.data?.id);
        
        // If backend passed us the OTP transparently (dev mode), pre-fill it!
        if (response.data.data?.otp_code) {
           setOtp(response.data.data.otp_code);
        }
      }
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const verifyOtp = async (e) => {
    e.preventDefault();
    try {
      await api.post('/auth/verify-otp', { 
        user_id: userId, 
        otp_code: otp 
      });
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Invalid OTP.');
    }
  };

  if (success) {
    return (
      <div className="auth-container animate-fade-in">
        <div className="glass-card auth-card flex-col text-center">
          <div style={{ fontSize: '3rem', color: '#10b981', marginBottom: '1rem' }}><i className="fas fa-check-circle"></i></div>
          <h2 className="text-2xl font-bold text-white mb-4">Account Created!</h2>
          <p style={{ color: '#94a3b8', marginBottom: '1.5rem' }}>Please check your email for OTP verification.</p>
          
          <form onSubmit={verifyOtp} className="flex-col gap-4 mb-6">
            <input 
              type="text" 
              className="input-field" 
              placeholder="Enter OTP" 
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              style={{ textAlign: 'center', letterSpacing: '0.25em', fontSize: '1.25rem' }} 
            />
            <button type="submit" className="btn-primary w-full">Verify</button>
          </form>

          <p style={{ color: '#f59e0b', fontSize: '0.875rem', background: 'rgba(245, 158, 11, 0.1)', padding: '10px', borderRadius: '8px' }}>
            Development mode: OTP verification may be skipped. Contact admin for access.
            Redirecting to login in 3 seconds...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-container animate-fade-in py-12" style={{ padding: '3rem 1rem' }}>
      <div className="glass-card auth-card flex-col" style={{ maxWidth: '800px' }}>
        <div className="text-center mb-8">
          <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>✈️</div>
          <h2 className="text-2xl font-bold text-white">Create Account</h2>
          <p style={{ color: '#94a3b8', marginTop: '0.5rem' }}>Start your journey with Modern Airways</p>
        </div>

        {error && <div className="error-banner">{error}</div>}

        <form onSubmit={handleRegister} className="grid-form">
          <div>
            <label>First Name</label>
            <input name="first_name" type="text" className="input-field" required value={formData.first_name} onChange={handleChange} />
          </div>
          <div>
            <label>Last Name</label>
            <input name="last_name" type="text" className="input-field" required value={formData.last_name} onChange={handleChange} />
          </div>
          <div>
            <label>Email Address</label>
            <input name="email" type="email" className="input-field" required value={formData.email} onChange={handleChange} />
          </div>
          <div style={{ position: 'relative' }}>
            <label>Password</label>
            <input name="password" type={showPassword ? "text" : "password"} className="input-field" style={{ paddingRight: '40px' }} required value={formData.password} onChange={handleChange} />
            <button type="button" onClick={() => setShowPassword(!showPassword)} style={{ position: 'absolute', top: '38px', right: '12px', background: 'none', border: 'none', color: '#64748b', cursor: 'pointer' }}>
              <i className={showPassword ? "fas fa-eye-slash" : "fas fa-eye"}></i>
            </button>
          </div>
          <div>
            <label>Passport Number</label>
            <input name="passport_number" type="text" className="input-field" required value={formData.passport_number} onChange={handleChange} />
          </div>
          <div>
            <label>Phone Number</label>
            <input name="phone" type="text" className="input-field" required value={formData.phone} onChange={handleChange} />
          </div>
          <div>
            <label>Date of Birth</label>
            <input name="date_of_birth" type="date" className="input-field" required value={formData.date_of_birth} onChange={handleChange} />
          </div>
          <div>
            <label>Nationality</label>
            <input name="nationality" type="text" className="input-field" required value={formData.nationality} onChange={handleChange} />
          </div>

          <div style={{ gridColumn: '1 / -1', marginTop: '1rem' }}>
            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? 'Creating Account...' : 'Register'}
            </button>
          </div>
        </form>

        <div className="text-center mt-6">
          <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>
            Already have an account? <Link to="/login" style={{ color: '#3b82f6', fontWeight: 600 }}>Login</Link>
          </p>
        </div>
      </div>

      <style>
        {`
          .grid-form {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
          }
          .grid-form label {
            display: block;
            color: #cbd5e1;
            font-size: 0.875rem;
            margin-bottom: 0.5rem;
          }
          @media (max-width: 640px) {
            .grid-form {
              grid-template-columns: 1fr;
            }
          }
          input[type="date"]::-webkit-calendar-picker-indicator {
            filter: invert(1);
            opacity: 0.5;
            cursor: pointer;
          }
        `}
      </style>
    </div>
  );
};

export default RegisterPage;
