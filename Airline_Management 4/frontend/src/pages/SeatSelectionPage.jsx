import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import io from 'socket.io-client';
import api from '../api/axios';
import SeatMap from '../components/SeatMap';
import LoadingSpinner from '../components/LoadingSpinner';

function SeatSelectionPage() {
  const { flightId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const flight = JSON.parse(localStorage.getItem("flight")) || {};
  console.log("FLIGHT:", flight);
  
  const seatClassFromSearch = sessionStorage.getItem('selectedClass') || 'economy';

  const [seatsData, setSeatsData] = useState(null);
  const [selectedSeat, setSelectedSeat] = useState(null);
  const [loading, setLoading] = useState(true);
  const [locking, setLocking] = useState(false);
  const [error, setError] = useState('');
  
  const [lockedSeat, setLockedSeat] = useState(null);
  const [timeLeft, setTimeLeft] = useState(0);
  
  // ✅ NEW: Socket.IO and seat counts
  const [socket, setSocket] = useState(null);
  const [seatCounts, setSeatCounts] = useState({ economy: 0, business: 0, first: 0 });
  const [notification, setNotification] = useState('');

  // ✅ CONNECT TO SOCKET.IO
  useEffect(() => {
    const newSocket = io('http://127.0.0.1:5003', {
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5
    });

    newSocket.on('connect', () => {
      console.log('✅ Connected to real-time seat updates');
      newSocket.emit('join_flight', { flight_id: parseInt(flightId) });
    });

    newSocket.on('seat_update', (data) => {
      console.log('🪑 Seat update received:', data);
      if (data.action === 'booked') {
        // Remove booked seat from available seats
        setSeatsData(prev => ({
          ...prev,
          [data.seat.seat_class]: prev[data.seat.seat_class].filter(
            s => s.seat_number !== data.seat.seat_number
          )
        }));
        
        // Show notification
        showNotification(`Seat ${data.seat.seat_number} just got booked!`, 'info');
      }
    });

    newSocket.on('seat_count_update', (data) => {
      console.log('📊 Seat count update:', data);
      setSeatCounts(data.seat_counts);
    });

    newSocket.on('disconnect', () => {
      console.log('❌ Disconnected from real-time updates');
    });

    setSocket(newSocket);

    return () => {
      if (newSocket) {
        newSocket.emit('leave_flight', { flight_id: parseInt(flightId) });
        newSocket.disconnect();
      }
    };
  }, [flightId]);

  useEffect(() => {
    const fetchSeats = async () => {
      try {
        const response = await api.get(`/seats/${flightId}/available`);
        const data = response.data.data;
        
        // Enrich seat objects with seat_class field based on their section
        const enrichedData = {
          economy: data.economy?.map(s => ({...s, seat_class: 'economy'})) || [],
          business: data.business?.map(s => ({...s, seat_class: 'business'})) || [],
          first: data.first?.map(s => ({...s, seat_class: 'first'})) || []
        };
        
        setSeatsData(enrichedData);
        
        // ✅ SET INITIAL SEAT COUNTS
        setSeatCounts({
          economy: enrichedData.economy.length,
          business: enrichedData.business.length,
          first: enrichedData.first.length
        });
      } catch (err) {
        setError('Failed to fetch seat map. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchSeats();
  }, [flightId]);

  useEffect(() => {
    let interval = null;
    if (timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft(prev => prev - 1);
      }, 1000);
    } else if (timeLeft === 0 && lockedSeat) {
      setLockedSeat(null);
      setError('Seat lock expired. Please select a seat again.');
    }
    return () => clearInterval(interval);
  }, [timeLeft, lockedSeat]);

  const showNotification = (message, type) => {
    setNotification(message);
    setTimeout(() => setNotification(''), 4000);
  };

  const handleLockSeat = async () => {
    if (!selectedSeat) return;
    setLocking(true);
    setError('');
    
    try {
      const response = await api.post('/seats/lock', {
        flight_id: parseInt(flightId),
        seat_number: selectedSeat.seat_number
      });
      
      if (response.data.success) {
         setLockedSeat(selectedSeat);
         setTimeLeft(1800); // 30 minutes
         sessionStorage.setItem('bookingDetails', JSON.stringify({
            flight,
            seat: selectedSeat,
            price: getSeatPrice(selectedSeat)
         }));
      }
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to lock seat. It may have been taken.');
    } finally {
      setLocking(false);
    }
  };

  const proceedToPayment = () => {
    navigate('/payment');
  };

  function handleSeatClick(seat) {
    if (lockedSeat) return;
    console.log("SEAT:", seat);
    setSelectedSeat(seat);
    
    let price = 0;
    if (seat.seat_class === "economy") {
      price = flight.base_price_economy;
    } else if (seat.seat_class === "business") {
      price = flight.base_price_business;
    } else if (seat.seat_class === "first") {
      price = flight.base_price_first;
    }
    
    const targetElement = document.getElementById("price");
    if (targetElement) {
       targetElement.innerText = "₹" + price;
    }
  }

  const getSeatPrice = (seat) => {
    if (!seat) return 0;
    
    let price = 0;
    if (seat.seat_class === "economy") {
       price = flight.base_price_economy;
    } else if (seat.seat_class === "business") {
       price = flight.base_price_business;
    } else if (seat.seat_class === "first") {
       price = flight.base_price_first;
    }
    
    return price;
  };

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  return (
    <div className="animate-fade-in" style={{ padding: '2rem 1rem', maxWidth: '1200px', margin: '0 auto' }}>
      
      {/* Flight Summary */}
      <div className="glass-card" style={{ padding: '1.5rem 2rem', marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>Flight {flight.flight_number}</p>
          <h2 style={{ fontSize: '1.5rem', color: 'white', margin: '0.25rem 0 0' }}>
            {flight.source_iata || flight.source?.iata || 'SRC'} <i className="fas fa-arrow-right" style={{ color: '#3b82f6', fontSize: '1rem', margin: '0 0.5rem' }}></i> {flight.destination_iata || flight.destination?.iata || 'DST'}
          </h2>
        </div>
        <div style={{ textAlign: 'right' }}>
          <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>Selected Class</p>
          <h3 style={{ color: 'white', textTransform: 'capitalize', margin: '0.25rem 0 0' }}>{seatClassFromSearch}</h3>
        </div>
      </div>

      {/* ✅ NEW: LIVE SEAT COUNTS */}
      <div className="glass-card" style={{ padding: '1rem 2rem', marginBottom: '2rem', display: 'flex', justifyContent: 'space-around' }}>
        <div style={{ textAlign: 'center' }}>
          <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>Economy Available</p>
          <h3 style={{ color: '#10b981', fontSize: '1.5rem', margin: '0.5rem 0 0' }}>{seatCounts.economy} seats</h3>
        </div>
        <div style={{ textAlign: 'center' }}>
          <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>Business Available</p>
          <h3 style={{ color: '#3b82f6', fontSize: '1.5rem', margin: '0.5rem 0 0' }}>{seatCounts.business} seats</h3>
        </div>
        <div style={{ textAlign: 'center' }}>
          <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>First Class Available</p>
          <h3 style={{ color: '#f59e0b', fontSize: '1.5rem', margin: '0.5rem 0 0' }}>{seatCounts.first} seats</h3>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {notification && (
        <div style={{ 
          background: 'rgba(59, 130, 246, 0.2)', 
          border: '1px solid #3b82f6',
          borderRadius: '8px',
          padding: '1rem',
          marginBottom: '1rem',
          color: '#3b82f6',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <i className="fas fa-info-circle"></i>
          {notification}
        </div>
      )}

      <div style={{ display: 'flex', gap: '2rem', alignItems: 'flex-start' }} className="seat-container">
        
        {/* Main Seat Map */}
        <div style={{ flex: '1' }}>
          {loading ? (
            <LoadingSpinner />
          ) : (
            <SeatMap 
              seatsData={seatsData} 
              selectedSeat={selectedSeat} 
              onSeatSelect={handleSeatClick} 
            />
          )}
        </div>

        {/* Sidebar Info */}
        <div className="glass-card sidebar-info" style={{ width: '320px', padding: '1.5rem', flexShrink: 0, position: 'sticky', top: '100px' }}>
          <h3 style={{ color: 'white', fontSize: '1.25rem', marginBottom: '1.5rem' }}>Seat Details</h3>
          
          {!selectedSeat ? (
            <div style={{ padding: '2rem 1rem', textAlign: 'center', background: 'rgba(255,255,255,0.02)', borderRadius: '12px', border: '1px dashed rgba(255,255,255,0.1)' }}>
              <i className="fas fa-chair" style={{ fontSize: '2rem', color: '#64748b', marginBottom: '1rem' }}></i>
              <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>Please select a seat from the cabin map.</p>
            </div>
          ) : (
            <div className="animate-fade-in">
              <div style={{ background: 'rgba(59, 130, 246, 0.1)', border: '1px solid #3b82f6', borderRadius: '12px', padding: '1.5rem', textAlign: 'center', marginBottom: '1.5rem' }}>
                <span style={{ fontSize: '2.5rem', fontWeight: 800, color: 'white' }}>{selectedSeat.seat_number}</span>
                <p style={{ color: '#94a3b8', textTransform: 'uppercase', marginTop: '0.5rem', fontWeight: 600, letterSpacing: '1px' }}>
                  {selectedSeat.seat_class} CLASS
                </p>
                
                <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid rgba(59, 130, 246, 0.3)' }}>
                  <span style={{ color: '#cbd5e1', fontSize: '0.875rem' }}>Total Price</span>
                  <h3 id="price" className="gradient-text" style={{ fontSize: '1.5rem', margin: '0.25rem 0 0' }}>
                    ₹{getSeatPrice(selectedSeat)}
                  </h3>
                </div>
              </div>

              {!lockedSeat ? (
                <button 
                  className="btn-primary w-full" 
                  onClick={handleLockSeat}
                  disabled={locking}
                  style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem' }}
                >
                  {locking ? <i className="fas fa-spinner fa-spin"></i> : <i className="fas fa-lock"></i>}
                  {locking ? 'Locking...' : 'Lock Seat'}
                </button>
              ) : (
                <div className="animate-fade-in text-center">
                  <div style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid #10b981', color: '#10b981', padding: '12px', borderRadius: '8px', marginBottom: '1rem', fontWeight: 600 }}>
                    <i className="fas fa-check-circle" style={{ marginRight: '0.5rem' }}></i> Seat Locked
                  </div>
                  <p style={{ color: '#f59e0b', fontSize: '0.875rem', marginBottom: '1rem' }}>
                    <i className="far fa-clock" style={{ marginRight: '0.5rem' }}></i> 
                    Reserved for {formatTime(timeLeft)}
                  </p>
                  <button className="btn-primary w-full" onClick={proceedToPayment} style={{ background: 'linear-gradient(to right, #10b981, #059669)' }}>
                    Proceed to Checkout <i className="fas fa-arrow-right" style={{ marginLeft: '0.5rem' }}></i>
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <style>
        {`
          @media (max-width: 900px) {
            .seat-container {
              flex-direction: column;
            }
            .sidebar-info {
              width: 100% !important;
              position: static !important;
            }
          }
        `}
      </style>
    </div>
  );
};

export default SeatSelectionPage;