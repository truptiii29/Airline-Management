import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, isAuthenticated, isAdmin, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  let storedUser = 'Guest';
  try {
    const userData = localStorage.getItem('user');
    if (userData) {
      const userJSON = JSON.parse(userData);
      
      // Fallback handlers including dynamic admin parsing to preserve earlier state assumptions gracefully
      let extractedName = userJSON.name?.split(' ')[0] || userJSON.name || userJSON.first_name || userJSON.email?.split('@')[0];
      
      if (userJSON.role_id === 1 || userJSON?.role?.name === 'admin' || userJSON.role === 'admin') {
        extractedName = 'admin';
      }
      
      if (extractedName) storedUser = extractedName;
    }
  } catch (e) {
    // Failsafe in case the user data was a raw string
    const stringData = localStorage.getItem('user');
    if (stringData) storedUser = stringData;
  }

  const navLinks = () => {
    if (!isAuthenticated) {
      return (
        <>
          <span id="username" className="text-white font-semibold mr-4">Hello, {storedUser}</span>
          <Link to="/login" className="nav-link">Login</Link>
          <Link to="/register" className="btn-primary" style={{ padding: '8px 16px' }}>Register</Link>
        </>
      );
    }

    if (isAdmin) {
      return (
        <>
          <span id="username" className="text-white font-semibold mr-4">Hello, {storedUser}</span>
          <Link to="/admin" className="nav-link">Dashboard</Link>
          <Link to="/flights" className="nav-link">Flights</Link>
          <button onClick={handleLogout} className="btn-secondary" style={{ padding: '8px 16px' }}>Logout</button>
        </>
      );
    }

    return (
      <>
        <span id="username" className="text-white font-semibold mr-4">Hello, {storedUser}</span>
        <Link to="/flights" className="nav-link">Flights</Link>
        <Link to="/my-bookings" className="nav-link">My Bookings</Link>
        <button onClick={handleLogout} className="btn-secondary" style={{ padding: '8px 16px' }}>Logout</button>
      </>
    );
  };

  return (
    <nav className="sticky top-0 z-1000 w-full" style={{ position: 'sticky', top: 0, zIndex: 1000, background: 'rgba(10, 15, 30, 0.8)', backdropFilter: 'blur(12px)', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
      <div className="flex justify-between items-center px-8 py-4 max-w-7xl mx-auto" style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem 2rem' }}>
        <Link to="/" className="flex items-center gap-2" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', textDecoration: 'none' }}>
          <span style={{ fontSize: '1.5rem' }}>✈️</span>
          <span className="gradient-text font-bold text-xl" style={{ fontSize: '1.25rem', fontWeight: 700 }}>Modern Airways</span>
        </Link>

        {/* Desktop Nav */}
        <div className="hidden md:flex items-center gap-6" style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }} id="desktop-nav">
          {navLinks()}
        </div>

        {/* Mobile Toggle */}
        <div className="md:hidden" style={{ display: 'none' }} id="mobile-toggle">
          <button onClick={() => setMobileOpen(!mobileOpen)} style={{ background: 'transparent', border: 'none', color: 'white', fontSize: '1.5rem', cursor: 'pointer' }}>
            <i className={mobileOpen ? "fas fa-times" : "fas fa-bars"}></i>
          </button>
        </div>
      </div>

      {/* Mobile Nav */}
      {mobileOpen && (
        <div className="flex-col px-8 py-4 gap-4" style={{ display: 'flex', flexDirection: 'column', padding: '1rem 2rem', gap: '1rem', background: '#0d1526' }}>
          {navLinks()}
        </div>
      )}

      <style>
        {`
          .nav-link {
            color: #94a3b8;
            font-weight: 500;
            transition: color 0.3s ease;
            position: relative;
          }
          .nav-link:hover {
            color: #ffffff;
          }
          .nav-link::after {
            content: '';
            position: absolute;
            width: 0;
            height: 2px;
            bottom: -4px;
            left: 0;
            background: #3b82f6;
            transition: width 0.3s ease;
          }
          .nav-link:hover::after {
            width: 100%;
          }
          @media (max-width: 768px) {
            #desktop-nav { display: none !important; }
            #mobile-toggle { display: block !important; }
          }
        `}
      </style>
    </nav>
  );
};

export default Navbar;
