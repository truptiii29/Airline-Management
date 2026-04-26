import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <footer style={{ background: '#080c17', padding: '4rem 2rem 2rem', marginTop: 'auto', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', flexWrap: 'wrap', gap: '3rem', justifyContent: 'space-between' }}>
        
        <div style={{ flex: '1', minWidth: '250px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <span style={{ fontSize: '1.5rem' }}>✈️</span>
            <span className="gradient-text font-bold text-xl">Modern Airways</span>
          </div>
          <p style={{ color: '#64748b', lineHeight: '1.6' }}>
            The world is yours to explore — one flight at a time. Premium airline service connecting you to the best destinations.
          </p>
        </div>

        <div style={{ flex: '1', minWidth: '200px' }}>
          <h3 style={{ color: 'white', marginBottom: '1.5rem', fontSize: '1.1rem', fontWeight: 600 }}>Quick Links</h3>
          <ul style={{ listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <li><Link to="/" style={{ color: '#94a3b8', transition: 'color 0.3s' }} className="footer-link">Home</Link></li>
            <li><Link to="/flights" style={{ color: '#94a3b8', transition: 'color 0.3s' }} className="footer-link">Search Flights</Link></li>
            <li><Link to="/my-bookings" style={{ color: '#94a3b8', transition: 'color 0.3s' }} className="footer-link">My Bookings</Link></li>
            <li><Link to="/login" style={{ color: '#94a3b8', transition: 'color 0.3s' }} className="footer-link">Passenger Login</Link></li>
          </ul>
        </div>

        <div style={{ flex: '1', minWidth: '200px' }}>
          <h3 style={{ color: 'white', marginBottom: '1.5rem', fontSize: '1.1rem', fontWeight: 600 }}>Contact Us</h3>
          <ul style={{ listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '1rem', color: '#94a3b8' }}>
            <li style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <i className="fas fa-envelope" style={{ color: '#3b82f6' }}></i> support@modernairways.com
            </li>
            <li style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <i className="fas fa-phone-alt" style={{ color: '#3b82f6' }}></i> +91 1800 123 4567
            </li>
            <li style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <i className="fas fa-map-marker-alt" style={{ color: '#3b82f6' }}></i> Delhi, India
            </li>
          </ul>
        </div>

      </div>

      <div style={{ maxWidth: '1200px', margin: '3rem auto 0', paddingTop: '1.5rem', borderTop: '1px solid rgba(255,255,255,0.05)', textAlign: 'center', color: '#64748b', fontSize: '0.875rem' }}>
        <p>&copy; {new Date().getFullYear()} Modern Airways. All rights reserved.</p>
      </div>

      <style>
        {`
          .footer-link:hover {
            color: #3b82f6 !important;
          }
        `}
      </style>
    </footer>
  );
};

export default Footer;
