import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import BookingCard from '../components/BookingCard';
import LoadingSpinner from '../components/LoadingSpinner';

const MyBookingsPage = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('all'); // all, upcoming, completed, cancelled

  useEffect(() => {
    fetchBookings();
  }, []);

  const fetchBookings = async () => {
    setLoading(true);
    try {
      const response = await api.get('/bookings/');
      setBookings(response.data.data || []);
    } catch (err) {
      setError('Failed to fetch your bookings. Please try again later.');
    } finally {
      setLoading(false);
    }
  };



  const filteredBookings = bookings.filter(b => {
    if (activeTab === 'all') return true;
    if (activeTab === 'cancelled') return b.status === 'cancelled';
    
    const flightDate = new Date(b.flight?.departure_time);
    const now = new Date();
    
    if (activeTab === 'upcoming') {
      return flightDate >= now && b.status !== 'cancelled';
    }
    if (activeTab === 'completed') {
      return flightDate < now && b.status !== 'cancelled';
    }
    return true;
  });

  return (
    <div className="animate-fade-in" style={{ padding: '3rem 1rem', maxWidth: '1000px', margin: '0 auto', minHeight: 'calc(100vh - 140px)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
        <div style={{ width: '50px', height: '50px', borderRadius: '12px', background: 'rgba(59, 130, 246, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <i className="fas fa-plane" style={{ fontSize: '1.5rem', color: '#3b82f6' }}></i>
        </div>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 800, color: 'white', margin: 0 }}>My Journeys</h1>
      </div>

      <div className="glass-card" style={{ padding: '1rem', marginBottom: '2rem', display: 'flex', gap: '0.5rem', overflowX: 'auto' }}>
        {['all', 'upcoming', 'completed', 'cancelled'].map(tab => (
          <button 
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {error ? (
        <div className="error-banner">{error}</div>
      ) : loading ? (
        <LoadingSpinner />
      ) : filteredBookings.length > 0 ? (
        <div className="animate-slide-in">
          {filteredBookings.map(booking => (
            <BookingCard 
              key={booking.booking_id || booking.id} 
              booking={booking} 
              onRefresh={fetchBookings} 
            />
          ))}
        </div>
      ) : (
        <div className="glass-card flex-col items-center justify-center text-center" style={{ padding: '4rem 2rem' }}>
          <img src="https://cdni.iconscout.com/illustration/premium/thumb/empty-state-2130362-1800926.png" alt="Empty" style={{ width: '200px', opacity: 0.5, marginBottom: '2rem', filter: 'grayscale(1) invert(0.8)' }} />
          <h3 style={{ color: 'white', fontSize: '1.5rem', marginBottom: '0.5rem' }}>No Bookings Found</h3>
          <p style={{ color: '#94a3b8' }}>
            {activeTab === 'all' 
              ? "You haven't booked any flights yet. Let's start your journey!" 
              : `You have no ${activeTab} bookings.`}
          </p>
        </div>
      )}

      <style>
        {`
          .tab-btn {
            background: transparent;
            border: none;
            color: #94a3b8;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            white-space: nowrap;
          }
          .tab-btn:hover {
            color: white;
            background: rgba(255,255,255,0.05);
          }
          .tab-btn.active {
            background: #3b82f6;
            color: white;
          }
        `}
      </style>
    </div>
  );
};

export default MyBookingsPage;
